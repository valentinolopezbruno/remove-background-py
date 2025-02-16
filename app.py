import os
from PIL import Image
import streamlit as st
from rembg import remove
from pathlib import Path
import zipfile
import io

def save_uploaded_file(uploaded_file, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def process_images(images, background_image=None, background_color=None):
    results = []
    
    # Si hay imagen de fondo, prepararla
    if background_image:
        bg_img = Image.open(background_image)
    
    for img in images:
        # Guardar imagen original
        input_path = save_uploaded_file(img, "uploads/originals")
        
        # Procesar imagen
        input_image = Image.open(input_path)
        output_image = remove(input_image)
        
        if background_image:
            # Redimensionar el fondo al tamaño de la imagen actual
            resized_bg = bg_img.resize(output_image.size)
            # Convertir ambas imágenes a RGBA
            resized_bg = resized_bg.convert('RGBA')
            output_image = output_image.convert('RGBA')
            # Combinar imágenes
            resized_bg.paste(output_image, (0, 0), output_image)
            output_image = resized_bg
        elif background_color:
            # Usar color sólido como fondo
            bg = Image.new("RGBA", output_image.size, background_color)
            output_image = Image.alpha_composite(bg, output_image.convert('RGBA'))
        
        # Guardar resultado
        output_path = f"uploads/processed/{img.name}"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        output_image.save(output_path, "PNG")
        results.append((input_path, output_path))
    
    return results

def main():
    st.set_page_config(
        page_title="AI Background Remover",
        page_icon="🖼️",
        layout="wide"
    )
    
    st.title("🖼️ Procesador de Imágenes con IA")
    st.write("Sube hasta 10 imágenes para remover el fondo y agregar un fondo de galaxia")
    
    # Contenedor para opciones de fondo
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
    
    # Subida múltiple de archivos
    uploaded_files = st.file_uploader(
        "Sube tus imágenes (máximo 10)", 
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if len(uploaded_files) > 10:
            st.error("⚠️ Por favor, selecciona máximo 10 imágenes")
            return
            
        if st.button("Procesar Imágenes"):
            with st.spinner("Procesando imágenes..."):
                results = process_images(uploaded_files, background_image, background_color)
                
                # Mostrar resultados en una cuadrícula
                cols_per_row = 2
                for i in range(0, len(results), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j in range(cols_per_row):
                        if i + j < len(results):
                            with cols[j]:
                                st.subheader(f"Imagen {i + j + 1}")
                                original, processed = results[i + j]
                                st.image(original, caption="Original", use_column_width=True)
                                st.image(processed, caption="Procesada", use_column_width=True)
                
                # Crear un ZIP con los resultados
                if len(results) > 0:
                    zip_path = "uploads/processed_images.zip"
                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                        for _, processed in results:
                            zipf.write(processed)
                    
                    with open(zip_path, 'rb') as f:
                        st.download_button(
                            "⬇️ Descargar todas las imágenes procesadas",
                            f,
                            file_name="imagenes_procesadas.zip",
                            mime="application/zip",
                            key="download_button"
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
        
        
    