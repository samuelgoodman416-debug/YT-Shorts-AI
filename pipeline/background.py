"""Selects a background video clip and fits it to the target vertical frame and duration."""

import random
from pathlib import Path

from moviepy import VideoFileClip
from moviepy.video.fx import Loop

BACKGROUND_DIR = Path("assets/background_clips")


def _list_clips() -> list[Path]:
    return sorted(
        p for p in BACKGROUND_DIR.glob("*") if p.suffix.lower() in (".mp4", ".mov", ".m4v")
    )


def get_background_clip(duration: float, width: int = 1080, height: int = 1920) -> VideoFileClip:
    """Return a clip cropped/resized to width x height and trimmed to exactly `duration` seconds."""
    clips = _list_clips()
    if not clips:
        raise FileNotFoundError(
            f"No background clips found in {BACKGROUND_DIR}. Add an .mp4 file there first."
        )
    source = random.choice(clips)
    clip = VideoFileClip(str(source)).without_audio()

    target_ratio = width / height
    if clip.w / clip.h > target_ratio:
        new_w = int(clip.h * target_ratio)
        x1 = (clip.w - new_w) // 2
        clip = clip.cropped(x1=x1, width=new_w)
    else:
        new_h = int(clip.w / target_ratio)
        y1 = (clip.h - new_h) // 2
        clip = clip.cropped(y1=y1, height=new_h)
    clip = clip.resized((width, height))

    if clip.duration < duration:
        clip = clip.with_effects([Loop(duration=duration)])
    else:
        clip = clip.subclipped(0, duration)

    return clip
