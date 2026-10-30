# Multimodal Attendance & Engagement Agent

An AI-powered classroom analytics prototype that combines computer vision, audio activity analysis, and Generative AI to provide classroom session insights.

## Overview

The Multimodal Attendance & Engagement Agent is an educational analytics application designed to analyze classroom video and audio recordings.

It uses OpenCV for visible face presence detection, audio signal energy analysis for estimating active sound segments, and Google's Gemini API to generate an AI-powered classroom analytics report.

The application provides experimental indicators and teaching improvement suggestions through an interactive Streamlit dashboard.

## Key Features

### 1. Vision Analysis
- Uses OpenCV Haar Cascade face detection.
- Processes sampled frames from uploaded classroom videos.
- Estimates visible face presence.
- Calculates average detected faces per sampled frame.

### 2. Audio Analysis
- Accepts PCM WAV audio recordings.
- Analyzes audio signal energy.
- Estimates the percentage of active audio segments.
- Provides a basic audio activity indicator.

### 3. Combined Activity Indicator
- Combines available video and audio indicators.
- Generates an experimental session activity score.
- Provides a basic overview of classroom activity.

### 4. Gemini AI-Powered Analysis
- Integrates Google's Gemini API.
- Generates structured classroom analytics reports.
- Provides key observations and possible classroom interpretations.
- Suggests practical teaching improvements.
- Highlights limitations of the available data.

### 5. Interactive Dashboard
- Built using Streamlit.
- Supports video and audio uploads.
- Displays analysis results.
- Allows users to view and download AI-generated reports.

## Technologies Used

- Python
- Streamlit
- OpenCV
- NumPy
- Google Gemini API
- Google GenAI SDK
- Python-dotenv

## Project Workflow

1. Upload a classroom video in MP4, AVI, or MOV format.
2. Upload an audio recording in PCM WAV format.
3. Analyze video frames to estimate visible face presence.
4. Analyze audio energy to estimate active sound segments.
5. Calculate an experimental combined activity indicator.
6. Send the analysis metrics to Gemini AI.
7. Generate a structured classroom analytics report.
8. View and download the generated report.

## Installation and Setup

### Prerequisites
- Python 3.10 or newer
- Git
- Gemini API key

### 1. Clone the Repository

```bash
git clone https://github.com/jayant07prasad/multimodal-attendance-engagement-agent.git
cd multimodal-attendance-engagement-agent
```

### 2. Create a Virtual Environment

**Windows:**

```bash
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install google-genai python-dotenv
```

### 4. Configure Gemini API Key

Create a file named `.env` in the project root directory.

Add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with your actual API key.

**Important:** Never upload your `.env` file or API key to GitHub.

### 5. Run the Application

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal, usually:

`http://localhost:8501`

## Supported Input Formats

| Input | Supported Formats |
|---|---|
| Video | MP4, AVI, MOV |
| Audio | PCM WAV |

## Privacy and Responsible Use

This application is an experimental prototype, not a production attendance system.

- It does not identify students or perform identity recognition.
- It does not detect or infer emotions.
- Visible face presence does not prove that someone is paying attention.
- Audio energy does not necessarily represent meaningful speech.
- The combined activity indicator is not a scientifically validated engagement score.
- Video and audio recordings with different durations may not represent the same observation period.

Recordings should only be processed with appropriate consent and handled securely. AI-generated observations should be reviewed by an instructor before being used for decisions.

## Future Improvements

- Real-time classroom analytics.
- Improved video and audio synchronization.
- Advanced speech activity analysis.
- Instructor-managed session history.
- Better visualization of classroom activity trends.
- Authentication and secure data storage.
- Deployment for wider accessibility.

## Author

**Jayant Prasad**

Computer Science Engineering Student

GitHub: [@jayant07prasad](https://github.com/jayant07prasad)

## Project Status

**Current Status:** Working Prototype

The project includes video analysis, audio activity estimation, Gemini AI-powered report generation, and report download functionality.
