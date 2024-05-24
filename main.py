import os

import boto3
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

import text_to_speech as tts
from config import read_config
from explainer import retrieve_code_explanation, retrieve_code_language


polly = boto3.client(
    "polly",
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name="us-east-1",
)


def display_header() -> None:
    st.image("img/logo.png", width=100)
    st.title("Welcome to AI Code Tutor")
    st.text("Simply upload your code or paste it into the field below.")
    st.warning("Note: Uploaded files will take priority over copied and pasted code.")


def display_widgets() -> tuple[UploadedFile, str]:
    file = st.file_uploader("Upload your script here.")
    text = st.text_area("or copy and paste your code here (press Ctrl + Enter to send)")

    if not (text or file):
        st.error("Bring your code with one of the options from above.")

    return file, text


def retrieve_content_from_file(file: UploadedFile) -> str:
    return file.getvalue().decode("utf8")


def extract_code() -> str:
    uploaded_script, pasted_code = display_widgets()

    if uploaded_script:
        return retrieve_content_from_file(uploaded_script)
    return pasted_code or ""


def choose_voice(voices: list):
    voices = tts.list_available_names(voices)
    return st.selectbox(
        "Could you please choose one of our available voices to explain?",
        voices,
    )


def main() -> None:
    # read the configuration settings from a JSON file
    config = read_config("./config.json")

    display_header()

    voices = tts.get_voices(client=polly)
    selected_voice = choose_voice(voices)

    if code_to_explain := extract_code():
        with st.spinner(text="Let me think for a while..."):
            language = retrieve_code_language(code=code_to_explain)
            explanation = retrieve_code_explanation(code=code_to_explain)

        with st.spinner(text="Give me a little bit more time..."):
            tts.convert_text_to_mp3(
                client=polly,
                message=language,
                voices=voices,
                voice_name=selected_voice,
                mp3_filename=config.language_audio_dir,
            )
        with st.spinner(
            text=(
                "I've got the language! "
                "I'm thinking about how to explain to you in a few words now..."
            )
        ):
            tts.convert_text_to_mp3(
                client=polly,
                message=explanation,
                voices=voices,
                voice_name=selected_voice,
                mp3_filename=config.explanation_audio_dir,
            )

        st.success("Uhg, that was hard! But here is your explanation")
        st.warning("Remember to turn on your audio!")

        st.markdown(f"**Language:** {language}")
        st.audio("language.mp3")

        st.markdown(f"**Explanation:** {explanation}")
        st.audio("explanation.mp3")


if __name__ == "__main__":
    main()
