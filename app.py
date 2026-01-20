import streamlit as st
import speech_recognition as sr
import io
from datetime import datetime

# =====================================================
# Streamlit config (MUST be first)
# =====================================================
st.set_page_config(
    page_title="Speech Recognition",
    page_icon="🎙️"
)

# =====================================================
# Language options
# =====================================================
LANGUAGES = {
    "English (US)": "en-US",
    "English (UK)": "en-GB",
    "French": "fr-FR",
    "Spanish": "es-ES",
    "German": "de-DE",
    "Portuguese": "pt-BR",
    "Arabic": "ar-SA",
    "Hindi": "hi-IN"
}

# =====================================================
# Transcription function
# =====================================================
def transcribe_audio(file_bytes: bytes, language: str) -> str:
    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(io.BytesIO(file_bytes)) as source:
            audio = recognizer.record(source)

        return recognizer.recognize_google(audio, language=language)

    except sr.UnknownValueError:
        return "❌ Could not understand the audio."
    except sr.RequestError as e:
        return f"❌ Google API error: {e}"
    except Exception as e:
        return f"❌ Error: {e}"

# =====================================================
# UI
# =====================================================
st.title("🎙️ Speech Recognition (Cloud-Safe)")
st.write(
    "Upload an audio file (WAV recommended) and transcribe it using "
    "Google Speech Recognition — no API key required."
)

with st.sidebar:
    st.header("⚙️ Settings")
    language_name = st.selectbox("Language", list(LANGUAGES.keys()))
    language_code = LANGUAGES[language_name]
    st.success("Fully supported on Streamlit Cloud")

# =====================================================
# File uploader
# =====================================================
uploaded_file = st.file_uploader(
    "📤 Upload an audio file",
    type=["wav", "mp3", "m4a"]
)

if uploaded_file:
    st.audio(uploaded_file)

    if st.button("📝 Transcribe"):
        with st.spinner("Transcribing..."):
            text = transcribe_audio(uploaded_file.read(), language_code)
            st.session_state["text"] = text

# =====================================================
# Output
# =====================================================
if "text" in st.session_state:
    st.subheader("📝 Transcription")
    st.text_area("Result", st.session_state["text"], height=180)

    filename = f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    st.download_button(
        "⬇️ Download transcription",
        st.session_state["text"],
        file_name=filename,
        mime="text/plain"
    )
