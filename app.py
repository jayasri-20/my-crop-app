import streamlit as st
import pandas as pd
import numpy as np
import requests
import os
import base64
import speech_recognition as sr
from gtts import gTTS
from PIL import Image

# --- 1. SOIL MASTER DATABASE ---
SOIL_MASTER = {
    "black": {"n": 95, "p": 55, "k": 45, "name": "Karisal Mannu (Black Soil)", "msg": "Karisal mannu kandupidikkappattadhu. Idhil Nitrogen matrum Phosphorus athigamaaga irukkum."},
    "red": {"n": 75, "p": 45, "k": 35, "name": "Sivappu Mannu (Red Soil)", "msg": "Sivappu mannu kandupidikkappattadhu. Idhil eerappadham kuraivaaga irukkum."},
    "alluvial": {"n": 100, "p": 60, "k": 50, "name": "Vandall Mannu (Alluvial Soil)", "msg": "Vandall mannu kandupidikkappattadhu. Idhu payir valarchikku migavum ughandhadhu."},
    "clay": {"n": 85, "p": 50, "k": 40, "name": "Kalimannu (Clay Soil)", "msg": "Kalimannu kandupidikkappattadhu. Idhil neer thaangum thiran athigam."},
    "sandy": {"n": 40, "p": 25, "k": 20, "name": "Manal Mannu (Sandy Soil)", "msg": "Manal mannu kandupidikkappattadhu. Idhil sathukkal kuraivaaga ulladhu."},
    "laterite": {"n": 60, "p": 35, "k": 30, "name": "Semmai Mannu (Laterite)", "msg": "Laterite mannu vagai kandupidikkappattadhu."},
    "loamy": {"n": 90, "p": 50, "k": 50, "name": "Pasumai Mannu (Loamy Soil)", "msg": "Pasumai mannu kandupidikkappattadhu. Idhu nalla kalavai mannu."},
    "default": {"n": 50, "p": 40, "k": 40, "name": "Standard Soil", "msg": "Mannu vagai kandupidikkappattadhu."}
}

# --- NEW: DISEASE DATABASE ---
DISEASE_MASTER = {
    "leaf blast": {
        "name": "Leaf Blast (Ilaikkari Noi)",
        "solution": "Theervu: Tricyclazole 75 WP @ 0.6 g/lit spray pannunga. Nitrogen urathai kuraiyunga.",
        "msg": "Ungal chediyil Ilaikkari noi kandupidikkappattadhu."
    },
    "brown spot": {
        "name": "Brown Spot (Palaikkan Noi)",
        "solution": "Theervu: Mancozeb @ 2.0 g/lit spray pannunga. Potassium sethu kollunga.",
        "msg": "Ungal chediyil Palaikkan noi kandupidikkappattadhu."
    },
    "rust": {
        "name": "Rust (Thuru Noi)",
        "solution": "Theervu: Copper Oxychloride spray pannunga. Nozh thaakkiya ilaigalai agattrunga.",
        "msg": "Ungal chediyil Thuru noi kandupidikkappattadhu."
    },
    "default": {
        "name": "Healthy / Unknown",
        "solution": "Theervu: Chedi aarokkiyamaaga illai, adhanal viraivaana vivasaaya maiyathai anugavum.",
        "msg": "Sariyaaga kandupidikka mudiyavillai."
    }
}

# --- CROP CULTIVATION REGIONS DATABASE ---
CROP_REGIONS = {
    "TEA (Theylai)": {
        "regions": "Nilgiris, Coimbatore (Valparai), Assam, and Kerala.",
        "voice": "Idhu adhigamaaga Nilagiri, Valparai, Assam matrum Kerala-vil valarkkappadugiradhu."
    },
    "RICE (Nel)": {
        "regions": "Thanjavur, Tiruvarur, Nagapattinam, West Bengal, and Punjab.",
        "voice": "Idhu adhigamaaga Thanjavur, Tiruvarur, Nagapattinam, matrum West Bengal-il valarkkappadugiradhu."
    },
    "RUBBER": {
        "regions": "Kanyakumari, Kerala, and Tripura.",
        "voice": "Idhu adhigamaaga Kanyakumari matrum Kerala-vil valarkkappadugiradhu."
    },
    "SUGARCANE (Karumbu)": {
        "regions": "Villupuram, Erode, Kallakurichi, Uttar Pradesh, and Maharashtra.",
        "voice": "Idhu adhigamaaga Villupuram, Erode, Uttar Pradesh matrum Maharashtra-vil valarkkappadugiradhu."
    },
    "MAIZE (Makkacholam)": {
        "regions": "Salem, Perambalur, Dindigul, Karnataka, and Andhra Pradesh.",
        "voice": "Idhu adhigamaaga Salem, Perambalur, Dindigul matrum Karnataka-vil valarkkappadugiradhu."
    },
    "COTTON (Paruthi)": {
        "regions": "Coimbatore, Tiruppur, Madurai, Gujarat, and Maharashtra.",
        "voice": "Idhu adhigamaaga Coimbatore, Tiruppur, Gujarat matrum Maharashtra-vil valarkkappadugiradhu."
    },
    "GROUNDNUT (Nilakkadali)": {
        "regions": "Tiruvannamalai, Vellore, Villupuram, and Gujarat.",
        "voice": "Idhu adhigamaaga Tiruvannamalai, Vellore, Villupuram matrum Gujarat-il valarkkappadugiradhu."
    },
    "WHEAT (Godhumai)": {
        "regions": "Uttar Pradesh, Punjab, Haryana, and Madhya Pradesh.",
        "voice": "Idhu adhigamaaga Uttar Pradesh, Punjab, matrum Haryana-vil valarkkappadugiradhu."
    },
    "BAJRA (Kambu)": {
        "regions": "Thoothukudi, Virudhunagar, Rajasthan, and Gujarat.",
        "voice": "Idhu adhigamaaga Thoothukudi, Virudhunagar matrum Rajasthan-il valarkkappadugiradhu."
    },
    "RAGI": {
        "regions": "Krishnagiri, Dharmapuri, and Karnataka.",
        "voice": "Idhu adhigamaaga Krishnagiri, Dharmapuri matrum Karnataka-vil valarkkappadugiradhu."
    },
    "PULSES (Paruppu Vagaigal)": {
        "regions": "Thanjavur, Pudukkottai, Madhya Pradesh, and Rajasthan.",
        "voice": "Idhu adhigamaaga Thanjavur, Pudukkottai matrum Madhya Pradesh-il valarkkappadugiradhu."
    }
}

# --- NEW: SIDEBAR CROP MONTHS & SCIENTIFIC REASONS DATABASE ---
SIDEBAR_CROP_DETAILS = {
    "Select a Crop...": {"months": "", "reason": ""},
    "Sugarcane (Karumbu)": {"months": "10 முதல் 12 மாதங்கள்", "reason": "கரும்பு ஒரு நீண்ட கால பயிர். இதன் தண்டு பகுதியில் சர்க்கரை சத்து முழுமையாக ஊறி முதிர்ச்சியடைய அதிக நாட்கள் தேவைப்படுகிறது."},
    "Cotton (Paruthi)": {"months": "5 முதல் 6 மாதங்கள்", "reason": "பொருத்தி செடி வளர்ந்து, பூ பூத்து, காய் வெடித்து பஞ்சு தயாராக நீண்ட கால சீரான வெப்பம் தேவைப்படுகிறது."},
    "Jute (Sanappu)": {"months": "4 முதல் 5 மாதங்கள்", "reason": "இதன் தண்டு பகுதியில் இருந்து நார் பிரித்தெடுக்க ஏதுவாக செடி உயரமாகவும் வலுவாகவும் வளர இவ்வளவு காலம் ஆகிறது."},
    "Tea (Theylai)": {"months": "3 முதல் 4 ஆண்டுகள் (முதல் அறுவடைக்கு)", "reason": "தேயிலை ஒரு பல்லாண்டு பயிர். இலைகள் தொடர்ந்து துளிர்விட செடியின் வேர்கள் மண்ணில் ஆழமாக நிலைபெற வேண்டும்."},
    "Coffee (Kaapi)": {"months": "3 முதல் 4 ஆண்டுகள் (முதல் அறுவடைக்கு)", "reason": "காபி செடி வளர்ந்து அதன் பழங்கள் பழுத்து அறுவடைக்கு வர பல மாதங்கள் நீடித்த ஈரப்பதம் தேவைப்படுகிறது."},
    "Tobacco (Pugaiyilai)": {"months": "4 முதல் 5 மாதங்கள்", "reason": "இதன் இலைகள் பெரியதாக வளர்ந்து, அதில் உள்ள நிக்கோடின் சத்து சரியான அளவில் முதிர இந்த நாட்கள் தேவை."},
    "Rubber": {"months": "5 முதல் 7 ஆண்டுகள் (பால் எடுக்க)", "reason": "ரப்பர் மரம் தடிமனாகி, அதிலிருந்து லேடெக்ஸ் எனும் பால் சுரக்கும் அளவுக்கு திசுக்கள் முதிர்ச்சியடைய பல வருடங்கள் ஆகும்."},
    "Spices (Masaala Vagaigal)": {"months": "6 முதல் 8 மாதங்கள்", "reason": "மஞ்சள், மிளகாய் போன்ற பயிர்களின் கிழங்குகள் மற்றும் விதைகள் நறுமண எண்ணெய்களைச் சேமிக்க அதிக காலம் எடுக்கிறது."},
    "Cashew (Mundhiri)": {"months": "3 ஆண்டுகள் (முதல் பலனுக்கு)", "reason": "முந்திரி மரம் பூ பூத்து, கொட்டைகளுடன் கூடிய பழங்கள் மரத்தில் முதிர்வடைய நீண்ட பருவகால சுழற்சி தேவை."},
    "Oilseeds (Ennai Vithu)": {"months": "3 முதல் 4 மாதங்கள்", "reason": "நிலக்கடலை, கடுகு போன்ற பயிர்களின் விதைகளில் எண்ணெய் சத்து முழுமையாகக் கூட இந்த நாட்கள் அவசியம்."},
    "Rice (Nel)": {"months": "3 முதல் 4 மாதங்கள்", "reason": "நெற்பயிர்கள் தூர்வாரி, கதிர் விட்டு, தானியங்கள் பால் பிடித்து முதிர்வடைய இந்த கால அளவு தேவைப்படுகிறது."},
    "Wheat (Godhumai)": {"months": "4 முதல் 5 மாதங்கள்", "reason": "கோதுமை பயிர் பனிக்காலத்தில் வளர்ந்து, பின் வெயில் காலத்தில் தானியங்கள் காய்ந்து முதிர இவ்வளவு காலம் ஆகிறது."},
    "Maize (Makkacholam)": {"months": "3 முதல் 4 மாதங்கள்", "reason": "சோளக் கதிர்கள் பெரியதாக வளர்ந்து, அதனுள் முத்துக்கள் கெட்டியாக மாறுவதற்கு சீரான சூரிய ஒளி தேவை."},
    "Ragi (Kelvaragu)": {"months": "3 முதல் 4 மாதங்கள்", "reason": "கேழ்வரகின் சிறிய தானியக் கதிர்கள் வறட்சியைத் தாங்கி வளர்ந்து முதிர்ச்சியடைய இந்த நாட்கள் ஆகும்."},
    "Jowar (Cholam)": {"months": "4 மாதங்கள்", "reason": "சோளப் பயிரின் தண்டு பகுதி வலுவடைந்து கதிர்கள் திரட்சியாக வளர்வதற்கு இந்த காலம் தேவைப்படுகிறது."},
    "Bajra (Kambu)": {"months": "3 மாதங்கள்", "reason": "கம்பு மிகக் குறுகிய காலத்தில் வளரக்கூடியது, மணல் பாங்கான நிலத்திலும் வேகமாக கதிர்விட்டு முதிர்ந்துவிடும்."},
    "Pulses (Paruppu Vagaigal)": {"months": "3 மாதங்கள்", "reason": "பயறு வகைகள் காற்றில் உள்ள நைட்ரஜனை வேர்களில் சேமித்து, வேகமாக வளர்ந்து காய்களை உருவாக்கிவிடும்."},
    "Potato (Uruzaikkizhangu)": {"months": "3 முதல் 4 மாதங்கள்", "reason": "மண்ணுக்கு அடியில் கிழங்குகள் உருவாவதற்கும், அதில் ஸ்டார்ச் சத்து சேமிக்கப்படுவதற்கும் குளிர்ந்த வானிலை தேவை."},
    "Onion (Vengayam)": {"months": "3 முதல் 4 மாதங்கள்", "reason": "வெங்காயத் தாள்கள் வளர்ந்து, பின் மண்ணுக்கு அடியில் இருக்கும் வெங்காயக் குமிழ்கள் பெருக்க இந்த நாட்கள் ஆகும்."},
    "Coconut (Thengai)": {"months": "5 முதல் 7 ஆண்டுகள் (காய்க்க தொடங்க)", "reason": "தென்னை மரம் உயரமாக வளர்ந்து, அதன் பாளைகள் முதிர்ந்து தேங்காய்கள் உருவாக வருட கணக்கில் காலம் எடுக்கும்."}
}

# --- 2. CORE FUNCTIONS ---
def speak(text):
    try:
        tts = gTTS(text=text, lang='ta')
        tts.save("temp_voice.mp3")
        with open("temp_voice.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(md, unsafe_allow_html=True)
        os.remove("temp_voice.mp3")
    except: pass

def get_voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.sidebar.info("🎙️ Listening...")
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)
        try:
            return r.recognize_google(audio, language="ta-IN")
        except: return None

def get_weather(city):
    api_key = "8c9a017105244988a37b8036a3a60c56" 
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        res = requests.get(url).json()
        if res.get("cod") == 200:
            return res["main"]["temp"], res["main"]["humidity"]
    except: return None, None

# --- 3. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="Crop Intelligence Pro", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)), 
                    url("https://img.freepik.com/premium-photo/meadow-wheat-sunset-nature-composition_157744-1696.jpg");
        background-size: cover;
    }
    
    /* ATTRACTIVE GLASSMORPHISM FOR SIDEBAR MENU BAR */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, rgba(20, 50, 25, 0.9), rgba(10, 25, 40, 0.95)) !important;
        backdrop-filter: blur(20px);
        border-right: 3px solid rgba(30, 126, 52, 0.5);
    }
    
    /* ENHANCING TEXT VISIBILITY IN SIDEBAR */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4, [data-testid="stSidebar"] span, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #ffffff !important;
        font-weight: bold !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.9) !important;
    }
    
    /* STYLING SELECTBOX & INPUTS INSIDE SIDEBAR FOR BETTER CONTRAST */
    [data-testid="stSidebar"] div[data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] span {
        color: #ffffff !important;
        text-shadow: none !important;
    }

    .glass-card {
        background: rgba(0, 0, 0, 0.65) !important;
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 30px;
        color: #ffffff !important;
        border: 2px solid rgba(255,255,255,0.25);
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    .glass-card p, .glass-card li, .glass-card h1, .glass-card h2, .glass-card h3, .glass-card span {
        color: #ffffff !important;
        font-weight: 500;
    }
    label { 
        color: #ffffff !important; 
        font-weight: bold !important;
        font-size: 16px !important;
        text-shadow: 1px 1px 2px black;
    }
    div.stButton > button {
        background-color: #1e7e34 !important;
        color: white !important;
        font-weight: bold;
        border-radius: 10px;
        width: 100%;
        border: 1px solid white;
    }
    .white-text-list {
        color: #ffffff !important;
        font-size: 16px !important;
        font-weight: bold !important;
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Session States
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'n_val' not in st.session_state: st.session_state.n_val = 0
if 'p_val' not in st.session_state: st.session_state.p_val = 0
if 'k_val' not in st.session_state: st.session_state.k_val = 0
if 'temp_val' not in st.session_state: st.session_state.temp_val = 28.0
if 'hum_val' not in st.session_state: st.session_state.hum_val = 70.0
if 'ph_val' not in st.session_state: st.session_state.ph_val = 6.5
if 'rain_val' not in st.session_state: st.session_state.rain_val = 120.0
if 'city' not in st.session_state: st.session_state.city = ""
if 'last_selected_crop' not in st.session_state: st.session_state.last_selected_crop = "Select a Crop..."

# --- 4. LOGIN PAGE ---
if not st.session_state.logged_in:
    st.markdown('<h1 style="color:white; text-align:center;">🌿 Smart Crop Intelligence</h1>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Login to Dashboard")
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            u_name = st.text_input("User Name")
            reg_id = st.text_input("Reg ID")
        with col_l2:
            password = st.text_input("Password", type="password") 
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        
        age = st.number_input("Age", value=20, min_value=1)
        
        if st.button("LOGIN"):
            if u_name and reg_id and password == "12345":
                st.session_state.logged_in = True
                st.session_state.user_name = u_name
                st.rerun()
            elif password != "12345" and password != "":
                st.error("Thappana Password! Marubadiyum try pannunga.")
            else:
                st.warning("Ella details-aiyum fill pannunga.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. DASHBOARD ---
else:
    with st.sidebar:
        st.title(f"👋 {st.session_state.user_name}")
        st.write("---")
        
        # 📋 NEW: SIDEBAR CROP SELECTION WITH VOICE ASSISTANT
        st.subheader("🌱 Crop Info & Duration")
        selected_crop = st.selectbox("Choose a crop to know details:", list(SIDEBAR_CROP_DETAILS.keys()))
        
        if selected_crop != "Select a Crop..." and selected_crop != st.session_state.last_selected_crop:
            st.session_state.last_selected_crop = selected_crop
            crop_data = SIDEBAR_CROP_DETAILS[selected_crop]
            
            st.info(f"⏱️ **Duration:** {crop_data['months']}")
            st.write(f"🔬 **Reason:** {crop_data['reason']}")
            
            # Voice assistant triggers immediately when a crop is touched/selected
            crop_voice_msg = f"{selected_crop} பயிர் வளர்வதற்கு {crop_data['months']} ஆகும். இதன் அறிவியல் காரணம்: {crop_data['reason']}"
            speak(crop_voice_msg)
            
        st.write("---")
        
        # 📸 SOIL SCANNER
        st.subheader("📸 Soil Variety Scanner")
        uploaded_file = st.file_uploader("Upload Soil Photo", type=["jpg", "png", "jpeg"], key="soil_uploader")
        if uploaded_file:
            img = Image.open(uploaded_file)
            st.image(img, caption="Scanning...", use_container_width=True)
            fname = uploaded_file.name.lower()
            detected_key = "default"
            for key in SOIL_MASTER:
                if key in fname: detected_key = key; break
            data = SOIL_MASTER[detected_key]
            st.session_state.n_val, st.session_state.p_val, st.session_state.k_val = data['n'], data['p'], data['k']
            st.sidebar.success(f"Detected: {data['name']}")
            speak(f"{data['msg']}. Nitrogen {data['n']}, Phosphorus {data['p']}, Potassium {data['k']}.")

        st.write("---")

        # 🏥 NEW: PLANT DISEASE DIAGNOSIS
        st.subheader("🏥 Disease Diagnosis")
        leaf_file = st.file_uploader("Upload Leaf Photo", type=["jpg", "png", "jpeg"], key="leaf_uploader")
        if leaf_file:
            leaf_img = Image.open(leaf_file)
            st.image(leaf_img, caption="Diagnosing Leaf...", use_container_width=True)
            lfname = leaf_file.name.lower()
            d_key = "default"
            for dk in DISEASE_MASTER:
                if dk in lfname: d_key = dk; break
            d_data = DISEASE_MASTER[d_key]
            st.sidebar.warning(f"**Noi:** {d_data['name']}")
            st.sidebar.info(f"**{d_data['solution']}**")
            speak(f"{d_data['msg']}. {d_data['solution']}")

        st.write("---")
        
        # 🌤️ WEATHER & TEMPERATURE
        st.subheader("🌤️ Weather Condition")
        city_input = st.text_input("Enter City/Village")
        if st.button("Fetch Weather"):
            t, h = get_weather(city_input)
            if t:
                st.session_state.temp_val, st.session_state.hum_val = t, h
                st.session_state.city = city_input
                
                # --- RAINFALL BASED ON WEATHER (HUMIDITY) ---
                if h >= 85:
                    st.session_state.rain_val = 1800.0  
                elif h >= 70:
                    st.session_state.rain_val = 1200.0  
                elif h >= 50:
                    st.session_state.rain_val = 650.0   
                else:
                    st.session_state.rain_val = 250.0   
                
                st.sidebar.info(f"{t}°C | {h}% Humidity")
                
                # --- UPDATED VOICE ASSISTANT ---
                weather_voice = f"Ippo {city_input} oorula veppam {t} degree, eerappadham {h} percentage, mazhaippozhivu {st.session_state.rain_val} millimeter, matrum pH thunivu {st.session_state.ph_val}."
                speak(weather_voice)

        if st.session_state.city:
            map_url = f"https://maps.google.com/maps?q={st.session_state.city.replace(' ','+')}&t=&z=13&ie=UTF8&iwloc=&output=embed"
            st.markdown(f'<iframe width="100%" height="150" src="{map_url}"></iframe>', unsafe_allow_html=True)
            
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # --- MAIN DISPLAY ---
    st.markdown('<h1 style="color:white; text-align:center;">🌿 Crop Recommendation Dashboard</h1>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Soil & Climate Parameters")
        col1, col2 = st.columns(2)
        with col1:
            n_in = st.number_input("Nitrogen (N)", value=st.session_state.n_val)
            p_in = st.number_input("Phosphorus (P)", value=st.session_state.p_val)
            k_in = st.number_input("Potassium (K)", value=st.session_state.k_val)
            t_in = st.number_input("Temperature (°C)", value=st.session_state.temp_val)
        with col2:
            h_in = st.number_input("Humidity (%)", value=st.session_state.hum_val)
            ph_in = st.number_input("pH Level", value=st.session_state.ph_val)
            st.session_state.ph_val = ph_in 
            rain_in = st.number_input("Rainfall (mm)", value=st.session_state.rain_val)
            st.session_state.rain_val = rain_in
            
        if st.button("🔍 PREDICT BEST CROP"):
            st.balloons()
            
            # --- DYNAMIC INTELLIGENCE LOGIC BASED ON INPUTS ---
            if rain_in >= 2000 and ph_in <= 6.0:
                res = "TEA (Theylai)"
            elif rain_in >= 1500 and h_in >= 80:
                if n_in >= 80:
                    res = "RICE (Nel)"
                else:
                    res = "RUBBER"
            elif rain_in >= 1100 and n_in >= 90 and p_in >= 50:
                res = "SUGARCANE (Karumbu)"
            elif n_in >= 80 and p_in >= 50 and rain_in >= 700 and rain_in < 1100:
                res = "MAIZE (Makkacholam)"
            elif n_in >= 70 and p_in >= 40 and h_in <= 60:
                res = "COTTON (Paruthi)"
            elif ph_in >= 6.0 and ph_in <= 7.5 and t_in >= 25 and t_in <= 35 and rain_in < 700:
                res = "GROUNDNUT (Nilakkadali)"
            elif t_in < 22 and rain_in >= 600 and rain_in <= 1000:
                res = "WHEAT (Godhumai)"
            elif n_in <= 50 and rain_in < 500:
                if ph_in >= 7.0:
                    res = "BAJRA (Kambu)"
                else:
                    res = "RAGI"
            else:
                res = "PULSES (Paruppu Vagaigal)"
                
            # Get Cultivation Regions Info
            region_info = CROP_REGIONS.get(res, {"regions": "Various regions across India.", "voice": "Idhu India-vilப்பல idangalil valarkkappadugiradhu."})
            
            # Display Prediction result & Cultivation text details
            st.markdown(f"""
                <div style='background:white; color:green; padding:20px; border-radius:15px; text-align:center; margin-bottom:15px;'>
                    <h2>🌱 Recommended: {res}</h2>
                </div>
                <div style='background: #1e7e34; padding: 20px; border-radius: 15px; border: 2px solid #ffffff; box-shadow: 0 4px 8px rgba(0,0,0,0.3);'>
                    <h4 style='color: #ffffff !important; font-weight: bold; margin: 0; font-size: 20px;'>📍 Major Cultivation Regions:</h4>
                    <p style='color: #ffffff !important; font-size: 18px; font-weight: 500; margin-top: 8px;'>{region_info['regions']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Combined voice explanation
            full_voice_msg = f"Ungal mannu ku {res} payir seivadhu sirappu. {region_info['voice']}"
            speak(full_voice_msg)
            
        st.markdown('</div>', unsafe_allow_html=True)   

    # --- MAIN/CENTER DISPLAY: CROP CLASSIFICATION REFERENCE ---
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h2 style="color:white; text-align:center; text-shadow: 2px 2px 4px #000000;">📋 Agricultural Crops Classification Guide</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:white; text-align:center;">Here is the list of major categories of crops grown and utilized across regions:</p>', unsafe_allow_html=True)
    st.write("<br>", unsafe_allow_html=True)
    
    col_crop1, col_crop2 = st.columns(2)
    
    with col_crop1:
        st.markdown('<h3 style="color:#ffffff; text-decoration: underline;">💰 Cash Crops (Panappayirgal)</h3>', unsafe_allow_html=True)
        st.markdown('<div class="white-text-list">- Sugarcane</div>', unsafe_allow_html=True)
        st.markdown('<div class="white-text-list">- Cotton</div>', unsafe_allow_html=True)
        st.markdown('<div class="white-text-list">- Jute</div>', unsafe_allow_html=True)
        st.markdown('<div class="white-text-list">- Tea</div>', unsafe_allow_html=True)
        st.markdown('<div class="white-text-list">- Coffee</div>', unsafe_allow_html=True)
        st.markdown('<div class="white-text-list">- Tobacco</div>', unsafe_allow_html=True)
        st.markdown('<div class="white-text-list">- Rubber</div>', unsafe_allow_html=True)
        st.markdown('<div class="white-text-list">- Spices (Milagai, Manjal, Milagu)</div>', unsafe_allow_html=True)
        st.markdown('<div class="white-text-list">- Cashew</div>', unsafe_allow_html=True)
        st.markdown('<div class="white-text-list">- Oilseeds (Nilakkadali, Kadugu, Soybean)</div>', unsafe_allow_html=True)

    with col_crop2:
        st.markdown('<h3 style="color:#ffffff; text-decoration: underline;">🌾 Mostly Used Crops (Athigamaaga Payanpaduthappadum Payirgal)</h3>', unsafe_allow_html=True)
        st.markdown('<div class="white-text-list">- Rice (Nel)</div>', unsafe_allow_html=True)
        st.markdown('<div class="white-text-list">- Wheat (Godhumai)</div>', unsafe_allow_html=True)
        st.markdown('<div class="white-text-list">- Maize (Makkacholam)</div>', unsafe_allow_html=True)
        st.markdown('<div class="white-text-list">- Ragi</div>', unsafe_allow_html=True)
        st.markdown('<div class="white-text-list">- Jowar (Cholam)</div>', unsafe_allow_html=True)
        st.markdown('<div class="white-text-list">- Bajra (Kambu)</div>', unsafe_allow_html=True)
        st.markdown('<div class="white-text-list">- Pulses (Paruppu vagaigal - Thuvarai, Uzhandhu, Pasipayiru)</div>', unsafe_allow_html=True)
        st.markdown('<div class="white-text-list">- Potato (Uruzaikkizhangu)</div>', unsafe_allow_html=True)
        st.markdown('<div class="white-text-list">- Onion (Vengayam)</div>', unsafe_allow_html=True)
        st.markdown('<div class="white-text-list">- Coconut (Thengai)</div>', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
