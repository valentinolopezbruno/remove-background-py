import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
from PIL import Image, ImageTk
import os
from rembg import remove
import threading
from pathlib import Path
import zipfile
import shutil
import sys

class BackgroundRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Removedor de Fondos")
        self.root.geometry("1200x800")
        
        # Agregar ícono a la ventana
        try:
            if getattr(sys, 'frozen', False):
                # Si es un ejecutable
                application_path = sys._MEIPASS
            else:
                # Si es script Python
                application_path = os.path.dirname(os.path.abspath(__file__))
                
            icon_path = os.path.join(application_path, "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        # Variables
        self.selected_files = []
        self.background_image = None
        self.background_color = None
        self.processed_images = []  # Lista para guardar las rutas de las imágenes procesadas
        
        self.setup_ui()
        
    def setup_ui(self):
        # Panel principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Opciones de fondo
        bg_frame = ttk.LabelFrame(main_frame, text="Opciones de fondo", padding="5")
        bg_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.bg_var = tk.StringVar(value="transparent")
        ttk.Radiobutton(bg_frame, text="Transparente", variable=self.bg_var, 
                       value="transparent").grid(row=0, column=0, padx=5)
        ttk.Radiobutton(bg_frame, text="Color sólido", variable=self.bg_var,
                       value="color").grid(row=0, column=1, padx=5)
        ttk.Radiobutton(bg_frame, text="Imagen", variable=self.bg_var,
                       value="image").grid(row=0, column=2, padx=5)
        
        ttk.Button(bg_frame, text="Seleccionar color", 
                  command=self.choose_color).grid(row=0, column=3, padx=5)
        ttk.Button(bg_frame, text="Seleccionar imagen", 
                  command=self.choose_bg_image).grid(row=0, column=4, padx=5)
        
        # Botones principales
        ttk.Button(main_frame, text="Seleccionar imágenes", 
                  command=self.select_files).grid(row=1, column=0, pady=5)
        ttk.Button(main_frame, text="Procesar imágenes", 
                  command=self.process_images).grid(row=1, column=1, pady=5)
        
        # Lista de archivos
        self.file_list = tk.Listbox(main_frame, height=5)
        self.file_list.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Área de previsualización
        preview_frame = ttk.Frame(main_frame)
        preview_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.preview_original = ttk.Label(preview_frame, text="Original")
        self.preview_original.grid(row=0, column=0, padx=5)
        
        self.preview_processed = ttk.Label(preview_frame, text="Procesado")
        self.preview_processed.grid(row=0, column=1, padx=5)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(main_frame, length=300, mode='determinate')
        self.progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Agregar botón de descarga ZIP (inicialmente deshabilitado)
        self.download_button = ttk.Button(
            main_frame, 
            text="Descargar imágenes procesadas (ZIP)", 
            command=self.save_zip,
            state='disabled'
        )
        self.download_button.grid(row=5, column=0, columnspan=2, pady=5)
    
    def choose_color(self):
        color = colorchooser.askcolor(title="Seleccionar color de fondo")
        if color[1]:
            self.background_color = color[1]
            self.bg_var.set("color")
    
    def choose_bg_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            self.background_image = file_path
            self.bg_var.set("image")
    
    def select_files(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg")]
        )
        self.selected_files = list(files)
        self.file_list.delete(0, tk.END)
        for file in self.selected_files:
            self.file_list.insert(tk.END, Path(file).name)
    
    def save_zip(self):
        if not self.processed_images:
            messagebox.showwarning("Advertencia", "No hay imágenes procesadas para descargar")
            return
            
        # Pedir al usuario donde guardar el ZIP
        zip_path = filedialog.asksaveasfilename(
            defaultextension=".zip",
            filetypes=[("Archivo ZIP", "*.zip")],
            title="Guardar imágenes procesadas"
        )
        
        if zip_path:
            try:
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for img_path in self.processed_images:
                        # Agregar cada imagen al ZIP con solo el nombre del archivo
                        zipf.write(img_path, os.path.basename(img_path))
                
                messagebox.showinfo("Éxito", f"Imágenes guardadas en:\n{zip_path}")
                
                # Preguntar si desea abrir la carpeta contenedora
                if messagebox.askyesno("Abrir carpeta", "¿Deseas abrir la carpeta contenedora?"):
                    if sys.platform == "win32":
                        os.startfile(os.path.dirname(zip_path))
                    elif sys.platform == "darwin":  # macOS
                        os.system(f'open "{os.path.dirname(zip_path)}"')
                    else:  # linux
                        os.system(f'xdg-open "{os.path.dirname(zip_path)}"')
            
            except Exception as e:
                messagebox.showerror("Error", f"Error al crear el ZIP: {str(e)}")
    
    def process_images(self):
        if not self.selected_files:
            messagebox.showwarning("Advertencia", "No hay imágenes seleccionadas")
            return
            
        def process():
            output_dir = "processed_images"
            os.makedirs(output_dir, exist_ok=True)
            
            # Limpiar lista de imágenes procesadas
            self.processed_images = []
            
            total = len(self.selected_files)
            for i, file_path in enumerate(self.selected_files):
                # Actualizar progreso
                progress = (i + 1) / total * 100
                self.progress['value'] = progress
                self.root.update_idletasks()
                
                try:
                    # Procesar imagen
                    input_image = Image.open(file_path)
                    output_image = remove(input_image)
                    
                    if self.bg_var.get() == "color" and self.background_color:
                        bg = Image.new("RGBA", output_image.size, self.background_color)
                        output_image = Image.alpha_composite(bg, output_image.convert('RGBA'))
                    elif self.bg_var.get() == "image" and self.background_image:
                        bg = Image.open(self.background_image)
                        bg = bg.resize(output_image.size)
                        bg.paste(output_image, (0, 0), output_image)
                        output_image = bg
                    
                    # Guardar resultado
                    output_path = os.path.join(output_dir, f"processed_{Path(file_path).name}")
                    output_image.save(output_path, "PNG")
                    self.processed_images.append(output_path)
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Error procesando {Path(file_path).name}: {str(e)}")
            
            self.progress['value'] = 0
            
            # Habilitar botón de descarga
            self.download_button['state'] = 'normal'
            
            messagebox.showinfo("Éxito", f"Se procesaron {len(self.processed_images)} imágenes")
        
        # Ejecutar en un hilo separado
        threading.Thread(target=process, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = BackgroundRemoverApp(root)
    root.mainloop() 