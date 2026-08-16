"""Composites voiceover + background video + burned-in captions into a finished vertical mp4."""

from moviepy import AudioFileClip, CompositeVideoClip, TextClip

from pipeline.background import get_background_clip
from pipeline.captions import group_into_captions, transcribe_words

CAPTION_FONT = "C:/Windows/Fonts/impact.ttf"
CAPTION_FONT_SIZE = 90
CAPTION_COLOR = "white"
CAPTION_STROKE_COLOR = "black"
CAPTION_STROKE_WIDTH = 4


def _build_caption_clips(audio_path: str, width: int) -> list[TextClip]:
    words = transcribe_words(audio_path)
    captions = group_into_captions(words)

    clips = []
    for text, start, end in captions:
        clip = (
            TextClip(
                font=CAPTION_FONT,
                text=text.upper(),
                font_size=CAPTION_FONT_SIZE,
                color=CAPTION_COLOR,
                stroke_color=CAPTION_STROKE_COLOR,
                stroke_width=CAPTION_STROKE_WIDTH,
                method="caption",
                size=(int(width * 0.9), None),
                text_align="center",
            )
            .with_start(start)
            .with_end(end)
            .with_position(("center", "center"))
        )
        clips.append(clip)
    return clips


def assemble_video(audio_path: str, output_path: str, width: int = 1080, height: int = 1920) -> str:
    audio = AudioFileClip(audio_path)
    background = get_background_clip(audio.duration, width=width, height=height)
    caption_clips = _build_caption_clips(audio_path, width)

    video = CompositeVideoClip([background, *caption_clips], size=(width, height)).with_audio(audio)
    video.write_videofile(output_path, fps=30, codec="libx264", audio_codec="aac")
    return output_path


if __name__ == "__main__":
    assemble_video("output/tts_test.mp3", "output/test_video_captioned.mp4")
