
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


def analyze_video(video_bytes, file_name="video.mp4"):
    import tempfile

    temp_path = None
    cap = None

    try:
        file_extension = os.path.splitext(file_name)[1].lower()

        if file_extension not in [".mp4", ".avi", ".mov"]:
            file_extension = ".mp4"

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file_extension
        ) as temp:
            temp.write(video_bytes)
            temp_path = temp.name

        cap = cv2.VideoCapture(temp_path)

        if not cap.isOpened():
            print("VIDEO ERROR: OpenCV could not open this video file.")
            return None

        fps = cap.get(cv2.CAP_PROP_FPS)
        fps = fps if fps and fps > 0 else 25
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if frame_count > 0 else 0

        cascade_path = (
            cv2.data.haarcascades
            + "haarcascade_frontalface_default.xml"
        )
        face_cascade = cv2.CascadeClassifier(cascade_path)

        if face_cascade.empty():
            return None

        
        frame_number = 0
        sampled_frames = 0
        face_frames = 0
        face_counts = []
        face_presence = {}
        preview = None

        while True:
            ok, frame = cap.read()
            if not ok:
                break

            if frame_number % max(int(fps), 1) == 0:
                gray = cv2.cvtColor(
                    frame, cv2.COLOR_BGR2GRAY
                )

                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )

                face_counts.append(len(faces))
                sampled_frames += 1

                if len(faces) > 0:
                    face_frames += 1

                if preview is None:
                    preview = cv2.cvtColor(
                        frame, cv2.COLOR_BGR2RGB
                    )

                # Assign temporary IDs to detected faces
                for x, y, w, h in faces:
                    center = (x + w / 2, y + h / 2)
                    matched_id = None

                    for face_id, data in face_presence.items():
                        old_x, old_y = data["last_center"]
                        distance = (
                            (center[0] - old_x) ** 2
                            + (center[1] - old_y) ** 2
                        ) ** 0.5

                        if distance < 80:
                            matched_id = face_id
                            break

                    if matched_id is None:
                        matched_id = len(face_presence) + 1
                        face_presence[matched_id] = {
                            "visible_samples": 0,
                            "last_center": center
                        }

                    face_presence[matched_id]["visible_samples"] += 1
                    face_presence[matched_id]["last_center"] = center

            frame_number += 1

        cap.release()
        cap = None

        sample_interval = max(int(fps), 1) / fps

        for data in face_presence.values():
            data["presence_seconds"] = (
                data["visible_samples"] * sample_interval
            )

        return {
            "duration": duration,
            "samples": sampled_frames,
            "presence": (
                face_frames / sampled_frames * 100
                if sampled_frames else 0
            ),
            "avg_faces": (
                float(np.mean(face_counts))
                if face_counts else 0
            ),
            "max_faces": max(face_counts, default=0),
            "tracked_faces": len(face_presence),
            "face_details": face_presence,
                        "attendance_estimates": {
                f"Face {face_id}": {
                    "presence_seconds": round(
                        data["presence_seconds"], 1
                    ),
                    "presence_percentage": round(
                        data["presence_seconds"] / duration * 100, 1
                    ) if duration > 0 else 0
                }
                for face_id, data in face_presence.items()
            },
            "preview": preview
        }

    except Exception as e:
        print("Video analysis error:", e)
        return None

    finally:
        if cap is not None:
            cap.release()

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

# ---------------- AUDIO ANALYSIS ----------------

from analysis_core import analyze_wav, classify_audio_segment


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

    models = ["gemini-3.8-flash", "gemini-3.6-flash"]
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

# ---------------- MULTIMODAL AGENT ----------------

def run_multimodal_agent(video_result, audio_result):

    vision_data = None
    audio_data = None

    if video_result:
        vision_data = {
            "video_duration": video_result["duration"],
            "face_presence": video_result["presence"],
            "average_faces": video_result["avg_faces"],
            "maximum_faces": video_result["max_faces"],
            "tracked_faces": video_result["tracked_faces"]
        }

    if audio_result:
        audio_data = {
            "audio_duration": audio_result["duration"],
            "audio_activity": audio_result["activity"],
            "active_segments": audio_result["active_segments"],
            "silent_segments": audio_result["silent_segments"],
            "silence_percentage": audio_result["silence_percentage"]
        }

    return {
        "vision": vision_data,
        "audio": audio_data,
        "available_modalities": [
            name for name, data in [
                ("Video", vision_data),
                ("Audio", audio_data)
            ] if data is not None
        ]
    }
def fuse_multimodal_signals(agent_result):

    vision = agent_result["vision"]
    audio = agent_result["audio"]

    vision_score = (
        vision["face_presence"] if vision else None
    )

    audio_score = (
        audio["audio_activity"] if audio else None
    )

    available_scores = [
        score for score in [vision_score, audio_score]
        if score is not None
    ]

    fused_score = (
        sum(available_scores) / len(available_scores)
        if available_scores else None
    )

    return {
        "vision_score": vision_score,
        "audio_score": audio_score,
                       "fused_score": fused_score,
        "modalities_used": len(available_scores),
        "engagement_level": (
            "Low" if fused_score is not None and fused_score < 30 else
            "Moderate" if fused_score is not None and fused_score < 65 else
            "High" if fused_score is not None else
            "Insufficient data"
        )
    }


def generate_session_analytics(video_result, audio_result, fusion_result):
    return {
        "video_duration": video_result["duration"] if video_result else 0,
        "audio_duration": audio_result["duration"] if audio_result else 0,
        "faces_tracked": video_result["tracked_faces"] if video_result else 0,
        "video_presence": video_result["presence"] if video_result else None,
        "audio_activity": audio_result["activity"] if audio_result else None,
        "silence_percentage": audio_result["silence_percentage"] if audio_result else None,
        "combined_activity": fusion_result["fused_score"],
        "activity_level": fusion_result["engagement_level"]
    }


# ---------------- LIVE WEBCAM + MICROPHONE ----------------
# Live media is processed in-memory in the browser-to-server WebRTC stream.
# Metrics are approximate and are not identity recognition or validated engagement.

import threading
import time
from streamlit_webrtc import webrtc_streamer, WebRtcMode, VideoProcessorBase, AudioProcessorBase
import av

class LiveVideoProcessor(VideoProcessorBase):
    def __init__(self):
        cascade = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade)
        self._lock = threading.Lock()
        self._metrics = {"frames": 0, "face_frames": 0, "face_count": 0}

    def get_metrics(self):
        with self._lock:
            return dict(self._metrics)

    def reset_metrics(self):
        with self._lock:
            self._metrics = {"frames": 0, "face_frames": 0, "face_count": 0}

    def recv(self, frame):
        image = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 200, 0), 2)
        with self._lock:
            self._metrics["frames"] += 1
            self._metrics["face_count"] = int(len(faces))
            if len(faces) > 0:
                self._metrics["face_frames"] += 1
        return av.VideoFrame.from_ndarray(image, format="bgr24")


class LiveAudioProcessor(AudioProcessorBase):
    def __init__(self):
        self._lock = threading.Lock()
        self._metrics = {
            "audio_frames": 0, "speech_frames": 0,
            "noise_frames": 0, "silence_frames": 0,
            "last_audio_rms": 0.0, "last_audio_zcr": 0.0,
            "last_audio_centroid": 0.0,
        }

    def get_metrics(self):
        with self._lock:
            return dict(self._metrics)

    def reset_metrics(self):
        with self._lock:
            for key in self._metrics:
                self._metrics[key] = 0.0 if key.startswith("last_") else 0

    def recv(self, frame):
        audio = frame.to_ndarray()
        samples = np.asarray(audio).flatten()
        rate = int(frame.sample_rate or 48000)
        label, rms, zcr, centroid = classify_audio_segment(samples, rate)
        with self._lock:
            self._metrics["audio_frames"] += 1
            self._metrics["last_audio_rms"] = rms
            self._metrics["last_audio_zcr"] = zcr
            self._metrics["last_audio_centroid"] = centroid
            if label == "speech-like":
                self._metrics["speech_frames"] += 1
            elif label == "noise-like":
                self._metrics["noise_frames"] += 1
            else:
                self._metrics["silence_frames"] += 1
        return frame


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

# ---------------- LIVE CLASSROOM MODE ----------------

st.divider()
st.header("🎥 Live Classroom Mode")
st.caption(
    "Allow camera and microphone permissions in your browser. "
    "Live face detection and audio pattern estimates run during the session."
)

live_col1, live_col2 = st.columns([2, 1])
with live_col1:
    live_ctx = webrtc_streamer(
        key="live-classroom-stream",
        mode=WebRtcMode.SENDRECV,
        video_processor_factory=LiveVideoProcessor,
        audio_processor_factory=LiveAudioProcessor,
        media_stream_constraints={"video": True, "audio": True},
        async_processing=True,
    )
with live_col2:
    st.write("**Live session controls**")
    if st.button("Refresh metrics", key="refresh_live_metrics"):
        st.rerun()

    # Read counters from the active processor instances. Unlike module globals,
    # these objects survive Streamlit script reruns while the WebRTC stream runs.
    video_processor = live_ctx.video_processor
    audio_processor = live_ctx.audio_processor

    if video_processor is not None:
        video_live = video_processor.get_metrics()
    else:
        video_live = {"frames": 0, "face_frames": 0, "face_count": 0}

    if audio_processor is not None:
        audio_live = audio_processor.get_metrics()
    else:
        audio_live = {
            "audio_frames": 0, "speech_frames": 0,
            "noise_frames": 0, "silence_frames": 0,
        }

    if st.button("Reset metrics", key="reset_live_metrics"):
        if video_processor is not None:
            video_processor.reset_metrics()
        if audio_processor is not None:
            audio_processor.reset_metrics()
        st.rerun()

    st.caption(
        "Press Refresh metrics to read the latest counters. "
        "Counters are stored in the active WebRTC processors."
    )
    st.metric("Video frames processed", video_live["frames"])
    st.metric("Current faces in frame", video_live["face_count"])
    presence_pct = (
        video_live["face_frames"] / video_live["frames"] * 100
        if video_live["frames"] else 0
    )
    st.metric("Frames with face detected", f"{presence_pct:.1f}%")

    total_audio = audio_live["audio_frames"]
    speech_pct = audio_live["speech_frames"] / total_audio * 100 if total_audio else 0
    noise_pct = audio_live["noise_frames"] / total_audio * 100 if total_audio else 0
    silence_pct = audio_live["silence_frames"] / total_audio * 100 if total_audio else 0
    st.metric("Audio frames processed", total_audio)
    st.metric("Speech-like audio frames", f"{speech_pct:.1f}%")
    st.metric("Noise-like audio frames", f"{noise_pct:.1f}%")
    st.metric("Silence frames", f"{silence_pct:.1f}%")
    st.caption(
        "Speech/noise labels are heuristic estimates from RMS, zero-crossing rate "
        "and spectral centroid; they are not reliable speech recognition."
    )

if live_ctx.state.playing:
    st.success("Live camera and microphone stream is running.")
else:
    st.info("Click START above and allow camera/microphone access to begin live analysis.")


# ---------------- DASHBOARD ----------------

left, right = st.columns(2)

video_result = None
audio_result = None

with left:
    st.subheader("📹 Vision Module")

    if video_file:
        with st.spinner("Analyzing video..."):
           video_result = analyze_video(
    video_file.getvalue(),
    video_file.name
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

            st.metric(
                "Maximum faces detected",
                video_result["max_faces"]
            )

            st.metric(
                "Temporary face tracks (approx.)",
                video_result["tracked_faces"]
            )

            with st.expander("Face-wise presence details"):
                for face_id, details in video_result["face_details"].items():
                    st.write(
                        f"Face {face_id}: "
                        f"{details['presence_seconds']:.1f} seconds detected"
                    )

            with st.expander("📋 Presence-Based Attendance Estimates"):
                for face_id, details in video_result["attendance_estimates"].items():
                    st.write(f"**{face_id}**")
                    st.write(f"Presence: {details['presence_seconds']} seconds")
                    st.write(f"Video coverage: {details['presence_percentage']}%")
                    st.divider()

                st.caption(
                    "These are approximate visual presence estimates, "
                    "not verified student attendance."
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
            audio_result = analyze_wav(audio_file.getvalue())

        if audio_result:
            st.metric(
                "Audio Duration",
                f"{audio_result['duration']:.1f} seconds"
            )

            st.metric(
                "Audio Activity",
                f"{audio_result['activity']:.1f}%"
            )

            st.metric(
                "Active Segments",
                audio_result["active_segments"]
            )

            st.metric(
                "Silent Segments",
                audio_result["silent_segments"]
            )

            st.metric(
                "Silence Percentage",
                f"{audio_result['silence_percentage']:.1f}%"
            )

            st.metric(
                "Average Audio Energy",
                f"{audio_result['average_energy']:.1f}"
            )

            st.metric(
                "Peak Audio Energy",
                f"{audio_result['peak_energy']:.1f}"
            )

            metadata = audio_result["metadata"]

            st.caption(f"Sample Rate: {metadata['sample_rate']} Hz")
            st.caption(f"Channels: {metadata['channels']}")
            st.caption(f"Total Audio Samples: {metadata['total_samples']}")
            st.caption(f"Audio Segments: {audio_result['segments']}")

            st.caption(
                f"Estimated background energy: "
                f"{audio_result['background_energy_estimate']:.1f}"
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
st.subheader("🧠 Explainable Multimodal Activity Summary")

if video_result or audio_result:

    # Multimodal Agent
    agent_result = run_multimodal_agent(
        video_result,
        audio_result
    )

    st.subheader("🤖 Multimodal Agent Status")
    st.write(
        "Available inputs: "
        + ", ".join(agent_result["available_modalities"])
    )

    # Multimodal Signal Fusion
    fusion_result = fuse_multimodal_signals(agent_result)

    st.subheader("🔗 Multimodal Signal Fusion")
    st.write(f"Video presence score: {fusion_result['vision_score']}")
    st.write(f"Audio activity score: {fusion_result['audio_score']}")
    st.write(
        f"Combined activity indicator: {fusion_result['fused_score']}"
    )

    st.caption(
        "Experimental indicator; not a validated engagement score."
    )

    if fusion_result["fused_score"] is not None:
        st.metric(
            "Combined Activity Band",
            fusion_result["engagement_level"]
        )
    else:
        st.warning("Insufficient data to estimate activity level.")

    # Student Session Analytics
    session_analytics = generate_session_analytics(
        video_result,
        audio_result,
        fusion_result
    )

    st.subheader("📊 Student Session Analytics")
    st.json(session_analytics)

    # Activity Scores
    vision_score = (
        video_result["presence"] if video_result else None
    )

    audio_score = (
        audio_result["activity"] if audio_result else None
    )

    score = fusion_result["fused_score"]

    st.subheader("Teaching Suggestions")

    if score is None:
        recommendation = "Upload valid video or audio data before generating suggestions."

    elif score < 30:
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

    st.info(
        "Suggestion is based on approximate video presence "
        "and audio activity indicators, not confirmed student understanding."
    )

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

