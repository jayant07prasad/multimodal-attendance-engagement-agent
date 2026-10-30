"""Pure analysis helpers for the Multimodal Attendance & Engagement Agent."""
import io
import wave
import numpy as np

def analyze_wav(audio_bytes):
    """Analyze PCM WAV energy; return None for unsupported/corrupt input."""
    try:
        with wave.open(io.BytesIO(audio_bytes), "rb") as wf:
            rate = wf.getframerate()
            channels = wf.getnchannels()
            width = wf.getsampwidth()
            frames = wf.readframes(wf.getnframes())
        if rate <= 0 or channels <= 0 or not frames:
            return None
        dtype = {1: np.uint8, 2: np.int16, 4: np.int32}.get(width)
        if dtype is None:
            return None
        audio = np.frombuffer(frames, dtype=dtype).astype(np.float64)
        if channels > 1:
            if audio.size % channels:
                return None
            audio = audio.reshape(-1, channels).mean(axis=1)
        if width == 1:
            audio -= 128.0
        if audio.size == 0:
            return None
        duration = audio.size / rate
        chunk = max(int(rate), 1)
        rms = [float(np.sqrt(np.mean(audio[i:i+chunk] ** 2)))
               for i in range(0, audio.size, chunk) if audio[i:i+chunk].size]
        if not rms:
            return None
        threshold = max(float(np.percentile(rms, 35)) * 1.8, 100.0)
        active = sum(value > threshold for value in rms)
        silent = len(rms) - active
        return {
            "duration": float(duration),
            "activity": active / len(rms) * 100.0,
            "segments": len(rms),
            "metadata": {"sample_rate": rate, "channels": channels,
                         "sample_width": width, "total_samples": int(audio.size),
                         "duration": float(duration)},
            "active_segments": int(active),
            "silent_segments": int(silent),
            "silence_percentage": silent / len(rms) * 100.0,
            "average_energy": float(np.mean(rms)),
            "peak_energy": float(np.max(rms)),
            "background_energy_estimate": float(np.percentile(rms, 20)),
        }
    except (wave.Error, EOFError, ValueError, TypeError, OSError):
        return None

def classify_audio_segment(samples, sample_rate):
    """Heuristic speech-like/noise-like/silence estimate, not speech recognition."""
    x = np.asarray(samples)
    if x.size == 0 or not sample_rate or sample_rate <= 0:
        return "silence", 0.0, 0.0, 0.0
    if np.issubdtype(x.dtype, np.integer):
        info = np.iinfo(x.dtype)
        scale = float(max(abs(info.min), info.max))
        x = x.astype(np.float32) / scale
    else:
        x = x.astype(np.float32)
        peak = float(np.max(np.abs(x))) if x.size else 0.0
        if peak > 1.5:
            x /= 32768.0
    x = x.reshape(-1)
    rms = float(np.sqrt(np.mean(x * x)))
    if rms < 0.008:
        return "silence", rms, 0.0, 0.0
    zcr = float(np.mean(np.signbit(x[1:]) != np.signbit(x[:-1]))) if x.size > 1 else 0.0
    windowed = x * np.hanning(x.size)
    spectrum = np.abs(np.fft.rfft(windowed))
    freqs = np.fft.rfftfreq(x.size, d=1.0 / sample_rate)
    centroid = float(np.sum(freqs * spectrum) / (np.sum(spectrum) + 1e-12))
    speech_like = 0.015 <= zcr <= 0.25 and 180 <= centroid <= 4000 and rms >= 0.008
    return ("speech-like" if speech_like else "noise-like"), rms, zcr, centroid
