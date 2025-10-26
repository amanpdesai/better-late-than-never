"""
Module for downloading YouTube videos using yt-dlp
"""
import os
import yt_dlp


def download_video(url: str, output_dir: str = "downloads") -> str:
    """
    Download a YouTube video to the specified output directory.

    Args:
        url: YouTube video URL
        output_dir: Directory to save the downloaded video

    Returns:
        Path to the downloaded video file
    """
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info['id']
        ext = info['ext']
        video_path = os.path.join(output_dir, f'{video_id}.{ext}')

    return video_path


if __name__ == "__main__":
    # Test with a sample URL
    test_url = "https://www.youtube.com/watch?v=OIs4CdJ8uE4"
    video_path = download_video(test_url)
    print(f"Downloaded video to: {video_path}")
