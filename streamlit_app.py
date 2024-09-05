import pandas as pd
import streamlit as st
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
import json

st.set_page_config(layout="wide")

load_dotenv()


def initialise_model(model_name="gemini-1.5-flash"):
    model = genai.GenerativeModel(model_name)
    return model


def get_image_bytes(uploaded_image):
    if uploaded_image is not None:
        image_bytes = uploaded_image.getvalue()

        image_info = [{
            'mime_type': uploaded_image.type,
            "data": image_bytes
        }]
        return image_info
    else:
        raise FileNotFoundError("No image uploaded")


def get_response(model, model_behaviour, image, prompt):
    response = model.generate_content([model_behaviour, image[0], prompt])
    return response.text


st.header("Invoice Extractor")
# Read teh prompt in text box
prompt = "Generate a table from the invoice image"
# interface to upload image
with st.sidebar:
    uploaded_image = st.file_uploader("Choose an image", type=["jpg", "png", "jpeg"])

api_key = st.text_input("Enter your API key", type="password")

genai.configure(api_key=api_key)

model = initialise_model("gemini-1.5-flash")

col1, col2 = st.columns(2)

with col1:
    if uploaded_image is not None:
        image = Image.open(uploaded_image)

        st.image(image, caption="Uploaded Image", use_column_width=False, width=300)


    submit = st.button("Submit")

model_behaviour = """
You are an export who understands invoice overall structures and has deep knowledge on it.
We will upload the invoice image and you have to answer the questions based on the information in that is in the invoice image.
You will only provide the answers in table format. Text based answers are not acceptable.
The table should have the following columns:
Item
Price
Quantity

Your output should be in JSON format and should only be called "table",  Format the JSON properly as it should be in a dictionary format.
remove the "json" key from the output. Remove any other keys from the output.
Make all your outputs strictly consistent!
"""

with col2:
    if submit:
        image_info = get_image_bytes(uploaded_image)
        response = get_response(model, model_behaviour, image_info, prompt)
        response_json = json.loads(response)
        df = pd.DataFrame(response_json["table"])
        st.dataframe(df)
        csv_file = "invoice.xlsx"
        df.to_excel(csv_file, index=False)

        st.download_button(label="Download Excel"
                                 "", data=open(csv_file, "rb"), file_name=csv_file, mime='text/csv')
        ////test
