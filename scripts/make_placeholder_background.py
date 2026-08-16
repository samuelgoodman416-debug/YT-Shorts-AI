"""Dev utility: generates a synthetic color-cycling vertical clip for pipeline testing.

This is a placeholder only, not real background footage. Swap in licensed or
self-recorded footage in assets/background_clips/ before publishing anything.
"""

import colorsys

import numpy as np
from moviepy import VideoClip

WIDTH, HEIGHT = 1080, 1920
DURATION = 20


def make_frame(t):
    hue = (t / 8) % 1.0
    r, g, b = colorsys.hsv_to_rgb(hue, 0.55, 0.75)
    frame = np.empty((HEIGHT, WIDTH, 3), dtype=np.uint8)
    frame[:, :] = [int(r * 255), int(g * 255), int(b * 255)]
    return frame


if __name__ == "__main__":
    clip = VideoClip(make_frame, duration=DURATION).with_fps(30)
    clip.write_videofile("assets/background_clips/placeholder.mp4", codec="libx264", audio=False)
