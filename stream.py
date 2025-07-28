# stream.py

import subprocess
import os

def start_stream(stream_key, video_url, title, loop):
    output_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"

    # Set stream title (optional — YouTube usually uses scheduled live info)
    print(f"Starting stream: {title}")

    ffmpeg_command = [
        "ffmpeg",
        "-re",
        "-i", video_url,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-maxrate", "3000k",
        "-bufsize", "6000k",
        "-pix_fmt", "yuv420p",
        "-g", "50",
        "-c:a", "aac",
        "-b:a", "160k",
        "-ar", "44100",
        "-f", "flv",
        output_url
    ]

    if loop:
        ffmpeg_command = [
            "ffmpeg",
            "-stream_loop", "-1",  # infinite loop
            "-re",
            "-i", video_url,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-maxrate", "3000k",
            "-bufsize", "6000k",
            "-pix_fmt", "yuv420p",
            "-g", "50",
            "-c:a", "aac",
            "-b:a", "160k",
            "-ar", "44100",
            "-f", "flv",
            output_url
        ]

    return subprocess.Popen(ffmpeg_command)

def stop_stream(process):
    if process:
        process.terminate()

