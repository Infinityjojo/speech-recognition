import streamlit as st
import speech_recognition as sr
import io
from datetime import datetime

# =====================================================
# MUST be first Streamlit call
# =====================================================
st.set_page_config(
    page_title="Voice Transcription",
    page_icon="🎙️"
)

# =====================================================
# Import browser recorder
# =====================================================
try:
    from st_audiorec import st_audiorec
except Exception:
    st.error("st-audiorec is not installed")
    st.stop()

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
# Transcription function (NO conversion)
# =====================================================
def transcribe_wav_bytes(wav_bytes: bytes, language: str) -> str:
    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(io.BytesIO(wav_bytes)) as source:
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
st.title("🎙️ Browser Voice Transcription")
st.write(
    "Record your voice in the browser and transcribe it using "
    "Google Speech Recognition (no API key required)."
)

with st.sidebar:
    st.header("⚙️ Settings")
    language_name = st.selectbox("Language", list(LANGUAGES.keys()))
    language_code = LANGUAGES[language_name]
    st.success("Cloud-safe mode enabled")

st.subheader("🎤 Record")
audio_bytes = st_audiorec()

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")

    if st.button("📝 Transcribe"):
        with st.spinner("Transcribing..."):
            text = transcribe_wav_bytes(audio_bytes, language_code)
            st.session_state["text"] = text

if "text" in st.session_state:
    st.subheader("📝 Transcription")
    st.text_area("Result", st.session_state["text"], height=180)

    filename = f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    st.download_button(
        "⬇️ Download text",
        st.session_state["text"],
        file_name=filename,
        mime="text/plain"
    )
