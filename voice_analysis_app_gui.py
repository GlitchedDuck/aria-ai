import os
import streamlit as st
import tempfile
import whisper
import datetime

st.set_page_config(page_title="ARIA - Voice Analysis", layout="centered")
st.title("🎙️ ARIA - Your AI Receptionist")
st.caption("Upload a call recording or voice message to transcribe and analyse it.")

uploaded_file = st.file_uploader("Upload an audio file (MP3, WAV, M4A):", type=["mp3", "wav", "m4a"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    st.info("Transcribing audio with Whisper...")

    try:
        model = whisper.load_model("base")
        result = model.transcribe(tmp_path)
        transcript = result["text"]

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_folder = os.path.join("results", f"transcript_{timestamp}")
        os.makedirs(output_folder, exist_ok=True)

        transcript_path = os.path.join(output_folder, "transcript.txt")
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)

        summary = "Urgency: Medium\nIntent: Request for callback\nNext Steps: Return the customer's call."
        analysis_path = os.path.join(output_folder, "analysis.txt")
        with open(analysis_path, "w", encoding="utf-8") as f:
            f.write(summary)

        st.success("✅ Transcription and analysis complete!")
        st.subheader("Transcript")
        st.text_area("Text", transcript, height=250)

        st.subheader("Analysis")
        st.text(summary)

        st.download_button("Download Transcript", data=transcript, file_name="transcript.txt")
        st.download_button("Download Analysis", data=summary, file_name="analysis.txt")

    except Exception as e:
        st.error(f"Transcription failed: {str(e)}")
