# Multimodal Attendance & Engagement Agent

## Overview
A small educational MVP that combines:
- **Vision indicator:** OpenCV Haar-cascade face detection on sampled video frames. It estimates visible presence; it does not identify people.
- **Audio indicator:** WAV audio-energy analysis to estimate active sound segments. It does not transcribe speech.
- **Explainable recommendations:** A transparent rule-based summary combining available indicators.

## Run locally
1. Install Python 3.10 or newer.
2. Create and activate a virtual environment.
   - Windows: `py -m venv .venv` then `.venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Start the app: `streamlit run app.py`
5. Open the local URL shown in the terminal (usually http://localhost:8501).

## Inputs
- Video: MP4, AVI, or MOV
- Audio: PCM WAV

## Limitations and responsible use
This is a prototype, not a production attendance system. It does not perform identity recognition, emotion recognition, or reliable attention measurement. A visible-face percentage and sound-energy percentage are only rough session indicators. Obtain consent for recordings, process data securely, and have an instructor verify attendance.

## Suggested future work
- Add an instructor-managed roster and consent-based identity verification.
- Improve tracking across frames and handle occlusion/lighting.
- Add audio feature extraction using a validated dataset.
- Integrate Gemini for instructor-facing summaries, with human review.
- Add tests, persistent storage, authentication, and deployment.
