# Multimodal Attendance & Engagement Agent

A classroom-session analysis prototype that combines video face-presence indicators, WAV audio-energy indicators, simple multimodal fusion, rule-based teaching suggestions, session analytics, and an optional Gemini-generated report.

## Project Overview

The Multimodal Attendance & Engagement Agent is designed to demonstrate classroom activity monitoring using computer vision and audio signal processing.

It processes live or uploaded video and audio inputs to generate presence estimates, audio activity indicators, experimental engagement-related metrics, teaching suggestions, and session analytics.

## Key Features

- **Live Webcam Processing:** Captures and processes live video through WebRTC.
- **Face Detection:** Detects visible faces using OpenCV Haar cascades.
- **Presence-Based Attendance:** Estimates presence using frames in which faces are detected.
- **Video Upload:** Supports MP4, AVI, and MOV video files.
- **Live Microphone Processing:** Captures audio through the browser microphone using WebRTC.
- **Audio Upload:** Supports WAV audio files.
- **Audio Activity Analysis:** Estimates speech-like, noise-like, and silence segments using RMS, zero-crossing rate, and spectral centroid.
- **Multimodal Fusion:** Combines available video-presence and audio-activity percentages.
- **Engagement Estimation:** Generates an experimental activity indicator.
- **Teaching Suggestions:** Provides rule-based teaching suggestions.
- **Session Analytics:** Displays session-level activity metrics and analysis.
- **Optional Gemini Report:** Supports AI-assisted report generation when a valid Gemini API key is configured.

## Important Scope and Limitations

- Face detection is not identity recognition.
- Temporary face labels, if displayed, are rough frame-to-frame proximity matches and are not reliable student identities.
- Attendance is an estimate based on face-detected video frames, not verified attendance.
- Live audio speech-like/noise-like labels use lightweight signal heuristics, not a trained speech/noise classifier.
- Audio labels may mistake music, classroom noise, or other sounds for speech.
- The combined value is an experimental activity indicator, not a validated engagement score.
- Engagement metrics do not establish actual attention, emotion, or learning.
- Results may vary depending on lighting, camera quality, microphone quality, background noise, and input conditions.
- Obtain consent before capturing classroom video or audio and have an instructor verify attendance.

## Technology Stack

- Python
- Streamlit
- Streamlit WebRTC
- OpenCV
- NumPy
- PyAV
- Google GenAI SDK (optional)
- Python Dotenv

## Requirements

- Windows 10/11, macOS, or Linux
- Python 3.10–3.13 (64-bit recommended)
- Webcam and microphone for live input
- Internet connection for package installation
- Gemini API key only for optional Gemini reports

## Project Structure

```text
Multimodal_Attendance_Engagement_Agent_Final/
├── app.py
├── analysis_core.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── PREREQUISITES.md
├── RUN_PROJECT.bat
├── WEBRTC_NOTES.md
├── IMPLEMENTATION_STATUS.md
└── VALIDATION_REPORT.md
```

## Windows Setup (PowerShell)

Open PowerShell in the project directory.

### 1. Create a Virtual Environment

```powershell
py -3.13 -m venv .venv
```

### 2. Activate the Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If activation is blocked by PowerShell, use the environment's Python executable directly in the following commands.

### 3. Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### 4. Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### 5. Configure Optional Gemini Integration

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

Open `.env` and add your own Gemini API key:

```env
GEMINI_API_KEY=your_real_api_key
```

The Gemini integration is optional. Core application features can be used without configuring it.

**Never upload `.env` or expose your API key publicly.**

### 6. Run the Application

```powershell
streamlit run app.py
```

Alternatively, if the virtual environment is not activated:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local address displayed in the terminal, usually:

```text
http://localhost:8501
```

## macOS / Linux Setup

### 1. Create a Virtual Environment

```bash
python3 -m venv .venv
```

### 2. Activate the Environment

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure Optional Gemini Integration

```bash
cp .env.example .env
```

Add your Gemini API key to `.env` if you want to use the optional report feature.

### 5. Run the Application

```bash
streamlit run app.py
```

## Supported Inputs

### Video

- MP4
- AVI
- MOV

OpenCV must be able to decode the video codec. If a video cannot be opened, try exporting it as MP4 (H.264) or AVI.

### Audio

- WAV containing uncompressed PCM samples.
- Supported sample formats depend on the application's audio-processing implementation.

## Project Workflow

1. Start Live Classroom Mode and grant browser camera and microphone permissions, or upload a classroom video and WAV audio recording.
2. The vision module samples video frames and detects visible faces using OpenCV Haar cascades.
3. The live audio module estimates speech-like, noise-like, and silent segments using signal features.
4. Uploaded WAV analysis calculates audio energy and active/silent segments.
5. The multimodal agent collects the available video and audio features.
6. The fusion function combines the available video-presence and audio-activity percentages.
7. Rule-based teaching suggestions and session analytics are generated.
8. Optionally request a Gemini-generated report when API access is configured.

## Live Metrics Refresh

Live counters are stored on the active WebRTC processor instances so that they persist across Streamlit reruns.

Use the **Refresh Metrics** option to read the latest counters without resetting the active processors.

## Running the Project

The application can be launched using:

```bash
streamlit run app.py
```

For additional setup information, see `PREREQUISITES.md` and `WEBRTC_NOTES.md`.

## Project Purpose

This project demonstrates the practical integration of computer vision, audio signal processing, and multimodal analysis for a classroom monitoring use case.

It is an educational prototype intended for experimentation, demonstration, and further development.

## Author

**Jayant Prasad**

B.Tech – Computer Science & Engineering

