import json
from dataclasses import dataclass


@dataclass
class AppConfig:
    language_audio_dir: str
    explanation_audio_dir: str


def read_config(config_file: str) -> AppConfig:
    with open(config_file) as file:
        data = json.load(file)
        return AppConfig(**data)
