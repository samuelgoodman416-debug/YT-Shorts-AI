"""Composites voiceover + background video + burned-in captions into a finished vertical mp4."""

import re

from moviepy import AudioFileClip, CompositeVideoClip, ImageClip, TextClip
from moviepy.video.fx import FadeOut, Resize

from pipeline.background import get_background_clip
from pipeline.captions import group_into_captions, transcribe_words
from pipeline.reddit_card import render_card

CAPTION_FONT = "assets/fonts/Fredoka-Bold.ttf"
CAPTION_FONT_SIZE = 90
CAPTION_COLOR = "white"
CAPTION_STROKE_COLOR = "black"
CAPTION_STROKE_WIDTH = 4

HOOK_MIN_DURATION = 2.0
HOOK_MAX_DURATION = 6.0

POP_DURATION = 0.15
POP_START_SCALE = 0.6


def _pop_scale(t: float, duration: float = POP_DURATION, start_scale: float = POP_START_SCALE) -> float:
    """Ease-out-back scale curve: grows from start_scale to 1.0 with a slight overshoot bounce."""
    if t >= duration:
        return 1.0
    x = t / duration
    c1, c3 = 1.70158, 2.70158
    eased = 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
    return start_scale + (1 - start_scale) * eased


def _hook_duration(words: list) -> float:
    """How long to show the intro hook card: until the first sentence ends."""
    for word in words:
        if re.search(r"[.!?]$", word.text):
            return min(max(word.end, HOOK_MIN_DURATION), HOOK_MAX_DURATION)
    return HOOK_MIN_DURATION


def _build_hook_card_clip(title: str, username: str, duration: float, width: int, height: int) -> ImageClip:
    card = render_card(title, username=username, card_width=int(width * 0.85))
    return (
        ImageClip(card)
        .with_duration(duration)
        .with_effects([Resize(_pop_scale), FadeOut(0.15)])
        .with_position(("center", int(0.12 * height)))
    )


def _build_caption_clips(
    words: list,
    width: int,
    font: str,
    font_size: int,
    color: str,
    stroke_color: str,
    stroke_width: int,
) -> list[TextClip]:
    captions = group_into_captions(words)

    clips = []
    for text, start, end in captions:
        clip = (
            TextClip(
                font=font,
                text=text.upper(),
                font_size=font_size,
                color=color,
                stroke_color=stroke_color,
                stroke_width=stroke_width,
                method="caption",
                size=(int(width * 0.9), None),
                text_align="center",
            )
            .with_effects([Resize(_pop_scale)])
            .with_start(start)
            .with_end(end)
            .with_position(("center", "center"))
        )
        clips.append(clip)
    return clips


def assemble_video(
    audio_path: str,
    output_path: str,
    title: str = "",
    username: str = "StoryHub",
    width: int = 1080,
    height: int = 1920,
    caption_font: str = CAPTION_FONT,
    caption_font_size: int = CAPTION_FONT_SIZE,
    caption_color: str = CAPTION_COLOR,
    caption_stroke_color: str = CAPTION_STROKE_COLOR,
    caption_stroke_width: int = CAPTION_STROKE_WIDTH,
) -> str:
    audio = AudioFileClip(audio_path)
    background = get_background_clip(audio.duration, width=width, height=height)
    words = transcribe_words(audio_path)

    layers = [background]
    if title:
        hook_clip = _build_hook_card_clip(title, username, _hook_duration(words), width, height)
        layers.append(hook_clip)
    layers += _build_caption_clips(
        words,
        width,
        caption_font,
        caption_font_size,
        caption_color,
        caption_stroke_color,
        caption_stroke_width,
    )

    video = CompositeVideoClip(layers, size=(width, height)).with_audio(audio)
    video.write_videofile(output_path, fps=30, codec="libx264", audio_codec="aac")
    return output_path


if __name__ == "__main__":
    assemble_video(
        "output/tts_test.mp3",
        "output/test_video_captioned.mp4",
        title="This is a test of the text to speech system.",
    )
