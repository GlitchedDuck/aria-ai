import os
import subprocess
import sys
import uuid
from datetime import datetime
from pydub import AudioSegment
import streamlit as st

# Setup ffmpeg path
ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")
ffprobe_path = os.path.join(os.path.dirname(__file__), "ffprobe.exe")
AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

# Transcribe audio using Whisper CLI
def transcribe(audio_path):
    base_dir = os.path.abspath(os.path.dirname(__file__))

    ffmpeg_path = os.path.join(base_dir, "ffmpeg.exe")
    ffprobe_path = os.path.join(base_dir, "ffprobe.exe")
    AudioSegment.converter = ffmpeg_path
    AudioSegment.ffprobe = ffprobe_path

    wav_path = audio_path.rsplit(".", 1)[0] + ".wav"
    audio = AudioSegment.from_file(audio_path)
    audio.export(wav_path, format="wav")

    whisper_cli = os.path.join(base_dir, "whisper-cli.exe")
    model_path = os.path.join(base_dir, "models", "ggml-base.en.bin")

    subprocess.run([whisper_cli, "-m", model_path, "-f", wav_path, "-otxt", "-oj"])

    transcript_file = wav_path + ".txt"
    if os.path.exists(transcript_file):
        with open(transcript_file, "r", encoding="utf-8") as f:
            transcript = f.read()
        os.remove(wav_path)
        return transcript
    else:
        return "Transcription failed. No output file found."


# Streamlit UI
st.set_page_config(page_title="Voice Analysis App", layout="centered")
st.title("📞 Voice Analysis App")

uploaded_file = st.file_uploader("Upload an MP3 or WAV file", type=["mp3", "wav"])

if uploaded_file is not None:
    unique_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_" + str(uuid.uuid4())[:8]
    result_folder = os.path.join("Results", unique_id)
    os.makedirs(result_folder, exist_ok=True)

    input_path = os.path.join(result_folder, uploaded_file.name)
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with st.spinner("Transcribing audio..."):
        transcript = transcribe(input_path)

    st.success("✅ Transcription complete!")

    st.subheader("📄 Transcript")
    st.text_area("Transcript", transcript, height=300)

    # Placeholder summary
    summary = "Urgency: Medium\nIntent: Request for callback\nNext Steps: Return the customer's call."

    st.subheader("🧠 Summary")
    st.text_area("Analysis", summary, height=150)

    # Save files
    transcript_path = os.path.join(result_folder, "transcript.txt")
    analysis_path = os.path.join(result_folder, "analysis.txt")

    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(transcript)

    with open(analysis_path, "w", encoding="utf-8") as f:
        f.write(summary)

    st.success(f"Results saved in: {result_folder}")
