import os
from PIL import Image
import streamlit as st
from rembg import remove
import time
import zipfile
import io

def save_uploaded_file(uploaded_file, directory="uploads"):
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def process_single_image(image, background_image=None, background_color=None):
    # Guardar imagen original
    input_path = save_uploaded_file(image)
    
    # Remover fondo
    with st.spinner("Removiendo fondo..."):
        input_image = Image.open(input_path)
        output_image = remove(input_image)
    
    # Aplicar nuevo fondo
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
    
    # Guardar resultado
    output_path = f"uploads/processed_{image.name}"
    final_image.save(output_path, "PNG")
    return input_path, output_path

def process_multiple_images(images, background_image=None, background_color=None):
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, img in enumerate(images):
        # Actualizar progreso
        progress = (idx + 1) / len(images)
        progress_bar.progress(progress)
        status_text.text(f"Procesando imagen {idx + 1} de {len(images)}")
        
        # Procesar imagen
        try:
            input_path, output_path = process_single_image(img, background_image, background_color)
            results.append((input_path, output_path))
        except Exception as e:
            st.error(f"Error procesando {img.name}: {str(e)}")
    
    progress_bar.empty()
    status_text.empty()
    return results

def create_download_zip(paths):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for _, processed_path in paths:
            zip_file.write(processed_path, os.path.basename(processed_path))
    return zip_buffer

def main():
    st.set_page_config(page_title="AI Background Processor", page_icon="🖼️", layout="wide")
    
    st.title("🖼️ Procesador de Imágenes con IA")
    
    # Selector de modo
    mode = st.radio(
        "Selecciona el modo",
        ["Procesar una imagen", "Procesar múltiples imágenes"]
    )
    
    # Opciones de fondo
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
    
    # Procesamiento según modo
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
                
                # Mostrar resultados
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Imagen Original")
                    st.image(input_path)
                with col2:
                    st.subheader("Resultado")
                    st.image(output_path)
                    
                    # Botón de descarga
                    with open(output_path, "rb") as f:
                        st.download_button(
                            "⬇️ Descargar imagen procesada",
                            f,
                            file_name=f"processed_{uploaded_file.name}",
                            mime="image/png"
                        )
                
                end_time = time.time()
                st.success(f"✅ Imagen procesada en {end_time - start_time:.2f} segundos")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    else:  # Procesar múltiples imágenes
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
                
                results = process_multiple_images(
                    uploaded_files,
                    background_image,
                    background_color
                )
                
                if results:
                    # Mostrar resultados en grid
                    st.subheader("Resultados")
                    cols = st.columns(3)
                    for idx, (input_path, output_path) in enumerate(results):
                        with cols[idx % 3]:
                            st.image(output_path, caption=f"Imagen {idx + 1}")
                    
                    # Botón de descarga ZIP
                    zip_buffer = create_download_zip(results)
                    st.download_button(
                        "⬇️ Descargar todas las imágenes",
                        zip_buffer.getvalue(),
                        file_name="imagenes_procesadas.zip",
                        mime="application/zip"
                    )
                    
                    end_time = time.time()
                    st.success(f"✅ {len(results)} imágenes procesadas en {end_time - start_time:.2f} segundos")
    
    # Información
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
        
        
    