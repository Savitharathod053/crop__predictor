import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import requests
from PIL import Image
import speech_recognition as sr

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Smart Farming", page_icon="🌾")

# ---------------- DARK UI ----------------
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background-color: black;
    color: white;
}

h1, h2, h3, h4, h5, h6, p, label {
    color: white !important;
}

.stButton>button {
    background-color: #00ff99;
    color: black;
    border-radius: 10px;
    height: 3em;
    width: 100%;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ---------------- LANGUAGE ----------------
language = st.selectbox("Select Language", ["English", "తెలుగు"])

# ---------------- TITLE ----------------
if language == "తెలుగు":
    st.title("🌾 స్మార్ట్ వ్యవసాయ సహాయకుడు")
else:
    st.title("🌾 Smart Farming Assistant")

# ---------------- LOAD DATA ----------------
data = pd.read_csv("Crop_recommendation.csv")

X = data.drop("label", axis=1)
y = data["label"]

model = RandomForestClassifier()
model.fit(X, y)

# ---------------- VOICE FUNCTION ----------------
def voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎤 Speak now...")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            return text
        except:
            return ""

# ---------------- WEATHER ----------------
def get_weather(city):
    api_key = "1363cc7c140d05f8f8b6762ec443c244"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    res = requests.get(url).json()

    temp = res["main"]["temp"]
    humidity = res["main"]["humidity"]
    rainfall = res.get("rain", {}).get("1h", 0)

    return temp, humidity, rainfall

# ---------------- CITY INPUT ----------------
if language == "తెలుగు":
    city = st.text_input("మీ నగరం నమోదు చేయండి")
else:
    city = st.text_input("Enter your city")

# 🎤 MIC BUTTON
if st.button("🎤 Speak City"):
    spoken_text = voice_input()
    if spoken_text:
        city = spoken_text
        st.write(f"You said: {city}")

# ---------------- WEATHER DISPLAY ----------------
if city:
    try:
        temp, humidity, rainfall = get_weather(city)
        st.subheader("🌦️ Weather Data")
        st.write(f"📍 Location: {city}")
        st.write(f"🌡️ Temperature: {temp} °C")
        st.write(f"💧 Humidity: {humidity} %")

        if rainfall == 0:
            st.write("🌧️ Rainfall: No rain")
        else:
            st.write(f"🌧️ Rainfall: {rainfall} mm")

    except:
        st.error("Invalid city")
        temp, humidity, rainfall = 25, 60, 0
else:
    temp, humidity, rainfall = 25, 60, 0

# ---------------- SOIL INPUT ----------------
st.subheader("Soil Details")

N = st.number_input("Nitrogen", 0, 150)
P = st.number_input("Phosphorus", 0, 150)
K = st.number_input("Potassium", 0, 150)
ph = st.slider("Soil pH", 0.0, 14.0, 6.5)

# ---------------- IMAGE UPLOAD ----------------
st.subheader("📷 Upload Soil Image")
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Soil Image")
    st.success("Soil looks fertile 🌱")

# ---------------- PREDICTION ----------------
if st.button("🌱 Predict Crop"):
    values = [[N, P, K, temp, humidity, ph, rainfall]]
    result = model.predict(values)
    crop = result[0]

    st.success(f"✅ Recommended Crop: {crop}")

    # ---------------- FERTILIZER ----------------
    if crop == "rice":
        st.info("🌿 Use Nitrogen-rich fertilizer")
    elif crop == "wheat":
        st.info("🌱 Use balanced NPK fertilizer")
    elif crop == "maize":
        st.info("🌾 Use phosphorus fertilizer")
    else:
        st.info("Use organic compost fertilizer")