import os
import re
import yt_dlp

def is_youtube_playlist(url):
    return "playlist?list=" in url

def is_youtube_video(url):
    return "youtube.com/watch" in url or "youtu.be/" in url

def is_onedrive_url(url):
    return "1drv.ms" in url or "onedrive.live.com" in url

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def download_from_youtube(url, is_playlist=False):
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': not is_playlist,
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if is_playlist:
            entries = info.get('entries', [])
            if entries:
                return ydl.prepare_filename(entries[0])
        else:
            return ydl.prepare_filename(info)

    return None

def prepare_stream_source(source_url_or_path):
    if os.path.isfile(source_url_or_path):
        return source_url_or_path
    elif is_youtube_playlist(source_url_or_path):
        return download_from_youtube(source_url_or_path, is_playlist=True)
    elif is_youtube_video(source_url_or_path):
        return download_from_youtube(source_url_or_path)
    elif is_onedrive_url(source_url_or_path):
        return convert_onedrive_link(source_url_or_path)
    else:
        return source_url_or_path

def convert_onedrive_link(url):
    if "redir?" in url or "embed?" in url:
        return url
    return url.replace("1drv.ms", "onedrive.live.com/download.aspx")
