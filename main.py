import streamlit as st
import os
import time
from PIL import Image
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("G_API_KEY")
genai.configure(api_key=api_key)


os.environ["GOOGLE_API_KEY"] = api_key

st.set_page_config(page_title="What's For Dinner?", page_icon="🥪", layout="wide")
st.markdown("<h1 style='text-align: center; margin-top: -50px;'>What's For Dinner? 🥪</h1>", unsafe_allow_html=True)

st.write()
st.write()
st.write()
st.write()
st.write()
st.write()
st.write()
st.write()
st.write()
st.write()

st.divider()


if 'detected_items' not in st.session_state:
    st.session_state['detected_items'] = ""
if 'last_recipe' not in st.session_state:
    st.session_state['last_recipe'] = None


def get_food_list_from_image(image_data, prompt):
   
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content([prompt, image_data[0]])
    return response.text

def input_image_details(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        return [{"mime_type": uploaded_file.type, "data": bytes_data}]
    raise FileNotFoundError("No file uploaded")

@st.cache_data(show_spinner=False)
def generate_recommendations(ingredients_text):
   
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
        prompt = f"Given the ingredients: {ingredients_text}, suggest five easy-to-cook step-by-step recipes. Format them with bold titles and clear instructions."
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None


with st.sidebar:
    st.header("Settings")
    if st.button('Clear App Cache & Reset'):
        st.cache_data.clear()
        st.session_state['detected_items'] = ""
        st.session_state['last_recipe'] = None
        st.success("App Reset & Cache Cleared!")


col1, col2 = st.columns([0.45, 0.45]) 

with col1:
    st.subheader(" Upload a photo of your fridge :")
    uploaded_file = st.file_uploader(" ", type=["jpg", 'jpeg', 'png'])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Your Fridge ", use_column_width=True)
        
        if st.button("Scan Fridge Content"):
            with st.spinner('Scanning your pantry...'):
                input_prompt = "Can you please Identify the food items. Return only a comma-separated list of names. Thank You!"
                image_data = input_image_details(uploaded_file)
                
                st.session_state['detected_items'] = get_food_list_from_image(image_data, input_prompt)
                

        
with col2:
    st.subheader("Your ingredients :")
    
    user_ingredients = st.text_area(
        "Edit detected ingredients or add pantry staples :",
        value=st.session_state['detected_items'],
        height=150
    )
    
    if st.button("Get Recipe Recommendations"):
        if not user_ingredients.strip():
            st.warning("Please scan an image or enter ingredients first!")
        else:
            with st.spinner('Tasty food is a moment away...'):
                recipe_output = generate_recommendations(user_ingredients)
                st.session_state['last_recipe'] = recipe_output


if st.session_state['last_recipe']:
    st.markdown("---")
    st.markdown("### 👨‍🍳 Your Recipes :")
    st.markdown(st.session_state['last_recipe'])
