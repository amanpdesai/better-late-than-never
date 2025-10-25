"""
Module for extracting transcripts from YouTube videos using audio extraction
"""
import os
import subprocess
from typing import Optional
import google.generativeai as genai
import tempfile


def extract_audio_from_video(video_path: str) -> str:
    """
    Extract audio from video file using ffmpeg.

    Args:
        video_path: Path to video file

    Returns:
        Path to extracted audio file (MP3)
    """
    # Create temporary audio file path
    audio_path = video_path.rsplit('.', 1)[0] + '_audio.mp3'

    # Use ffmpeg to extract audio
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-vn',  # No video
        '-acodec', 'libmp3lame',  # MP3 codec
        '-y',  # Overwrite output file
        '-loglevel', 'error',  # Only show errors
        audio_path
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return audio_path
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio: {e}")
        return None


def get_transcript(video_path: str, api_key: str) -> Optional[str]:
    """
    Get transcript for a video using Gemini audio transcription.

    Args:
        video_path: Path to the video file
        api_key: Gemini API key

    Returns:
        Transcript text as a single string, or None if not available
    """
    import time

    max_retries = 3
    for attempt in range(max_retries):
        try:
            if attempt == 0:
                print("  [Transcript] Extracting audio...")
                # Extract audio from video
                audio_path = extract_audio_from_video(video_path)
                if not audio_path or not os.path.exists(audio_path):
                    return None

            print(f"  [Transcript] Attempt {attempt + 1}/{max_retries}...")
            # Configure Gemini
            genai.configure(api_key=api_key)

            print("  [Transcript] Uploading audio file...")
            # Upload audio file
            audio_file = genai.upload_file(audio_path)

            # Wait for file to be processed
            print("  [Transcript] Waiting for file to be ready...")
            while audio_file.state.name == "PROCESSING":
                time.sleep(2)
                audio_file = genai.get_file(audio_file.name)

            if audio_file.state.name == "FAILED":
                raise Exception("Audio file processing failed")

            print("  [Transcript] Transcribing with Gemini...")
            # Use Gemini 2.5 Flash to transcribe
            model = genai.GenerativeModel('gemini-2.5-flash')

            prompt = "Please transcribe all the speech in this audio file. Provide only the transcription text, nothing else."

            response = model.generate_content([prompt, audio_file])

            print("  [Transcript] Done!")
            # Don't delete audio file - it's needed by audio_recognizer too

            return response.text

        except Exception as e:
            print(f"  [Transcript] Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print(f"  [Transcript] Retrying in 2 seconds...")
                time.sleep(2)
            else:
                print(f"  [Transcript] All retries failed")
                return None

    return None


if __name__ == "__main__":
    # Test with a sample URL
    test_url = "https://www.youtube.com/watch?v=OIs4CdJ8uE4"
    transcript = get_transcript(test_url)
    if transcript:
        print(f"Transcript: {transcript[:200]}...")
    else:
        print("No transcript available")
