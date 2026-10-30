# Project Prerequisites

## Knowledge prerequisites
- Python fundamentals (functions, dictionaries, loops, exception handling)
- Basic computer vision and image-frame concepts
- Basic audio sampling and RMS energy concepts
- Introductory multimodal AI / agent workflow concepts
- Streamlit dashboard basics
- Git and GitHub basics

## Software and libraries used
- Python 3.10–3.13
- Streamlit: dashboard interface
- streamlit-webrtc and av: live browser camera/microphone streaming
- OpenCV: sampled-frame face detection
- NumPy: numerical and audio calculations
- Google Gen AI SDK: optional Gemini report generation
- python-dotenv: local API-key configuration

MediaPipe and Librosa are not dependencies in this delivered implementation.

## Runtime assumptions
- Local desktop/laptop execution
- Uploaded video file: MP4, AVI, or MOV
- Uploaded audio file: PCM WAV
- Internet connection for package installation and Gemini API use
- A Gemini API key is optional; the core upload analysis works without it

## Installation

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

Optional Gemini configuration: copy `.env.example` to `.env` and add `GEMINI_API_KEY`.

## Known limitations
The application supports continuous live webcam/microphone streaming through WebRTC. Face detection runs on incoming video frames. Audio is classified into speech-like/noise-like/silence using simple signal heuristics; this is not a trained classifier and may be wrong. The app does not implement verified student identity, speech transcription, temporal synchronization, or validated engagement measurement.
These must not be claimed in a project demonstration unless implemented and tested separately.
