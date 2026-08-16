"""Converts text to speech using edge-tts (free, no API key required)."""

import asyncio

import edge_tts

DEFAULT_VOICE = "en-US-ChristopherNeural"
DEFAULT_RATE = "+25%"


async def _synthesize(text: str, voice: str, rate: str, output_path: str) -> None:
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)


def synthesize(text: str, output_path: str, voice: str = DEFAULT_VOICE, rate: str = DEFAULT_RATE) -> str:
    """Render text to an mp3 file at output_path. Returns output_path."""
    asyncio.run(_synthesize(text, voice, rate, output_path))
    return output_path


if __name__ == "__main__":
    sample = (
        "This is a test of the text to speech system for the short form video pipeline."
    )
    path = synthesize(sample, "output/tts_test.mp3")
    print(f"Wrote {path}")
