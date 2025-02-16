import os
from PIL import Image
import streamlit as st
from rembg import remove
from pathlib import Path

def save_uploaded_file(uploaded_file):
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    file_path = os.path.join(upload_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def overlay_images(foreground_path, background_path="./banners/banner-galaxia.jpeg"):
    foreground = Image.open(foreground_path)
    background = Image.open(background_path)
    
    background = background.resize(foreground.size)
    
    if foreground.mode != 'RGBA':
        foreground = foreground.convert('RGBA')
    if background.mode != 'RGBA':
        background = background.convert('RGBA')
    
    combined = Image.alpha_composite(background, foreground)
    
    output_path = foreground_path.replace('_rmbg.', '_combined.')
    combined.save(output_path, "PNG")
    return output_path

def remove_background(input_path):
    input_image = save_uploaded_file(input_path)
    output_path = input_image.replace('.', '_rmbg.')
    
    try:
        img = Image.open(input_image)
        output = remove(img)
        output.save(output_path, "PNG")
        
        combined_path = overlay_images(output_path)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.header("Original")
            st.image(input_image, caption="Original Img")
            with open(input_image, "rb") as img_file:
                st.download_button(label="Download Original", data=img_file, file_name="original_image.png", mime="image/png")
        
        with col2:
            st.header("Sin Fondo")
            st.image(output_path, caption="Sin Fondo")
            with open(output_path, "rb") as img_file:
                st.download_button(label="Download Sin Fondo", data=img_file, file_name="no_background.png", mime="image/png")
        
        with col3:
            st.header("Con Galaxia")
            st.image(combined_path, caption="Con Fondo de Galaxia")
            with open(combined_path, "rb") as img_file:
                st.download_button(label="Download Final", data=img_file, file_name="with_galaxy.png", mime="image/png")
        
        st.success("¡Imágenes procesadas exitosamente!")
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")

def process_folder(input_folder, output_folder="processed_images"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    valid_extensions = {'.jpg', '.jpeg', '.png'}
    image_files = [f for f in os.listdir(input_folder) 
                   if Path(f).suffix.lower() in valid_extensions]
    
    progress_container = st.empty()
    
    st.write(f"Encontradas {len(image_files)} imágenes para procesar")
    
    for i, filename in enumerate(image_files):
        progress = (i + 1) / len(image_files)
        progress_container.progress(progress)
        
        try:
            input_path = os.path.join(input_folder, filename)
            base_name = Path(filename).stem
            final_path = os.path.join(output_folder, f"{base_name}_final.png")
            
            img = Image.open(input_path)
            
            output_no_bg = remove(img)
            
            background = Image.open("./banners/banner-galaxia.jpeg")
            background = background.resize(output_no_bg.size)
            
            if output_no_bg.mode != 'RGBA':
                output_no_bg = output_no_bg.convert('RGBA')
            if background.mode != 'RGBA':
                background = background.convert('RGBA')
            
            combined = Image.alpha_composite(background, output_no_bg)
            combined.save(final_path, "PNG")
            
            st.write(f"✅ Procesada: {filename}")
            
        except Exception as e:
            st.write(f"❌ Error procesando {filename}: {str(e)}")
    
    progress_container.empty()
    st.success("¡Procesamiento por lotes completado!")

def main():
    st.title("Procesador de Imágenes con IA")
    
    tab1, tab2 = st.tabs(["Procesar Imagen Individual", "Procesar Carpeta"])
    
    with tab1:
        st.header("Subir Imagen Individual")
        uploaded_file = st.file_uploader("Subir una imagen", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            remove_background(uploaded_file)
    
    with tab2:
        st.header("Procesar Carpeta Completa")
        input_folder = st.text_input("Ruta de la carpeta con imágenes:", "./images")
        
        if st.button("Procesar Carpeta"):
            if os.path.exists(input_folder):
                process_folder(input_folder)
            else:
                st.error(f"La carpeta {input_folder} no existe")

if __name__ == "__main__":
    main()
        
        
    