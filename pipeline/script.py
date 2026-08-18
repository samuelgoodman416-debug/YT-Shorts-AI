"""Cleans generated story text so it reads naturally when spoken by TTS."""

import re


def sanitize_for_tts(text: str) -> str:
    text = re.sub(r"[*_#`]", "", text)  # markdown emphasis/headers/code marks
    text = re.sub(r"\s*[—–]\s*", ", ", text)  # em/en dashes -> spoken pause
    text = re.sub(r"\s+", " ", text).strip()
    return text
