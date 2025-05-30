from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import google.generativeai as genai

# Load environment variables and configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Prepare image bytes correctly before anything else
def input_image_setup(image_bytes, mime_type):
    if image_bytes and len(image_bytes) > 0:
        return {
            "inline_data": {
                "mime_type": mime_type,
                "data": image_bytes
            }
        }
    else:
        raise ValueError("Uploaded image is empty. Cannot process.")

# Generate content using Gemini model
def get_gemini_response(prompt_text, image_part):
    model = genai.GenerativeModel('gemini-1.5-flash')
    try:
        response = model.generate_content([
            {"text": prompt_text},
            image_part
        ])
        return response.text
    except Exception as e:
        st.exception(e)
        raise RuntimeError("Model inference failed.") from e

# Streamlit UI
st.set_page_config(page_title="Gemini Flash Animal Information Extractor")
st.title("Gemini App Animal Image Analyzer")

user_input = st.text_input("Enter your question about the image:", key="input")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

image_bytes = None
image_display = None

# Read image once (early!) and cache both bytes and display image
if uploaded_file is not None:
    image_bytes = uploaded_file.read()
    if image_bytes:
        image_display = Image.open(uploaded_file)
        st.image(image_display, caption="Uploaded Image", use_container_width=True)

system_prompt = """
You are an expert animal biologist and zoologist. You will receive animal images as input and your task is to answer the questions 
based on the input image.
"""

if st.button("Tell me about the animal displayed in the image"):
    if uploaded_file and user_input and image_bytes:
        try:
            full_prompt = f"{system_prompt.strip()}\n\nQuestion: {user_input.strip()}"
            image_part = input_image_setup(image_bytes, uploaded_file.type)
            response_text = get_gemini_response(full_prompt, image_part)
            st.subheader("Response:")
            st.write(response_text)
        except Exception as e:
            st.error(str(e))
    else:
        st.warning("Please upload an image and enter a valid question.")
