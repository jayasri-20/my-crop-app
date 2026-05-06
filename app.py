import streamlit as st
import pandas as pd
import pickle
import numpy as np
import os

# 1. Page Configuration
st.set_page_config(page_title="Smart Crop Intelligence", page_icon="🌱", layout="centered")

# 2. Advanced Styling (Labels clear-aa theriya)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)),
        url("https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?q=80&w=2000&auto=format&fit=crop");
        background-size: cover;
    }
    /* Input labels-ai bold white-aa black background-oda kaatta */
    label {
        color: white !important;
        font-weight: 900 !important;
        font-size: 20px !important;
        background-color: rgba(0, 0, 0, 0.7);
        padding: 5px 12px;
        border-radius: 4px;
        display: inline-block;
        margin-bottom: 8px !important;
    }
    .stNumberInput div div input {
        background-color: white !important;
        color: black !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Model Loading with Path Fix
base_path = os.path.dirname(__file__)
model_path = os.path.join(base_path, 'model.pkl')
encoder_path = os.path.join(base_path, 'label_encoder.pkl')

@st.cache_resource
def load_models():
    try:
        model = pickle.load(open(model_path, 'rb'))
        le = pickle.load(open(encoder_path, 'rb'))
        return model, le
    except Exception as e:
        return None, None

model, le = load_models()

# 4. App Logic
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔐 Login to Crop Intelligence")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        # Neenga use panna Username: jayasri, Password: 12345
        if username == "jayasri" and password == "12345":
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Invalid Username or Password")
else:
    st.title("🌱 Smart Crop Intelligence")
    st.write("Enter soil details to get the best crop recommendation.")

    if model is None:
        st.error("Model files missing in GitHub! Please ensure model.pkl and label_encoder.pkl are in the main folder.")
    else:
        # Input Fields
        col1, col2 = st.columns(2)
        with col1:
            n = st.number_input("Nitrogen (N)", min_value=0, max_value=140, value=50)
            p = st.number_input("Phosphorus (P)", min_value=0, max_value=145, value=50)
            k = st.number_input("Potassium (K)", min_value=0, max_value=205, value=50)
            temp = st.number_input("Temperature (°C)", min_value=8.0, max_value=44.0, value=25.0)
        
        with col2:
            hum = st.number_input("Humidity (%)", min_value=14.0, max_value=100.0, value=80.0)
            ph = st.number_input("pH Level", min_value=3.5, max_value=10.0, value=6.5)
            rain = st.number_input("Rainfall (mm)", min_value=20.0, max_value=300.0, value=100.0)

        if st.button("Predict Best Crop"):
            features = np.array([[n, p, k, temp, hum, ph, rain]])
            prediction = model.predict(features)
            crop_name = le.inverse_transform(prediction)[0]
            
            st.success(f"### Best Recommended Crop: **{crop_name.upper()}** 🌾")

    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()
