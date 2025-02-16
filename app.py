import os
from PIL import Image
import streamlit as st
from rembg import remove

def save_uploaded_file(uploaded_file):
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    file_path = os.path.join(upload_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def overlay_images(foreground_path, background_path="./banners/banner-galaxia.jpeg"):
    # Abrir las imágenes
    foreground = Image.open(foreground_path)
    background = Image.open(background_path)
    
    # Redimensionar el fondo al tamaño del primer plano si es necesario
    background = background.resize(foreground.size)
    
    # Asegurar que las imágenes están en modo RGBA
    if foreground.mode != 'RGBA':
        foreground = foreground.convert('RGBA')
    if background.mode != 'RGBA':
        background = background.convert('RGBA')
    
    # Combinar las imágenes
    combined = Image.alpha_composite(background, foreground)
    
    # Guardar la imagen combinada
    output_path = foreground_path.replace('_rmbg.', '_combined.')
    combined.save(output_path, "PNG")
    return output_path

def remove_background(input_path):
    input_image = save_uploaded_file(input_path)
    output_path = input_image.replace('.', '_rmbg.')
    
    try:
        # Abrir la imagen y remover el fondo
        img = Image.open(input_image)
        output = remove(img)
        output.save(output_path, "PNG")
        
        # Combinar con el fondo de galaxia
        combined_path = overlay_images(output_path)
        
        # Mostrar las imágenes
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

def main():
    st.title("Background Removal App")
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        remove_background(uploaded_file)

if __name__ == "__main__":
    main()
        
        
    