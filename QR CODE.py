import streamlit as st
import qrcode
from PIL import Image
import pandas as pd
from io import BytesIO
import json
import os
import re

st.set_page_config(page_title="QR code Generator", page_icon="", layout="wide")
st.markdown("""
            <style>
                .block-container {
                        padding-top: 0rem;
                        padding-bottom: 2rem;   # this is to remove that blank space on top of the title 
                        padding-left: 5rem;
                        padding-right: 5rem;
                    }
            </style>
            """, unsafe_allow_html=True)

hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True)


st.markdown(
        """
        <style>
        .center-title {
            font-size: 100px;
            font-weight: bold;
            text-align: center;
            color: #31333F;
        }
        </style>
        <h1 class="center-title">✨ QR code Generator ✨</h1>
        """, 
        unsafe_allow_html=True
    )

#----------
QR_FOLDER = "qr_codes"
os.makedirs(QR_FOLDER, exist_ok=True)

def sanitize_filename(s):
    return re.sub(r'[^\w\-]', '_', s)

def generate_qr_code(data, filename):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    img_path = os.path.join(QR_FOLDER, filename)
    img.save(img_path)
    return img_path

def display_data_as_table(data_string):
    try:
        data_dict = json.loads(data_string)
        df = pd.DataFrame(data_dict)
        st.dataframe(df)
    except json.JSONDecodeError:
        data_list = data_string.split(", ")
        data_dict = {}
        for item in data_list:
            if ":" in item:
                key, value = item.split(": ")
                data_dict[key.strip()] = [value.strip()]
        df = pd.DataFrame(data_dict)
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error displaying data: {e}")
        st.write(f"Raw data string: {data_string}")

if 'qr_image_path' not in st.session_state:
    st.session_state['qr_image_path'] = None
if 'qr_data_string' not in st.session_state:
    st.session_state['qr_data_string'] = None

with st.form("user_data_form"):
    name = st.text_input("Name")
    enrollment_no = st.text_input("Enrollment No.")
    grade_section = st.text_input("Grade/Section")
    submitted = st.form_submit_button("Generate QR Code")

    if submitted:
        if name and enrollment_no and grade_section:
            data = json.dumps({
                "Name": [name],
                "Enrollment No": [enrollment_no],
                "Grade/Section": [grade_section]
            })

    
            safe_name = sanitize_filename(name)
            safe_grade = sanitize_filename(grade_section)
            safe_enrollment = sanitize_filename(enrollment_no)
            filename = f"{safe_name}_{safe_grade}_{safe_enrollment}_qr.png"

            image_path = generate_qr_code(data, filename)
            st.session_state['qr_image_path'] = image_path
            st.session_state['qr_data_string'] = data
            st.success("QR Code Generated and Saved!")
        else:
            st.error("Please fill in all the fields.")

if st.session_state['qr_image_path']:
    st.markdown("---")
    st.subheader("Generated QR Code")
    st.image(st.session_state['qr_image_path'])  

    with open(st.session_state['qr_image_path'], "rb") as img_file:
        img_bytes = img_file.read()

    st.download_button(
        label="Download QR Code",
        data=img_bytes,
        file_name=os.path.basename(st.session_state['qr_image_path']),
        mime="image/png",
    )
    st.markdown("---")
    st.subheader("Data Encoded in QR Code")
    display_data_as_table(st.session_state['qr_data_string'])
    st.markdown("---")
