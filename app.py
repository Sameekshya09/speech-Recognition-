import streamlit as st
import os
import time
import glob
from gtts import gTTS
from googletrans import Translator
from textblob import TextBlob
import speech_recognition as sr

# Create a temporary directory to save audio files
if not os.path.exists("temp"):
    os.mkdir("temp")

# Set up page configuration
st.set_page_config(page_title="Text & Speech Converter", page_icon="🗣️", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 4px;
        }
        .stAudio, .stText {
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 5px;
        }
        .main-title {
            text-align: center;
            font-weight: bold;
            font-size: 32px;
        }
    </style>
    """, unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.title("Choose Functionality")
app_mode = st.sidebar.radio("Select Mode", ["Text to Speech", "Speech to Text"])

# Language settings
st.sidebar.title("Language Settings")
languages = ["English", "Hindi", "Bengali", "Korean", "Chinese", "Japanese"]
language_codes = {
    "English": "en", "Hindi": "hi", "Bengali": "bn",
    "Korean": "ko", "Chinese": "zh-cn", "Japanese": "ja"
}

if app_mode == "Text to Speech":
    # Main page title
    st.markdown("<h1 class='main-title'>🗣️ Text to Speech Converter</h1>", unsafe_allow_html=True)

    # Input and output language selection
    in_lang = st.sidebar.selectbox("Select your input language", languages)
    out_lang = st.sidebar.selectbox("Select your output language", languages)

    english_accent = st.sidebar.selectbox(
        "Select your English accent (if applicable)",
        ("Default", "India", "United Kingdom", "United States", "Canada", "Australia", "Ireland", "South Africa"),
    )

    input_language = language_codes[in_lang]
    output_language = language_codes[out_lang]

    accent_tld = {
        "Default": "com", "India": "co.in", "United Kingdom": "co.uk",
        "United States": "com", "Canada": "ca", "Australia": "com.au",
        "Ireland": "ie", "South Africa": "co.za"
    }

    tld = accent_tld[english_accent]

    # User input section
    st.markdown("### Enter your text below to convert it to speech:")
    text = st.text_area("Input your text here:", height=150)

    # File upload option
    uploaded_file = st.file_uploader("Or upload a text file", type=["txt", "docx"])

    # Checkbox to display output text and sentiment analysis
    display_output_text = st.checkbox("Display translated text")
    display_sentiment = st.checkbox("Display sentiment analysis")

    # Function to analyze sentiment
    def analyze_sentiment(text):
        blob = TextBlob(text)
        sentiment_polarity = blob.sentiment.polarity
        return sentiment_polarity

    # Convert button
    if st.button("Convert"):
        if uploaded_file is not None:
            # Read text from the uploaded file
            text = uploaded_file.read().decode('utf-8')
        if text.strip() == "":
            st.warning("Please enter or upload some text to convert.")
        else:
            # Function to convert text to speech
            def text_to_speech(input_language, output_language, text, tld):
                translator = Translator()
                translation = translator.translate(text, src=input_language, dest=output_language)
                trans_text = translation.text
                tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
                file_name = "audio_" + str(int(time.time()))
                tts.save(f"temp/{file_name}.mp3")
                return file_name, trans_text

            # Call the function and display the audio and text
            result, output_text = text_to_speech(input_language, output_language, text, tld)
            audio_file = open(f"temp/{result}.mp3", "rb")
            audio_bytes = audio_file.read()

            st.markdown("### Your audio:")
            st.audio(audio_bytes, format="audio/mp3", start_time=0)

            # Download button for the audio file
            st.download_button("Download Audio", audio_bytes, file_name=f"{result}.mp3", mime="audio/mp3")

            if display_output_text:
                st.markdown("### Output text:")
                st.write(output_text)

            if display_sentiment:
                sentiment_polarity = analyze_sentiment(text)
                sentiment_message = "Positive" if sentiment_polarity > 0 else "Negative" if sentiment_polarity < 0 else "Neutral"
                st.markdown(f"### Sentiment Analysis: **{sentiment_message}** (Polarity: {sentiment_polarity})")

elif app_mode == "Speech to Text":
    st.markdown("<h1 class='main-title'>🎤 Speech to Text Converter</h1>", unsafe_allow_html=True)

    # Input and output language selection
    st.sidebar.markdown("#### Speech Recognition Settings")
    st.sidebar.markdown("Select the language for speech recognition:")
    speech_rec_lang = st.sidebar.selectbox("Speech Recognition Language", languages)
    speech_rec_code = language_codes[speech_rec_lang]

    st.sidebar.markdown("Select the output language for translation:")
    speech_trans_lang = st.sidebar.selectbox("Translation Output Language", languages)
    speech_trans_code = language_codes[speech_trans_lang]

    recognizer = sr.Recognizer()

    # Button to start listening
    if st.button("Start Listening"):
        with sr.Microphone() as source:
            st.write("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio_data = recognizer.listen(source)

        try:
            # Convert speech to text
            text = recognizer.recognize_google(audio_data, language=speech_rec_code)
            st.markdown("### Recognized Text:")
            st.write(text)

            # Translate text if different output language is selected
            if speech_rec_code != speech_trans_code:
                translator = Translator()
                translation = translator.translate(text, src=speech_rec_code, dest=speech_trans_code)
                trans_text = translation.text
                st.markdown("### Translated Text:")
                st.write(trans_text)

        except sr.UnknownValueError:
            st.write("Sorry, I could not understand the audio.")
        except sr.RequestError as e:
            st.write(f"Could not request results from Google Speech Recognition service; {e}")

# Function to remove old audio files
def remove_files(n):
    mp3_files = glob.glob("temp/*.mp3")
    now = time.time()
    cutoff_time = now - n * 86400  # Convert days to seconds
    for file_path in mp3_files:
        if os.stat(file_path).st_mtime < cutoff_time:
            os.remove(file_path)

# Clean up old files every 7 days
remove_files(7)

st.sidebar.info("This app combines text-to-speech and speech-to-text functionalities with language translation and sentiment analysis.")
st.sidebar.markdown(
    """
    **Instructions:**
    1. Choose the functionality from the sidebar.
    2. For Text to Speech, enter the text or upload a file.
    3. For Speech to Text, press 'Start Listening' to begin recording.
    4. Choose languages for input, output, and speech recognition.
    5. Click 'Convert' or 'Start Listening' to see the results.
    """
)



