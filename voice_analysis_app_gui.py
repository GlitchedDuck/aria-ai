import os
import subprocess
import sys
import uuid
from datetime import datetime
import ffmpeg
import streamlit as st


def convert_audio_to_wav(input_path):
    output_path = os.path.splitext(input_path)[0] + ".wav"
    ffmpeg.input(input_path).output(output_path).run(overwrite_output=True)
    return output_path


def transcribe(audio_path):
    base_dir = os.path.abspath(os.path.dirname(__file__))

    # Convert audio
    wav_path = convert_audio_to_wav(audio_path)

    # Whisper paths (must exist in cloud or local environment)
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


def generate_summary(transcript):
    # Placeholder summary generator
    return "Urgency: Medium\nIntent: Callback requested\nNext steps: Return the call."


st.title("🎙️ ARIA – Voice Analysis")
uploaded_file = st.file_uploader("Upload an audio file (mp3, wav, m4a):", type=["mp3", "wav", "m4a"])

if uploaded_file is not None:
    # Save file temporarily
    unique_id = uuid.uuid4().hex[:8]
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    temp_input_path = f"input_{unique_id}.tmp"
    with open(temp_input_path, "wb") as f:
        f.write(uploaded_file.read())

    st.info("Transcribing audio... This may take a moment.")
    transcript = transcribe(temp_input_path)

    if transcript.startswith("Transcription failed"):
        st.error(transcript)
    else:
        summary = generate_summary(transcript)

        st.subheader("Transcript")
        st.text_area("Transcript", transcript, height=200)

        st.subheader("Summary")
        st.text(summary)

    # Clean up
    if os.path.exists(temp_input_path):
        os.remove(temp_input_path)
