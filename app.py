import os
from PIL import Image
import streamlit as st
from rembg import remove
from pathlib import Path
import zipfile
import io

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

def create_zip_of_images(image_paths, zip_name="processed_images.zip"):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for path in image_paths:
            zip_file.write(path, os.path.basename(path))
    return zip_buffer

def process_images(uploaded_files):
    processed_paths = []
    
    for uploaded_file in uploaded_files:
        try:
            # Guardar y procesar imagen
            input_image = save_uploaded_file(uploaded_file)
            output_path = input_image.replace('.', '_rmbg.')
            
            # Remover fondo
            img = Image.open(input_image)
            output = remove(img)
            output.save(output_path, "PNG")
            
            # Agregar fondo de galaxia
            final_path = overlay_images(output_path)
            processed_paths.append(final_path)
            
        except Exception as e:
            st.error(f"Error procesando {uploaded_file.name}: {str(e)}")
            continue
    
    return processed_paths

def main():
    st.set_page_config(
        page_title="AI Background Remover",
        page_icon="🖼️",
        layout="wide"
    )
    
    st.title("🖼️ Procesador de Imágenes con IA")
    st.write("Sube hasta 10 imágenes para remover el fondo y agregar un fondo de galaxia")
    
    uploaded_files = st.file_uploader(
        "Arrastra o selecciona tus imágenes (máximo 10)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if len(uploaded_files) > 10:
            st.error("⚠️ Por favor, selecciona máximo 10 imágenes")
            return
        
        with st.spinner("Procesando imágenes..."):
            processed_paths = process_images(uploaded_files)
        
        if processed_paths:
            st.success(f"✅ {len(processed_paths)} imágenes procesadas exitosamente!")
            
            # Mostrar imágenes procesadas
            cols = st.columns(min(3, len(processed_paths)))
            for idx, path in enumerate(processed_paths):
                with cols[idx % 3]:
                    st.image(path, caption=f"Imagen {idx + 1}")
                    with open(path, "rb") as img_file:
                        st.download_button(
                            label=f"⬇️ Descargar imagen {idx + 1}",
                            data=img_file,
                            file_name=os.path.basename(path),
                            mime="image/png"
                        )
            
            # Botón para descargar todas las imágenes
            if len(processed_paths) > 1:
                zip_buffer = create_zip_of_images(processed_paths)
                st.download_button(
                    label="⬇️ Descargar todas las imágenes",
                    data=zip_buffer.getvalue(),
                    file_name="imagenes_procesadas.zip",
                    mime="application/zip"
                )
    
    # Información adicional
    with st.expander("ℹ️ Información"):
        st.markdown("""
        ### Cómo usar:
        1. Arrastra o selecciona hasta 10 imágenes
        2. Espera a que se procesen
        3. Descarga las imágenes individualmente o todas juntas
        
        ### Formatos soportados:
        - JPG/JPEG
        - PNG
        
        ### Limitaciones:
        - Máximo 10 imágenes por vez
        - Tamaño máximo por imagen: 5MB
        """)

if __name__ == "__main__":
    main()
        
        
    