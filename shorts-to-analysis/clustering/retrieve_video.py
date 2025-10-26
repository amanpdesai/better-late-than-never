from openai import OpenAI
import os

import requests

id = "video_68fdedf18b648191b60493b9c6f1c18901a04a96cc624201"

client = OpenAI()

status = client.videos.retrieve(id)
print(status)

response = client.videos.download_content(id)
print(response)

# Ensure we write raw bytes to the file: extract bytes from the HttpxBinaryResponseContent or Response
if hasattr(response, "read") and callable(response.read):
    data = response.read()
elif hasattr(response, "content"):
    data = response.content
else:
    data = response

with open("downloaded_video.mp4", "wb") as f:
    f.write(data)