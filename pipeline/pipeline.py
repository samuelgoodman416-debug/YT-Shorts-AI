"""Orchestrates story generation -> TTS -> assembly into finished captioned videos."""

import re
import time
from pathlib import Path

from pipeline.assemble import assemble_video
from pipeline.config import load_config
from pipeline.script import sanitize_for_tts
from pipeline.state import already_used, record_video
from pipeline.story_generator import generate_story
from pipeline.tts import synthesize

OUTPUT_DIR = Path("output")


def _slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:60] or "video"


def run_once(config: dict) -> str:
    story = generate_story(
        topic_hint=config.get("story_topic_hint") or None,
        target_words=config.get("target_story_words", 150),
    )

    if already_used(story.text):
        raise RuntimeError(f"Generated a duplicate story ({story.title!r}) - run again.")

    OUTPUT_DIR.mkdir(exist_ok=True)
    slug = f"{_slugify(story.title)}-{int(time.time())}"
    audio_path = OUTPUT_DIR / f"{slug}.mp3"
    video_path = OUTPUT_DIR / f"{slug}.mp4"

    narration = sanitize_for_tts(story.text)
    synthesize(
        narration,
        str(audio_path),
        voice=config.get("voice", "en-US-ChristopherNeural"),
        rate=config.get("voice_rate", "+25%"),
    )

    assemble_video(
        str(audio_path),
        str(video_path),
        title=story.title,
        username=config.get("channel_username", "StoryHub"),
        width=config.get("video_width", 1080),
        height=config.get("video_height", 1920),
        caption_font=config.get("caption_font", "assets/fonts/Fredoka-Bold.ttf"),
        caption_font_size=config.get("caption_font_size", 90),
        caption_color=config.get("caption_color", "white"),
        caption_stroke_color=config.get("caption_stroke_color", "black"),
        caption_stroke_width=config.get("caption_stroke_width", 4),
    )

    record_video(story.title, story.text, str(video_path))
    return str(video_path)


def run(videos_per_run: int | None = None) -> list[str]:
    config = load_config()
    count = videos_per_run if videos_per_run is not None else config.get("videos_per_run", 1)
    return [run_once(config) for _ in range(count)]
