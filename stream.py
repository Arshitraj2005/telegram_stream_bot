import subprocess
import os

current_process = None

def start_stream(stream_key, video_url, title, loop):
    global current_process
    output_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"

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
        ffmpeg_command.insert(1, "-stream_loop")
        ffmpeg_command.insert(2, "-1")

    current_process = subprocess.Popen(ffmpeg_command)

def stop_stream():
    global current_process
    if current_process:
        current_process.terminate()
        current_process = None

def stream_status():
    global current_process
    if current_process and current_process.poll() is None:
        return "✅ Stream is running."
    else:
        return "❌ No active stream."
