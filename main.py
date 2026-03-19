import streamlit as st
import os

from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("G_API_KEY"))

model = genai.GenerativeModel('gemini-2.5-flash')

def get_gemini_response(input, image, prompt):
    response = model.generate_content([input, image[0], prompt])
    return response.text

def input_image_details(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]

        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")
    
st.set_page_config(page_title="Whats For Dinner", page_icon="🥪")
st.header('Whats For Dinner 🥪')

uploaded_file = st.file_uploader("Click an image of your fridge and upload it here as either jpg,jpeg or png", type=["jpg", 'jpeg', 'png'])
image = ""
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

submit = st.button("Scan the Food(s)")

input_prompt = """
You have to identify different types of food in images,please.
The system should accurately detect and label various foods displayed in the image,indivudually, can you also please return the names of 
the foods detected in a python list. Thank You! 
"""

if submit:
    image_data = input_image_details(uploaded_file)
    response = get_gemini_response(input_prompt, image_data, input)
    items = list(response)

with st.sidebar:
    st.header("Settings")
    if st.button('Clear App Cache'):
      
        st.cache_data.clear()
      
        if 'last_recipe' in st.session_state:
            del st.session_state['last_recipe']
        st.success("Cache Cleared! Ready for a fresh start.")


@st.cache_data(show_spinner=False)
def generate_recommendations(input_text):
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.7
        )
        prompt = f"Given the ingredients: {items}, suggest five easy-to-cook step-by-step recipes."
        response = llm.invoke(prompt)
        return response.content
    
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
        
            placeholder = st.empty()
            for seconds_left in range(60, 0, -1):
                placeholder.error(f"⏳ Quota limit reached. Please wait {seconds_left}s before retrying...")
                time.sleep(1)
            placeholder.success("🔄 You can try again now!")
            return None
        else:
            st.error(f"An error occurred: {error_msg}")
            return None

with st.spinner('Tasty Food Is A Moment Away...'):
            recipe = generate_recommendations(items)
            st.session_state['last_recipe'] = recipe

if 'last_recipe' in st.session_state:
    st.markdown("---")
    st.markdown("### 📝 Your Custom Recipe")





