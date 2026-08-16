"""Selects background video clip(s) and fits them to the target vertical frame and duration."""

import random
from pathlib import Path

from moviepy import CompositeVideoClip, VideoFileClip
from moviepy.video.fx import CrossFadeIn, Loop

BACKGROUND_DIR = Path("assets/background_clips")

TRANSITION_DURATION = 0.5


def _list_clips() -> list[Path]:
    return sorted(
        p for p in BACKGROUND_DIR.glob("*") if p.suffix.lower() in (".mp4", ".mov", ".m4v")
    )


def _fit_frame(clip: VideoFileClip, width: int, height: int) -> VideoFileClip:
    """Crop/resize a clip to exactly width x height, preserving center framing."""
    target_ratio = width / height
    if clip.w / clip.h > target_ratio:
        new_w = int(clip.h * target_ratio)
        x1 = (clip.w - new_w) // 2
        clip = clip.cropped(x1=x1, width=new_w)
    else:
        new_h = int(clip.w / target_ratio)
        y1 = (clip.h - new_h) // 2
        clip = clip.cropped(y1=y1, height=new_h)
    return clip.resized((width, height))


def get_background_clip(duration: float, width: int = 1080, height: int = 1920) -> VideoFileClip:
    """Return a single clip cropped/resized to width x height and trimmed to exactly `duration` seconds."""
    clips = _list_clips()
    if not clips:
        raise FileNotFoundError(
            f"No background clips found in {BACKGROUND_DIR}. Add an .mp4 file there first."
        )
    source = random.choice(clips)
    clip = _fit_frame(VideoFileClip(str(source)).without_audio(), width, height)

    if clip.duration < duration:
        clip = clip.with_effects([Loop(duration=duration)])
    else:
        clip = clip.subclipped(0, duration)

    return clip


def _allocate_segment_durations(total_duration: float, clip_durations: list[float]) -> list[float]:
    """Split total_duration across clips, preferring each clip's own length over looping.

    Clips shorter than an equal share give up their unused time to clips that have
    more footage available, so long clips play a bit longer instead of short clips
    looping. Only falls back to stretching (which requires looping) if the combined
    footage across all clips can't cover total_duration on its own.
    """
    n = len(clip_durations)
    ideal = total_duration / n
    allocated = [min(ideal, d) for d in clip_durations]
    remaining = total_duration - sum(allocated)

    for _ in range(n):
        if remaining <= 1e-6:
            break
        slack_indices = [i for i in range(n) if clip_durations[i] - allocated[i] > 1e-6]
        if not slack_indices:
            break
        share = remaining / len(slack_indices)
        for i in slack_indices:
            room = clip_durations[i] - allocated[i]
            take = min(share, room)
            allocated[i] += take
            remaining -= take

    if remaining > 1e-6:
        # Not enough total footage even using every clip at full length - the
        # leftover must be covered by looping, spread evenly across all clips.
        add_each = remaining / n
        allocated = [a + add_each for a in allocated]

    return allocated


def get_multi_background_clip(
    duration: float,
    width: int = 1080,
    height: int = 1920,
    num_segments: int = 3,
    transition: float = TRANSITION_DURATION,
) -> CompositeVideoClip:
    """Build a single clip of exactly `duration` seconds, cut across up to num_segments
    different background clips with a crossfade transition at each cut.

    Segment lengths favor an even split, but a clip shorter than its equal share
    yields its unused time to clips with more footage, so longer clips play a bit
    longer rather than looping a short one (see _allocate_segment_durations).
    """
    clips = _list_clips()
    if not clips:
        raise FileNotFoundError(
            f"No background clips found in {BACKGROUND_DIR}. Add an .mp4 file there first."
        )

    n = num_segments
    if len(clips) >= n:
        sources = random.sample(clips, k=n)
    else:
        sources = [random.choice(clips) for _ in range(n)]

    raw_clips = [VideoFileClip(str(p)).without_audio() for p in sources]
    clip_durations = [c.duration for c in raw_clips]

    tr = transition if n > 1 else 0.0
    target_sum = duration + (n - 1) * tr
    allocated = _allocate_segment_durations(target_sum, clip_durations)

    segments = []
    start = 0.0
    for i, (raw, alloc) in enumerate(zip(raw_clips, allocated)):
        fitted = _fit_frame(raw, width, height)
        if fitted.duration < alloc:
            fitted = fitted.with_effects([Loop(duration=alloc)])
        else:
            fitted = fitted.subclipped(0, alloc)

        fitted = fitted.with_start(start)
        if i > 0:
            fitted = fitted.with_effects([CrossFadeIn(tr)])
        segments.append(fitted)
        start += alloc - tr

    return CompositeVideoClip(segments, size=(width, height)).with_duration(duration)
