
import streamlit as st
import cv2
import numpy as np
import wave
import io
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

st.set_page_config(
    page_title="Multimodal Attendance & Engagement Agent",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Multimodal Attendance & Engagement Agent")
st.caption(
    "AI-powered classroom analysis using video presence indicators, "
    "audio activity indicators and Gemini AI."
)

st.info(
    "Prototype notice: This demo estimates visible face presence and "
    "audio activity. It does not identify students, infer emotions, "
    "or prove that someone is paying attention."
)


# ---------------- VIDEO ANALYSIS ----------------

def analyze_video(video_bytes):
    temp_path = "uploaded_video.mp4"

    with open(temp_path, "wb") as f:
        f.write(video_bytes)

    cap = cv2.VideoCapture(temp_path)

    if not cap.isOpened():
        return None

    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = frame_count / fps if fps else 0

    cascade_path = (
        cv2.data.haarcascades
        + "haarcascade_frontalface_default.xml"
    )

    face_cascade = cv2.CascadeClassifier(cascade_path)

    sampled = 0
    face_frames = 0
    face_counts = []
    preview = None

    while True:
        ok, frame = cap.read()

        if not ok:
            break

        if sampled % max(int(fps), 1) == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            face_counts.append(len(faces))

            if len(faces) > 0:
                face_frames += 1

            if preview is None:
                preview = cv2.cvtColor(
                    frame, cv2.COLOR_BGR2RGB
                )

        sampled += 1

    cap.release()

    seconds_sampled = len(face_counts)

    presence = (
        face_frames / seconds_sampled * 100
        if seconds_sampled else 0
    )

    return {
        "duration": duration,
        "samples": seconds_sampled,
        "presence": presence,
        "avg_faces": float(np.mean(face_counts))
        if face_counts else 0,
        "preview": preview
    }


# ---------------- AUDIO ANALYSIS ----------------

def analyze_wav(audio_bytes):
    try:
        with wave.open(io.BytesIO(audio_bytes), "rb") as wf:
            rate = wf.getframerate()
            channels = wf.getnchannels()
            width = wf.getsampwidth()
            frames = wf.readframes(wf.getnframes())

        dtype = {
            1: np.uint8,
            2: np.int16,
            4: np.int32
        }.get(width)

        if dtype is None:
            return None

        audio = np.frombuffer(
            frames, dtype=dtype
        ).astype(np.float64)

        if channels > 1:
            audio = audio.reshape(-1, channels).mean(axis=1)

        if width == 1:
            audio = audio - 128

        duration = len(audio) / rate if rate else 0

        chunk = max(int(rate * 1), 1)
        rms = []

        for start in range(0, len(audio), chunk):
            part = audio[start:start + chunk]

            if len(part):
                rms.append(
                    float(np.sqrt(np.mean(part ** 2)))
                )

        threshold = max(
            (np.percentile(rms, 35) * 1.8 if rms else 0),
            100
        )

        active = sum(v > threshold for v in rms)

        activity = (
            active / len(rms) * 100 if rms else 0
        )

        return {
            "duration": duration,
            "activity": activity,
            "segments": len(rms)
        }

    except Exception:
        return None


# ---------------- GEMINI AI ANALYSIS ----------------


def generate_gemini_analysis(
    vision_score,
    audio_score,
    combined_score,
    video_result,
    audio_result
):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return "API key not found. Please check your .env file."

    client = genai.Client(api_key=api_key)

    video_details = (
        f"Video duration: {video_result['duration']:.1f} seconds. "
        f"Visible face presence: {vision_score:.1f}%. "
        f"Average detected faces per sampled frame: "
        f"{video_result['avg_faces']:.2f}."
        if video_result else "Video was not uploaded."
    )

    audio_details = (
        f"Audio duration: {audio_result['duration']:.1f} seconds. "
        f"Audio energy activity: {audio_score:.1f}%."
        if audio_result else "Audio was not uploaded."
    )

    prompt = f"""
You are an educational classroom analytics assistant.

VIDEO DATA:
{video_details}

AUDIO DATA:
{audio_details}

Combined session activity indicator: {combined_score:.1f}/100.

Write a professional report with:
1. Session Overview
2. Key Observations
3. Possible Classroom Interpretation
4. Teaching Improvement Suggestions
5. Limitations of This Analysis

Give useful explanations and practical suggestions.
Use clear professional language suitable for a college project.
Do not claim face presence proves attention.
Audio energy does not prove meaningful speech.
Do not identify people or infer emotions.
Mention that the combined score is an experimental prototype indicator,
not a scientifically validated engagement score.
"""

    models = ["gemini-3.8-flash", "gemini-flash-latest"]
    last_error = None

    for model_name in models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={
                    "max_output_tokens": 2500,
                    "temperature": 0.3
                }
            )

            if response and response.text:
                return response.text

        except Exception as e:
            last_error = e

    raise Exception(f"Gemini models unavailable: {last_error}")
# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.header("Upload session files")

    video_file = st.file_uploader(
        "Classroom video (MP4/AVI/MOV)",
        type=["mp4", "avi", "mov"]
    )

    audio_file = st.file_uploader(
        "Classroom audio (WAV)",
        type=["wav"]
    )

    st.caption(
        "Use consented sample recordings. "
        "Video is processed locally by this app."
    )


# ---------------- DASHBOARD ----------------

left, right = st.columns(2)

video_result = None
audio_result = None

with left:
    st.subheader("📹 Vision Module")

    if video_file:
        with st.spinner("Analyzing video..."):
            video_result = analyze_video(
                video_file.getvalue()
            )

        if video_result:
            st.metric(
                "Visible-presence indicator",
                f"{video_result['presence']:.1f}%"
            )

            st.metric(
                "Average faces per sampled frame",
                f"{video_result['avg_faces']:.2f}"
            )

            st.caption(
                f"Video duration: "
                f"{video_result['duration']:.1f} seconds"
            )

            if video_result["preview"] is not None:
                st.image(
                    video_result["preview"],
                    caption="First sampled frame",
                    use_container_width=True
                )
        else:
            st.error("Could not read this video.")

    else:
        st.write("Upload a video to estimate visible face presence.")


with right:
    st.subheader("🔊 Audio Module")

    if audio_file:
        with st.spinner("Analyzing audio..."):
            audio_result = analyze_wav(
                audio_file.getvalue()
            )

        if audio_result:
            st.metric(
                "Audio activity indicator",
                f"{audio_result['activity']:.1f}%"
            )

            st.caption(
                f"Audio duration: "
                f"{audio_result['duration']:.1f} seconds"
            )

            st.caption(
                "Measures sound energy only, "
                "not speech meaning or speaker identity."
            )

        else:
            st.error("Could not read this WAV file.")

    else:
        st.write("Upload a WAV file to estimate audio activity.")


# ---------------- COMBINED SUMMARY ----------------

st.divider()
st.subheader("🧠 Explainable Engagement Summary")

if video_result or audio_result:

    vision_score = (
        video_result["presence"] if video_result else 0
    )

    audio_score = (
        audio_result["activity"] if audio_result else 0
    )

    available = (
        (1 if video_result else 0)
        + (1 if audio_result else 0)
    )

    score = (
        (vision_score if video_result else 0)
        + (audio_score if audio_result else 0)
    ) / available

    st.metric(
        "Combined session activity indicator",
        f"{score:.1f}/100"
    )

    if video_result:
        st.write(
            f"• Visible faces detected in "
            f"{vision_score:.1f}% of sampled video frames."
        )

    if audio_result:
        st.write(
            f"• Audio energy exceeded the activity threshold "
            f"in {audio_score:.1f}% of one-second segments."
        )

    if score < 30:
        recommendation = (
            "Review recording quality and consider adding "
            "an interactive question or short discussion."
        )

    elif score < 65:
        recommendation = (
            "Consider a short knowledge check, discussion prompt, "
            "or change of teaching pace."
        )

    else:
        recommendation = (
            "Continue using periodic checks for understanding. "
            "Activity alone does not confirm learning."
        )

    st.success("Basic Teaching Suggestion: " + recommendation)

    # ---------------- GEMINI BUTTON ----------------

    st.divider()
    st.subheader("✨ Gemini AI-Powered Classroom Insights")

    st.write(
        "Generate a detailed AI analysis using the "
        "video and audio indicators."
    )

    if st.button(
        "🚀 Generate AI Analysis with Gemini",
        type="primary",
        use_container_width=True
    ):

        try:
            with st.spinner(
                "Gemini AI is analyzing your session data..."
            ):
                ai_result = generate_gemini_analysis(
                    vision_score,
                    audio_score,
                    score,
                    video_result,
                    audio_result
                )

            if ai_result.startswith("API key not found"):
                st.error(ai_result)
            else:
                st.success("Gemini AI analysis generated!")
                st.markdown(ai_result)
                st.download_button(
    label="📥 Download AI Report",
    data=ai_result,
    file_name="classroom_ai_report.txt",
    mime="text/plain"
)

        except Exception as e:
            st.error(
                "Gemini AI error. Please check your API key "
                "and internet connection."
            )
            st.caption(str(e))

else:
    st.write(
        "Upload at least one session file "
        "to generate the analysis."
    )


# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "Built as an educational Generative AI capstone MVP. "
    "Automated indicators must not be used as proof of attendance "
    "or student attention. Instructor verification is required."
)
