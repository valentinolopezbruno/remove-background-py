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

def remove_background(input_path):
    input_image = save_uploaded_file(input_path)
    output_path = input_image.replace('.', '_rmbg.')
    
    try:
        # Abrir la imagen y remover el fondo
        img = Image.open(input_image)
        output = remove(img)
        output.save(output_path, "PNG")
        
        # Mostrar las imágenes
        col1, col2 = st.columns(2)
        with col1:
            st.header("Original Image")
            st.image(input_image, caption="Original Img")
            with open(input_image, "rb") as img_file:
                st.download_button(label="Download original Image", data=img_file, file_name="original_image.png", mime="image/png")
        
        with col2:
            st.header("Background Removed Image")
            st.image(output_path, caption="Background Removed Img")
            with open(output_path, "rb") as img_file:
                st.download_button(label="Download Background Removed Image", data=img_file, file_name="background_removed_image.png", mime="image/png")
        
        st.success("Background removed successfully")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def main():
    st.title("Background Removal App")
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        remove_background(uploaded_file)

if __name__ == "__main__":
    main()
        
        
    