# Live WebRTC Notes

- Run the app locally with `streamlit run app.py` and open the displayed localhost URL.
- Click **START** in Live Classroom Mode and allow camera and microphone permissions.
- The video callback draws rectangles around detected faces and counts frames containing faces.
- The audio callback estimates speech-like, noise-like and silence segments from short audio frames.
- Click **Refresh live metrics** to display the latest counters; stop the stream when finished.

## Network deployment
For localhost, browser camera/microphone permissions normally work on `localhost`.
For access from another device or a public deployment, WebRTC requires a secure HTTPS origin
and appropriate STUN/TURN/network configuration. A public deployment may need TURN credentials
and firewall configuration.

## Classifier limitations
The audio labels are heuristic signal analysis, not machine-learning classification.
They do not transcribe speech, identify speakers, or reliably separate speech from music/noise.
Test with silence, ordinary speech, fan noise, music and mixed classroom audio. Record the
observed errors honestly in the project report.
