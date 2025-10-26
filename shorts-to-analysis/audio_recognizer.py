"""
Module for analyzing audio in videos using Gemini
"""
import os
from typing import Optional
import google.generativeai as genai


def analyze_audio_with_gemini(audio_path: str, api_key: str) -> str:
    """
    Analyze audio using Gemini's audio understanding capabilities.

    Args:
        audio_path: Path to audio file
        api_key: Gemini API key

    Returns:
        Audio description string
    """
    import time

    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"  [Audio] Attempt {attempt + 1}/{max_retries}...")
            # Configure Gemini
            genai.configure(api_key=api_key)

            print("  [Audio] Uploading audio file...")
            # Upload audio file with timeout
            audio_file = genai.upload_file(audio_path)

            # Wait for file to be processed
            print("  [Audio] Waiting for file to be ready...")
            while audio_file.state.name == "PROCESSING":
                time.sleep(2)
                audio_file = genai.get_file(audio_file.name)

            if audio_file.state.name == "FAILED":
                raise Exception("Audio file processing failed")

            print("  [Audio] Analyzing with Gemini...")
            # Use Gemini 2.5 Flash to analyze audio
            model = genai.GenerativeModel('gemini-2.5-flash-lite')

            prompt = """Analyze this audio and provide a brief description (1-2 sentences) covering:
- Type of audio (music, speech, sound effects, silence, etc.)
- If music: describe the genre, mood, or any recognizable elements
- If speech: mention the tone or what's being discussed
- Any notable sounds or audio characteristics

Be concise and descriptive."""

            response = model.generate_content([prompt, audio_file])

            print("  [Audio] Done!")
            return response.text.strip()

        except Exception as e:
            print(f"  [Audio] Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print(f"  [Audio] Retrying in 2 seconds...")
                time.sleep(2)
            else:
                print(f"  [Audio] All retries failed")
                return "Could not analyze audio - connection issues"


def recognize_audio(video_path: str, api_key: str) -> str:
    """
    Main function to extract and analyze audio from video using Gemini.

    Args:
        video_path: Path to video file
        api_key: Gemini API key

    Returns:
        Audio description string
    """
    import time

    # The audio file should be extracted by transcript_extractor (running in parallel)
    # Use the same path pattern
    audio_path = video_path.rsplit('.', 1)[0] + '_audio.mp3'

    # Wait for the audio file to be created (up to 30 seconds)
    print("  [Audio] Waiting for audio file to be extracted...")
    max_wait = 30
    waited = 0
    while not os.path.exists(audio_path) and waited < max_wait:
        time.sleep(1)
        waited += 1

    if not os.path.exists(audio_path):
        return "Audio file not available for analysis"

    print(f"  [Audio] Audio file found after {waited}s")

    # Analyze with Gemini
    description = analyze_audio_with_gemini(audio_path, api_key)

    return description


if __name__ == "__main__":
    # Test
    test_video = "output/downloads/OIs4CdJ8uE4.mp4"
    if os.path.exists(test_video):
        description = recognize_audio(test_video)
        print(f"Audio description: {description}")
