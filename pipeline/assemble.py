"""Composites voiceover + background video into a finished vertical mp4 (no captions yet)."""

from moviepy import AudioFileClip

from pipeline.background import get_background_clip


def assemble_video(audio_path: str, output_path: str, width: int = 1080, height: int = 1920) -> str:
    audio = AudioFileClip(audio_path)
    background = get_background_clip(audio.duration, width=width, height=height)
    video = background.with_audio(audio)
    video.write_videofile(output_path, fps=30, codec="libx264", audio_codec="aac")
    return output_path


if __name__ == "__main__":
    assemble_video("output/tts_test.mp3", "output/test_video.mp4")
