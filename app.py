import os
from PIL import Image
import streamlit as st
from rembg import remove
import time
import zipfile
import io
import shutil

def cleanup_files(paths):
    """Elimina los archivos y directorios temporales"""
    for path in paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            st.warning(f"No se pudo eliminar {path}: {e}")
    

    directories = ['uploads']
    for directory in directories:
        if os.path.exists(directory):
            try:
                shutil.rmtree(directory)
            except Exception as e:
                st.warning(f"No se pudo eliminar el directorio {directory}: {e}")

def save_uploaded_file(uploaded_file, directory="uploads"):
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def process_single_image(image, background_image=None, background_color=None):

    input_path = save_uploaded_file(image)
    

    with st.spinner("Removiendo fondo..."):
        input_image = Image.open(input_path)
        output_image = remove(input_image)
    
    
    with st.spinner("Aplicando nuevo fondo..."):
        if background_image:
            bg_img = Image.open(background_image)
            bg_img = bg_img.resize(output_image.size)
            bg_img = bg_img.convert('RGBA')
            output_image = output_image.convert('RGBA')
            bg_img.paste(output_image, (0, 0), output_image)
            final_image = bg_img
        elif background_color:
            bg = Image.new("RGBA", output_image.size, background_color)
            final_image = Image.alpha_composite(bg, output_image.convert('RGBA'))
        else:
            final_image = output_image
    
 
    output_path = f"uploads/processed_{image.name}"
    final_image.save(output_path, "PNG")
    return input_path, output_path

def process_multiple_images(images, background_image=None, background_color=None):
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, img in enumerate(images):
      
        progress = (idx + 1) / len(images)
        progress_bar.progress(progress)
        status_text.text(f"Procesando imagen {idx + 1} de {len(images)}")
  
        try:
            input_path, output_path = process_single_image(img, background_image, background_color)
            results.append((input_path, output_path))
        except Exception as e:
            st.error(f"Error procesando {img.name}: {str(e)}")
    
    progress_bar.empty()
    status_text.empty()
    return results

def create_download_zip(paths):
    """Crea un ZIP en memoria con las imágenes procesadas"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for _, processed_path in paths:
            zip_file.write(processed_path, os.path.basename(processed_path))
    return zip_buffer

def main():
    st.set_page_config(page_title="AI Background Processor", page_icon="🖼️", layout="wide")
    
    st.title("🖼️ Procesador de Imágenes con IA")

    mode = st.radio(
        "Selecciona el modo",
        ["Procesar una imagen", "Procesar múltiples imágenes"]
    )

    with st.expander("Opciones de fondo", expanded=True):
        background_option = st.radio(
            "Selecciona el tipo de fondo",
            ["Transparente", "Color sólido", "Imagen personalizada"]
        )
        
        background_color = None
        background_image = None
        
        if background_option == "Color sólido":
            background_color = st.color_picker("Selecciona el color de fondo", "#FFFFFF")
        elif background_option == "Imagen personalizada":
            background_image = st.file_uploader(
                "Sube una imagen de fondo",
                type=["png", "jpg", "jpeg"]
            )
    
  
    if mode == "Procesar una imagen":
        uploaded_file = st.file_uploader(
            "Sube tu imagen",
            type=["png", "jpg", "jpeg"]
        )
        
        if uploaded_file and st.button("Procesar imagen"):
            start_time = time.time()
            
            try:
                input_path, output_path = process_single_image(
                    uploaded_file,
                    background_image,
                    background_color
                )
                
             
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Imagen Original")
                    st.image(input_path)
                with col2:
                    st.subheader("Resultado")
                    st.image(output_path)
                   
                    with open(output_path, "rb") as f:
                        file_data = f.read()  
                        
                  
                    cleanup_files([input_path, output_path])
                    
                  
                    st.download_button(
                        "⬇️ Descargar imagen procesada",
                        file_data,
                        file_name=f"processed_{uploaded_file.name}",
                        mime="image/png"
                    )
                
                end_time = time.time()
                st.success(f"✅ Imagen procesada en {end_time - start_time:.2f} segundos")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
            
                cleanup_files([input_path, output_path])
    
    else:  
        uploaded_files = st.file_uploader(
            "Sube tus imágenes (máximo 10)",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            if len(uploaded_files) > 10:
                st.error("⚠️ Por favor, selecciona máximo 10 imágenes")
                return
            
            if st.button("Procesar imágenes"):
                start_time = time.time()
                all_paths = [] 
                
                try:
                    results = process_multiple_images(
                        uploaded_files,
                        background_image,
                        background_color
                    )
                    
                    if results:
                   
                        st.subheader("Resultados")
                        cols = st.columns(3)
                        for idx, (input_path, output_path) in enumerate(results):
                            all_paths.extend([input_path, output_path])
                            with cols[idx % 3]:
                                st.image(output_path, caption=f"Imagen {idx + 1}")
                        
                      
                        zip_buffer = create_download_zip(results)
                        zip_data = zip_buffer.getvalue()
                        
                     
                        cleanup_files(all_paths)
                        
                        st.download_button(
                            "⬇️ Descargar todas las imágenes",
                            zip_data,
                            file_name="imagenes_procesadas.zip",
                            mime="application/zip"
                        )
                        
                        end_time = time.time()
                        st.success(f"✅ {len(results)} imágenes procesadas en {end_time - start_time:.2f} segundos")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    cleanup_files(all_paths)
    
    with st.expander("ℹ️ Información"):
        st.markdown("""
        ### Instrucciones:
        1. Selecciona el modo de procesamiento
        2. Elige el tipo de fondo que deseas
        3. Sube tu(s) imagen(es)
        4. Espera el procesamiento
        5. Descarga los resultados
        
        ### Limitaciones:
        - Máximo 10 imágenes simultáneas
        - Formatos soportados: JPG, JPEG, PNG
        - Tamaño máximo por imagen: 5MB
        """)

if __name__ == "__main__":
    main()
        
        
    