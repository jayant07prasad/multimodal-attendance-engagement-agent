# Multimodal Attendance & Engagement Agent

A classroom-session analysis prototype that combines video face-presence indicators,
WAV audio-energy indicators, simple multimodal fusion, rule-based teaching suggestions,
session analytics, and an optional Gemini-generated report.

## Important scope and limitations

- Live webcam and microphone capture are available through WebRTC in the Live Classroom Mode.
- Uploaded video (MP4, AVI, MOV) and WAV analysis remain available as an alternative.
- Live audio speech-like/noise-like labels use lightweight signal heuristics (RMS, zero-crossing
  rate and spectral centroid), not a trained speech/noise classifier.
- Face detection is not identity recognition. Temporary face labels are rough frame-to-frame
  proximity matches and are not reliable student identities.
- Live speech/noise classification is heuristic and can mistake music, classroom noise, or other sounds for speech.
- The combined value is an experimental activity indicator, **not a validated engagement score**.
- Do not use the output as proof of attendance, attention, emotion, or learning. Obtain consent
  and have an instructor verify attendance.

## Requirements

- Windows 10/11, macOS, or Linux
- Python 3.10–3.13 (64-bit recommended)
- Internet only for installing packages and optional Gemini reports
- For Gemini reports, a Gemini API key

## Windows setup (PowerShell)

Open PowerShell in this project folder and run:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and replace the placeholder with your own key:

```env
GEMINI_API_KEY=your_real_api_key
```

Never upload `.env` or share your API key on GitHub.

Run:

```powershell
streamlit run app.py
```

Open the local address printed in the terminal (usually http://localhost:8501).

## macOS / Linux setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

## Inputs

- Video: MP4 / AVI / MOV. OpenCV must be able to decode the codec.
- Audio: WAV containing uncompressed PCM samples (8-bit, 16-bit, or 32-bit).

If a video cannot be opened, try exporting it as MP4 (H.264) or AVI. Some phone recordings
use codecs that the local OpenCV build cannot decode.

## Project workflow

1. Start Live Classroom Mode and grant browser camera/microphone permission, or upload a classroom video and/or WAV audio recording.
2. The vision module samples frames and detects visible faces using OpenCV Haar cascades.
3. The live audio module estimates speech-like/noise-like/silent segments using simple signal features; uploaded WAV analysis calculates RMS energy and active/silent segments.
4. The multimodal agent collects available features.
5. The fusion function averages the available video-presence and audio-activity percentages.
6. Rule-based suggestions and session summary are displayed.
7. Optionally request a Gemini report and download it as text.

## Tests

Run the lightweight analysis tests:

```powershell
python -m unittest discover -s tests -v
```

## Folder structure

```text
Multimodal_Attendance_Engagement_Agent_Final/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── PREREQUISITES.md
├── RUN_PROJECT.bat
└── tests/
    └── test_analysis.py
```


## Live metrics refresh

The live counters are stored on the active WebRTC processor instances so they persist across Streamlit reruns. Use **Refresh metrics** to read the latest values without resetting the active processors.
