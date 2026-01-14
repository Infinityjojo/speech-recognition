

# 🎙️ Enhanced Speech Recognition App (Streamlit)

Convert speech to text in your browser using multiple recognition backends, language selection, pause/resume controls, and easy export. Built with Streamlit and SpeechRecognition.

## Features

- Multiple APIs:
  - Google Speech Recognition (default)
  - Sphinx (offline, via PocketSphinx)
  - Wit.ai, Microsoft Bing, IBM (require API keys)
- Language selection (e.g., en-US, es-ES, fr-FR…)
- Pause and resume recording
- Adjustable timeout and phrase length
- Save transcription to a file
- Copy-to-clipboard helper
- Clear, friendly error messages
- Session state to keep your text across reruns

## Demo

- Start the app
- Pick API and language in the sidebar
- Click Start Recording, speak, Pause/Resume as needed
- Save or copy your text


## Requirements

Create requirements.txt with:
```
streamlit
SpeechRecognition
PyAudio
pocketsphinx
python-dotenv
```

If deploying on a service that uses runtime files (e.g., Streamlit Community Cloud), add a runtime.txt:
```
python-3.11
```

## Installation

1. Clone the repo:
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. OS notes for PyAudio/PortAudio:
- macOS: 
  - brew install portaudio
  - pip install pyaudio
- Ubuntu/Debian:
  - sudo apt-get update && sudo apt-get install -y portaudio19-dev
  - pip install pyaudio
- Windows:
  - pip install pyaudio
  - If it fails, try pipwin:
    - pip install pipwin
    - pipwin install pyaudio

4. Optional: create a .env for API keys (don’t commit this file):
```
WIT_AI_KEY=your_wit_key
BING_KEY=your_bing_key
IBM_USERNAME=your_ibm_username
IBM_PASSWORD=your_ibm_password
```

## Run

```bash
streamlit run app.py
```

Then open the URL Streamlit prints (usually http://localhost:8501).

## Configuration

- Choose API and language in the sidebar
- Set listening timeout and max phrase length
- For online APIs (Wit/Bing/IBM), ensure environment variables are set or loaded via python-dotenv

## Notes and Tips

- Offline mode: choose “Sphinx (Offline)” to use PocketSphinx without internet
- Microphone permissions: allow the browser/system to access your mic
- Pause/Resume: implemented via app session state; for long continuous dictation, consider batching phrases
- Better accuracy:
  - Reduce background noise (the app auto-calibrates briefly)
  - Speak clearly at a moderate pace
  - Use a decent microphone

## Troubleshooting

- PyAudio install issues: install PortAudio dev libs (see OS notes above)
- “API Error” or “RequestError”: check internet connectivity and API credentials
- “Could not understand audio”: try a quieter room, adjust timeouts, or speak closer to the mic

## Security

- Never commit API keys. Use environment variables or a local .env (ignored by .gitignore).

## License

MIT (or your preferred license)

## Acknowledgements

- Streamlit
- SpeechRecognition by Uberi
- PocketSphinx/Sphinx for offline recognition

Happy transcribing!