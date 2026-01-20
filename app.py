import streamlit as st
import speech_recognition as sr
from datetime import datetime
import io
from pydub import AudioSegment

# Optional: Install required packages
# pip install streamlit st-audiorec pydub

try:
    from st_audiorec import st_audiorec
except ImportError:
    st.error("Please install st-audiorec: pip install st-audiorec")
    st.stop()

# Language options (Google supports these freely)
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

def transcribe_audio_bytes(audio_bytes: bytes, language_code: str = "en-US") -> str:
    """
    Transcribe audio bytes (WAV format) using Google's free API.
    Converts WebM/Opus (from browser) to WAV if needed.
    """
    try:
        # st_audiorec returns audio in WebM (Opus) format in most browsers
        # We need to convert to WAV for speech_recognition
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="webm")
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)

        r = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language=language_code)
        return text
    except sr.UnknownValueError:
        return "❌ Could not understand audio. Please speak clearly."
    except sr.RequestError as e:
        return f"❌ Google API error: {str(e)}"
    except Exception as e:
        return f"❌ Processing error: {str(e)}"

def save_text_to_file(text, filename=None):
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transcription_{timestamp}.txt"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
        return filename, True
    except Exception as e:
        return str(e), False

def main():
    st.set_page_config(page_title="Browser Speech Recognition", page_icon="🎙️")
    st.title("🎙️ Browser-Based Speech Recognition")
    st.write("Speak into your microphone — audio is recorded in your browser and transcribed using Google's free API.")

    # Sidebar config
    with st.sidebar:
        st.header("⚙️ Settings")
        language_display = st.selectbox(
            "Language",
            options=list(LANGUAGE_OPTIONS.keys()),
            index=0
        )
        language_code = LANGUAGE_OPTIONS[language_display]
        st.info("✅ Uses Google's free speech recognition (no API key needed)")

    # Main area
    st.subheader("🎤 Record Your Voice")
    st.write("Click the button below, allow microphone access, and speak.")

    # Record audio in browser
    audio_bytes = st_audiorec()

    if audio_bytes:
        st.audio(audio_bytes, format="audio/webm")  # Playback

        if st.button("📝 Transcribe"):
            with st.spinner("Transcribing..."):
                text = transcribe_audio_bytes(audio_bytes, language_code)
                st.session_state.transcribed_text = text

    # Display result
    if "transcribed_text" in st.session_state and st.session_state.transcribed_text:
        st.subheader("📝 Transcription")
        st.text_area("Result", st.session_state.transcribed_text, height=150)

        col1, col2 = st.columns(2)
        with col1:
            filename = st.text_input("Filename", "transcription.txt")
        with col2:
            if st.button("💾 Save"):
                fname, ok = save_text_to_file(st.session_state.transcribed_text, filename)
                if ok:
                    st.success(f"Saved as {fname}")
                else:
                    st.error(fname)

        if st.button("📋 Copy Text"):
            st.code(st.session_state.transcribed_text)

if __name__ == "__main__":
    main()
