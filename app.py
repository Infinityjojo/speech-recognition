import streamlit as st
import speech_recognition as sr
import os
from datetime import datetime
import time
import threading
from streamlit.runtime.scriptrunner import add_script_run_ctx

# Restrict to only Google's free Speech Recognition API
API_OPTIONS = {
    "Google Speech Recognition (Free)": "google"
}

# Supported languages for Google API
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

def init_session_state():
    """Initialize session state variables for recording and transcription"""
    if 'recognizer' not in st.session_state:
        try:
            st.session_state.recognizer = sr.Recognizer()
            st.session_state.microphone = sr.Microphone()
        except OSError:
            st.session_state.microphone_error = "No microphone detected. Please connect a microphone and refresh the page."
            return
    
    if 'recording' not in st.session_state:
        st.session_state.recording = False
    if 'pause_recording' not in st.session_state:
        st.session_state.pause_recording = False
    if 'transcribed_text' not in st.session_state:
        st.session_state.transcribed_text = ""
    if 'listening_thread' not in st.session_state:
        st.session_state.listening_thread = None
    if 'error_msg' not in st.session_state:
        st.session_state.error_msg = ""

def listen_continuous(language_code, timeout, phrase_limit):
    """Continuous listening function to run in background thread"""
    recognizer = st.session_state.recognizer
    microphone = st.session_state.microphone

    # Calibrate for ambient noise once at start
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
    
    while st.session_state.recording:
        # Skip if paused
        if st.session_state.pause_recording:
            time.sleep(0.5)
            continue
        
        try:
            with microphone as source:
                audio = recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_limit
                )
            
            # Transcribe using Google Speech Recognition
            text = recognizer.recognize_google(audio, language=language_code)
            if text:
                st.session_state.transcribed_text += text + " "
        
        except sr.WaitTimeoutError:
            # No speech detected in timeout window, keep listening
            continue
        except sr.UnknownValueError:
            st.session_state.transcribed_text += "[Unintelligible] "
        except sr.RequestError as e:
            st.session_state.error_msg = f"Google API Error: {str(e)}. Check your internet connection."
            st.session_state.recording = False
            break
        except Exception as e:
            st.session_state.error_msg = f"Unexpected error: {str(e)}"
            st.session_state.recording = False
            break
        
        time.sleep(0.1)  # Reduce CPU usage

def save_text_to_file(text, filename=None):
    """Save transcribed text to a UTF-8 encoded file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transcription_{timestamp}.txt"

    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(text)
        return filename, True
    except Exception as e:
        return f"Error saving file: {str(e)}", False

def main():
    st.set_page_config(page_title="Google Speech Transcriber", page_icon="🎙️")
    st.title("🎙️ Google Free Speech Transcriber")
    st.write("Convert speech to text using Google's free Speech Recognition API")

    # Initialize session state
    init_session_state()

    # Handle microphone error
    if 'microphone_error' in st.session_state:
        st.error(st.session_state.microphone_error)
        return

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Language selection
        language_display = st.selectbox(
            "Select Language",
            options=list(LANGUAGE_OPTIONS.keys()),
            index=0,
            help="Choose the language you will speak in"
        )
        language_code = LANGUAGE_OPTIONS[language_display]

        # Recording parameters
        st.subheader("Recording Parameters")
        timeout = st.slider("Listening Timeout (seconds)", 1, 10, 3)
        phrase_limit = st.slider("Max Phrase Length (seconds)", 1, 15, 5)

    # Main content area
    col1, col2 = st.columns([3,1])

    with col1:
        # Recording control buttons
        col_btn1, col_btn2, col_btn3 = st.columns(3)

        with col_btn1:
            if not st.session_state.recording:
                if st.button("🎙️ Start Recording", type="primary", use_container_width=True):
                    st.session_state.recording = True
                    st.session_state.error_msg = ""
                    # Start background listening thread
                    listen_thread = threading.Thread(
                        target=listen_continuous,
                        args=(language_code, timeout, phrase_limit),
                        daemon=True
                    )
                    add_script_run_ctx(listen_thread)
                    st.session_state.listening_thread = listen_thread
                    listen_thread.start()
            else:
                if st.button("⏹️ Stop Recording", use_container_width=True):
                    st.session_state.recording = False
                    st.session_state.pause_recording = False

        with col_btn2:
            if st.session_state.recording:
                if st.session_state.pause_recording:
                    if st.button("▶️ Resume", use_container_width=True):
                        st.session_state.pause_recording = False
                else:
                    if st.button("⏸️ Pause", use_container_width=True):
                        st.session_state.pause_recording = True

        with col_btn3:
            if st.session_state.transcribed_text:
                if st.button("🗑️ Clear Text", use_container_width=True):
                    st.session_state.transcribed_text = ""
                    st.session_state.error_msg = ""

        # Display recording status
        if st.session_state.recording:
            if st.session_state.pause_recording:
                st.warning("⏸️ Recording paused. Click Resume to continue.")
            else:
                st.success("🔴 Recording in progress... Speak clearly into your microphone.")
        
        # Display error messages
        if st.session_state.error_msg:
            st.error(st.session_state.error_msg)

    # Display transcribed text
    if st.session_state.transcribed_text:
        st.subheader("📝 Transcription")
        text_area = st.text_area(
            "Transcribed Text",
            value=st.session_state.transcribed_text,
            height=250,
            key="transcription_display"
        )

        # Save and copy options
        col_save, col_copy = st.columns(2)
        
        with col_save:
            custom_filename = st.text_input("Custom Filename", f"transcription_{datetime.now().strftime('%Y%m%d')}.txt")
            if st.button("💾 Save to File", use_container_width=True):
                filename, success = save_text_to_file(st.session_state.transcribed_text, custom_filename)
                if success:
                    st.success(f"✅ Saved to {os.path.abspath(filename)}")
                else:
                    st.error(filename)
        
        with col_copy:
            if st.button("📋 Copy to Clipboard", use_container_width=True):
                st.code(st.session_state.transcribed_text)
                st.success("✅ Text copied to clipboard!")

    # Tips section
    with st.expander("💡 Tips for Better Transcription"):
        st.write("- Use a high-quality microphone (headset mics work best)")
        st.write("- Speak clearly at a moderate pace")
        st.write("- Reduce background noise (close windows, turn off fans)")
        st.write("- Ensure stable internet connection (required for Google API)")
        st.write("- Speak in complete phrases for better accuracy")

if __name__ == "__main__":
    main()
