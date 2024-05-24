from typing import BinaryIO

from boto3 import Session
from contextlib import closing
import sys


def _get_id_from_name(voices: list[dict], name: str) -> str:
    id_to_name = {item.get("Name"): item.get("Id") for item in voices}

    return id_to_name[name]


def _save_binary_to_mp3(content: BinaryIO, filename: str) -> None:
    with open(filename, "wb") as mp3_file:
        mp3_file.write(content)


def get_voices(client: Session.client) -> list[dict]:
    voices_response = client.describe_voices(
        Engine="generative",
        LanguageCode="en-US",
    )
    return voices_response["Voices"]


def list_available_names(voices: list[dict]) -> list[dict]:
    return [voice.get("Name") for voice in voices]


def convert_text_to_mp3(
    client: Session.client,
    message: str,
    voices: list[dict],
    voice_name: str,
    mp3_filename: str,
) -> None:
    voice_id = _get_id_from_name(voices, voice_name)
    # Request speech synthesis
    response = client.synthesize_speech(
        Engine="generative", Text=message, OutputFormat="mp3", VoiceId=voice_id
    )

    # Access the audio stream from the response
    if "AudioStream" in response:
        # Note: Closing the stream is important because the service throttles on the
        # number of parallel connections. Here we are using contextlib.closing to
        # ensure the close method of the stream object will be called automatically
        # at the end of the with statement's scope.
        with closing(response["AudioStream"]) as stream:
            try:
                # Open a file for writing the output as a binary stream
                with open(mp3_filename, "wb") as file:
                    file.write(stream.read())
            except IOError as error:
                # Could not write to file, exit gracefully
                print(error)
                sys.exit(-1)

    else:
        # The response didn't contain audio data, exit gracefully
        print("Could not stream audio")
        sys.exit(-1)
