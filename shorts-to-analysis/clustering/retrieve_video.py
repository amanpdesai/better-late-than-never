import openai
import os

import requests

id = "video_68fdedf18b648191b60493b9c6f1c18901a04a96cc624201"

openai.api_key = os.getenv("OPENAI_API_KEY")

def retrieve_video(job_id: str):
    """Retrieve the status of a video generation job."""
    try:
        status = openai.videos.retrieve(job_id)
        return status
    except Exception as e:
        print(f"❌ Error retrieving video job {job_id}: {e}")
        return None
    
video_status = retrieve_video(id)
print(video_status)

# GET request to download the video if the status is completed
if video_status and getattr(video_status, "status", None) in ("completed", "succeeded", "ready"):
    video_urls = []
    # Extract video URLs from the status object
    def _find_video_urls(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "url" and isinstance(value, str) and value.startswith("http"):
                    yield value
                else:
                    yield from _find_video_urls(value)
        elif isinstance(data, list):
            for item in data:
                yield from _find_video_urls(item)

    video_urls = list(_find_video_urls(video_status.__dict__))
    
    if video_urls:
        video_url = video_urls[0]
        print(f"⬇️  Downloading video from {video_url}")
        response = requests.get(video_url)
        output_path = "downloaded_video.mp4"
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"✅ Video downloaded to: {output_path}")
    else:
        print("❌ No video URL found in the job status.")