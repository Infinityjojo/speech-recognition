import streamlit as st
import speech_recognition as sr
from datetime import datetime
import io
import os
from pydub import AudioSegment

# =========================================================
# MUST be first Streamlit call
# =========================================================
st.set_page_config(page_title="Browser Speech Recognition", page_icon="🎙️")

# =========================================================
# Optional dependency (browser recording)
# =========================================================
try:
    from st_audiorec import st_audiorec
except ImportError:
    st.error("❌ Missing dependency: st-audiorec")
    st.stop()

# =========================================================
# Language options
# =========================================================
LANGUAGE_OPTIONS = {
    "English (US)": "en-US",
    "English (UK)": "en-GB",
    "Spanish": "es-ES",
    "French": "fr-FR",
    "German": "de-DE",
    "Italian": "it-IT",
    "Portuguese": "pt-BR",
    "Chinese (Mandarin)": "zh-CN",
    "Japanese": "ja-JP",
    "Korean": "ko-KR",
    "Hindi": "hi-IN",
    "Arabic": "ar-SA",
    "Russian": "ru-RU"
}

# =========================================================
# Audio transcription
# =========================================================
def transcribe_audio_bytes(audio_bytes: bytes, language_code: str) -> str:
    try:
        audio = AudioSegment.from_file(
            io.BytesIO(audio_bytes),
            format="webm"
        )

        wav_buffer = io.BytesIO()
        audio.export(wav_buffer, format="wav")
        wav_buffer.seek(0)

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_buffer) as source:
            audio_data = recognizer.record(source)

        return recognizer.recognize_google(
            audio_data,
            language=language_code
        )

    except sr.UnknownValueError:
        return "❌ Speech not clear enough."
    except sr.RequestError as e:
        return f"❌ Google Speech API error: {e}"
    except Exception as e:
        return f"❌ Audio processing failed: {e}"

# =========================================================
# App UI
# =========================================================
st.title("🎙️ Browser-Based Speech Recognition")
st.write(
    "Record audio directly in your browser and transcribe it "
    "using Google's free speech recognition (no API key)."
)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    lang_label = st.selectbox(
        "Language",
        list(LANGUAGE_OPTIONS.keys())
    )
    language_code = LANGUAGE_OPTIONS[lang_label]
    st.success("No API key required")

# Recorder
st.subheader("🎤 Record")
audio_bytes = st_audiorec()

if audio_bytes:
    st.audio(audio_bytes, format="audio/webm")

    if st.button("📝 Transcribe"):
        with st.spinner("Transcribing..."):
            text = transcribe_audio_bytes(audio_bytes, language_code)
            st.session_state["text"] = text

# Output
if "text" in st.session_state:
    st.subheader("📝 Transcription")
    st.text_area("Result", st.session_state["text"], height=180)

    # Save to temp folder (Cloud-safe)
    filename = f"/tmp/transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    if st.button("💾 Save"):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(st.session_state["text"])

        with open(filename, "rb") as f:
            st.download_button(
                label="⬇️ Download transcription",
                data=f,
                file_name=os.path.basename(filename),
                mime="text/plain"
            )
