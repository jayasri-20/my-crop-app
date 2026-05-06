import streamlit as st
import pandas as pd
import pickle
import numpy as np
from datetime import datetime
import os

# 1. Page Configuration
st.set_page_config(page_title="Crop Intelligence Pro", page_icon="🌿", layout="centered")

# 2. Advanced Styling for Better Visibility
st.markdown("""
    <style>
    /* Full Page Background */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
                    url("https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?q=80&w=2000&auto=format&fit=crop");
        background-size: cover;
    }

    /* Input Labels - Perusa matrum Clear-aa theriya */
    label {
        color: white !important;
        font-weight: 900 !important;
        font-size: 22px !important;
        background-color: rgba(0, 0, 0, 0.6); /* Black background for text */
        padding: 5px 15px;
        border-radius: 10px;
        display: inline-block;
        margin-bottom: 10px !important;
    }

    /* Input Box Styling */
    .stNumberInput input {
        font-size: 18px !important;
        font-weight: bold !important;
        color: #2ecc71 !important;
    }

    /* Card Styling */
    .main-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
    }

    /* Button Styling */
    div.stButton > button {
        background: #2ecc71;
        color: white !important;
        border-radius: 50px;
        width: 100%;
        height: 55px;
        font-size: 20px;
        font-weight: bold;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# Function to save user data to a CSV
def save_user_log(name, gender, age):
    log_file = "user_database.csv"
    now = datetime.now()
    dt = now.strftime("%Y-%m-%d %H:%M:%S")
    
    new_entry = pd.DataFrame([[name, gender, age, dt]], columns=['Name', 'Gender', 'Age', 'Login_Time'])
    
    if not os.path.isfile(log_file):
        new_entry.to_csv(log_file, index=False)
    else:
        new_entry.to_csv(log_file, mode='a', header=False, index=False)

# 3. Session Management
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# --- LOGIN & DETAILS PAGE ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: #2ecc71;'>🌾 Welcome to Crop Advisor</h1>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='main-card'>", unsafe_allow_html=True)
        name = st.text_input("Your Name")
        gender = st.radio("Gender", ["Male", "Female", "Other"], horizontal=True)
        age = st.number_input("Your Age", min_value=1, max_value=100, step=1)
        password = st.text_input("Password", type="password")
        
        if st.button("Sign In"):
            if name and password:
                save_user_log(name, gender, age)
                st.session_state.user_name = name
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Dhayavu seidhu ella details-aiyum fill pannunga!")
        st.markdown("</div>", unsafe_allow_html=True)

# --- MAIN PREDICTION PAGE ---
else:
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👋 Hello, {st.session_state.user_name}!")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown("<h1 style='text-align: center; color: white;'>🌱 Smart Crop Intelligence</h1>", unsafe_allow_html=True)
    st.write("---")

    # Load Model
    try:
        model = pickle.load(open('model.pkl', 'rb'))
        le = pickle.load(open('label_encoder.pkl', 'rb'))
    except:
        st.error("Model files missing!")

    # Inputs - Clear Labels with Black Background
    col1, col2 = st.columns(2)
    with col1:
        n = st.number_input("Nitrogen (N)", min_value=0)
        p = st.number_input("Phosphorus (P)", min_value=0)
        k = st.number_input("Potassium (K)", min_value=0)
        temp = st.number_input("Temperature (°C)", min_value=0.0)

    with col2:
        hum = st.number_input("Humidity (%)", min_value=0.0)
        ph = st.number_input("pH level", min_value=0.0)
        rain = st.number_input("Rainfall (mm)", min_value=0.0)

    st.write("")
    if st.button("🔍 Predict Best Crop"):
        data = np.array([[n, p, k, temp, hum, ph, rain]])
        prediction = model.predict(data)
        crop_name = le.inverse_transform(prediction)[0].upper()

        # Specific Emojis
        emojis = {"RICE": "🍚", "WHEAT": "🌾", "MAIZE": "🌽", "TEA": "🍃", "COTTON": "☁️", "BANANA": "🍌"}
        icon = emojis.get(crop_name, "🌱")

        st.balloons()
        st.markdown(f"""
            <div style="background: white; padding: 30px; border-radius: 20px; text-align: center; color: #2c3e50;">
                <h1 style='font-size: 100px; margin: 0;'>{icon}</h1>
                <h2 style='color: #27ae60; font-size: 40px;'>{crop_name}</h2>
                <p style='font-size: 20px;'>Intha mannu-ku intha payir migavum sariyaanadhu!</p>
            </div>
        """, unsafe_allow_html=True)