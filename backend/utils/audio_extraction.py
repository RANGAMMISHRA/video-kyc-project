# backend/utils/audio_extraction.py

import subprocess
from pathlib import Path

from backend.utils.performance_utils import timeit

@timeit
def extract_audio_from_video(video_path: str, audio_output_path: str, sample_rate=16000):
    """
    Extracts audio from the given video file using ffmpeg.
    - video_path: path to the input video file.
    - audio_output_path: path where the extracted audio .wav file will be saved.
    - sample_rate: target audio sample rate (default 16kHz for ASR).
    """
    video_path = Path(video_path)
    audio_output_path = Path(audio_output_path)
    audio_output_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "ffmpeg",
        "-y",  # overwrite without asking
        "-i", str(video_path),
        "-vn",                # no video
        "-acodec", "pcm_s16le",  # linear PCM
        "-ar", str(sample_rate), # sample rate
        "-ac", "1",             # mono channel
        str(audio_output_path)
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True, f"Audio extracted successfully: {audio_output_path}"
    except subprocess.CalledProcessError as e:
        return False, f"Audio extraction failed: {e.stderr.decode()}"
