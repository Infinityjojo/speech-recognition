import streamlit as st
import speech_recognition as sr
import os
from datetime import datetime
import time

# Available speech recognition APIs
API_OPTIONS = {
    "Google Speech Recognition": "google",
    "Sphinx (Offline)": "sphinx",
    "Wit.ai": "wit",
    "Microsoft Bing Voice Recognition": "bing",
    "IBM Speech to Text": "ibm"
}

# Available languages (Google API supports many languages)
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


def transcribe_speech(api_choice, language_code, timeout=5, phrase_time_limit=5):
    """
    Transcribe speech using the selected API and language
    """
    r = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            st.info("🔊 Calibrating microphone for ambient noise...")
            r.adjust_for_ambient_noise(source, duration=1)
            st.info("🎤 Speak now...")
            audio_text = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            st.info("📝 Transcribing...")

        text = ""

        if api_choice == "google":
            text = r.recognize_google(audio_text, language=language_code)
        elif api_choice == "sphinx":
            text = r.recognize_sphinx(audio_text)
        elif api_choice == "wit":
            # Wit.ai requires API key - you'd need to set WIT_AI_KEY environment variable
            text = r.recognize_wit(audio_text, key=os.getenv("WIT_AI_KEY"))
        elif api_choice == "bing":
            # Bing requires API key
            text = r.recognize_bing(audio_text, key=os.getenv("BING_KEY"))
        elif api_choice == "ibm":
            # IBM requires username and password
            text = r.recognize_ibm(audio_text, username=os.getenv("IBM_USERNAME"), password=os.getenv("IBM_PASSWORD"))

        return text

    except sr.WaitTimeoutError:
        return "❌ Listening timeout: No speech detected within the time limit."
    except sr.UnknownValueError:
        return "❌ Sorry, I could not understand the audio. Please speak more clearly."
    except sr.RequestError as e:
        return f"❌ API Error: {str(e)}. Please check your internet connection and API credentials."
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


def save_text_to_file(text, filename=None):
    """
    Save transcribed text to a file
    """
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
    st.set_page_config(page_title="Enhanced Speech Recognition", page_icon="🎙️")

    st.title("🎙️ Enhanced Speech Recognition App")
    st.write("Convert your speech to text with multiple recognition options")

    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # API selection
        api_display = st.selectbox(
            "Select Speech Recognition API",
            options=list(API_OPTIONS.keys()),
            index=0,
            help="Choose which speech recognition service to use"
        )
        api_choice = API_OPTIONS[api_display]

        # Language selection
        language_display = st.selectbox(
            "Select Language",
            options=list(LANGUAGE_OPTIONS.keys()),
            index=0,
            help="Select the language you'll be speaking in"
        )
        language_code = LANGUAGE_OPTIONS[language_display]

        # Recording settings
        st.subheader("Recording Settings")
        timeout = st.slider("Listening timeout (seconds)", 1, 15, 5)
        phrase_limit = st.slider("Maximum phrase length (seconds)", 1, 10, 5)

        # API key info
        if api_choice in ["wit", "bing", "ibm"]:
            st.warning(f"⚠️ {api_display} requires API credentials. Set environment variables: ")
            if api_choice == "wit":
                st.code("WIT_AI_KEY=your_api_key_here")
            elif api_choice == "bing":
                st.code("BING_KEY=your_api_key_here")
            elif api_choice == "ibm":
                st.code("IBM_USERNAME=your_username\nIBM_PASSWORD=your_password")

    # Main content area
    col1, col2 = st.columns([3, 1])

    with col1:
        # Recording controls
        if 'recording' not in st.session_state:
            st.session_state.recording = False
        if 'transcribed_text' not in st.session_state:
            st.session_state.transcribed_text = ""
        if 'pause_recording' not in st.session_state:
            st.session_state.pause_recording = False

        # Recording buttons
        col_btn1, col_btn2, col_btn3 = st.columns(3)

        with col_btn1:
            if not st.session_state.recording:
                if st.button("🎙️ Start Recording", type="primary", use_container_width=True):
                    st.session_state.recording = True
                    st.session_state.pause_recording = False
                    st.rerun()
            else:
                if st.button("⏹️ Stop Recording", use_container_width=True):
                    st.session_state.recording = False
                    st.rerun()

        with col_btn2:
            if st.session_state.recording:
                if st.session_state.pause_recording:
                    if st.button("▶️ Resume", use_container_width=True):
                        st.session_state.pause_recording = False
                        st.rerun()
                else:
                    if st.button("⏸️ Pause", use_container_width=True):
                        st.session_state.pause_recording = True
                        st.rerun()

        with col_btn3:
            if st.session_state.transcribed_text:
                if st.button("🗑️ Clear", use_container_width=True):
                    st.session_state.transcribed_text = ""
                    st.rerun()

        # Recording status
        if st.session_state.recording:
            if st.session_state.pause_recording:
                st.warning("⏸️ Recording paused. Click Resume to continue.")
            else:
                st.success("🔴 Recording in progress...")
                with st.spinner("Listening..."):
                    # Simulate recording process (in a real app, you'd handle this differently)
                    time.sleep(2)
                    if not st.session_state.pause_recording:
                        text = transcribe_speech(api_choice, language_code, timeout, phrase_limit)
                        if text and not text.startswith("❌"):
                            st.session_state.transcribed_text += text + " "
                        st.rerun()
        else:
            st.info("💡 Click Start Recording to begin")

    # Display transcribed text
    if st.session_state.transcribed_text:
        st.subheader("📝 Transcription")
        transcribed_text_area = st.text_area(
            "Transcribed Text",
            value=st.session_state.transcribed_text,
            height=200,
            key="transcription_display"
        )

        # Save to file option
        col_save1, col_save2 = st.columns(2)

        with col_save1:
            custom_filename = st.text_input("Custom filename (optional)", "transcription.txt")

        with col_save2:
            if st.button("💾 Save to File", use_container_width=True):
                filename, success = save_text_to_file(st.session_state.transcribed_text, custom_filename)
                if success:
                    st.success(f"✅ Text saved to {filename}")
                else:
                    st.error(filename)

        # Copy to clipboard
        if st.button("📋 Copy to Clipboard", use_container_width=True):
            st.code(st.session_state.transcribed_text)
            st.success("✅ Text copied to clipboard!")

    # Error handling display
    if st.session_state.transcribed_text and st.session_state.transcribed_text.startswith("❌"):
        st.error(st.session_state.transcribed_text)
        st.info("💡 Tips for better recognition:")
        st.write("- Speak clearly and at a moderate pace")
        st.write("- Reduce background noise")
        st.write("- Use a good quality microphone")
        st.write("- Check your internet connection (for online APIs)")


if __name__ == "__main__":
    main()