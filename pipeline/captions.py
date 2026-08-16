"""Transcribes narration audio to word-level timestamps for burned-in captions."""

from dataclasses import dataclass

from faster_whisper import WhisperModel

_model: WhisperModel | None = None


@dataclass
class Word:
    text: str
    start: float
    end: float


def _get_model() -> WhisperModel:
    global _model
    if _model is None:
        # "base" is a good speed/accuracy tradeoff on CPU for short clips.
        # First run downloads the model weights (~150MB) and caches them locally.
        _model = WhisperModel("base", device="cpu", compute_type="int8")
    return _model


def transcribe_words(audio_path: str) -> list[Word]:
    model = _get_model()
    segments, _info = model.transcribe(audio_path, word_timestamps=True)
    words: list[Word] = []
    for segment in segments:
        for word in segment.words:
            text = word.word.strip()
            if text:
                words.append(Word(text=text, start=word.start, end=word.end))
    return words


def group_into_captions(words: list[Word], words_per_caption: int = 4) -> list[tuple[str, float, float]]:
    """Group words into short on-screen caption chunks: (text, start, end)."""
    captions = []
    for i in range(0, len(words), words_per_caption):
        chunk = words[i : i + words_per_caption]
        text = " ".join(w.text for w in chunk)
        captions.append((text, chunk[0].start, chunk[-1].end))
    return captions


if __name__ == "__main__":
    words = transcribe_words("output/tts_test.mp3")
    for w in words:
        print(f"{w.start:5.2f} - {w.end:5.2f}  {w.text}")
