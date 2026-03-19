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

st.set_page_config(page_title="Whats For Dinner", page_icon="🥪")
st.title('Whats For Dinner 🥪 || Recipe Recommender')


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
        prompt = f"Given the ingredients: {ingredients_text}, suggest five easy-to-cook step-by-step recipes."
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        st.error(f"Error generating recipes: {str(e)}")
        return None


with st.sidebar:
    st.header("Settings")
    if st.button('Clear App Cache'):
        st.cache_data.clear()
        if 'last_recipe' in st.session_state:
            del st.session_state['last_recipe']
        st.success("Cache Cleared!")

uploaded_file = st.file_uploader("Upload an image of your fridge", type=["jpg", 'jpeg', 'png'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Your Fridge", use_column_width=True)

submit = st.button("Scan Fridge & Get Recipes")


input_prompt = """
Please Identify the food items in this image. 
Return only a comma-separated list of the food names.Thank You!
"""

if submit:
    if uploaded_file is not None:
        with st.spinner('Scanning your fridge...'):
          
            image_data = input_image_details(uploaded_file)
            detected_items = get_food_list_from_image(image_data, input_prompt)
            st.info(f"**Detected Ingredients:** {detected_items}")
            
        with st.spinner('Cooking up some ideas...'):
           
            recipe = generate_recommendations(detected_items)
            st.session_state['last_recipe'] = recipe
    else:
        st.warning("Please upload an image first!")


if 'last_recipe' in st.session_state:
    st.markdown("---")
    st.markdown("### 📝 Your Custom Recipes")
    st.write(st.session_state['last_recipe'])
