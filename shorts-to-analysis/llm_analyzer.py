"""
Module for analyzing videos using Google's Gemini API
"""
import google.generativeai as genai
from typing import List, Optional, TypedDict
import os
from PIL import Image


class MemeAnalysis(TypedDict):
    """Structured analysis of a meme/short video"""
    description: str
    humor: str
    topic: str
    template: str
    sound_description: str


def analyze_video_content(
    keyframe_paths: List[str],
    transcript: Optional[str],
    api_key: str,
    sound_description: Optional[str] = None
) -> MemeAnalysis:
    """
    Analyze video content using Gemini API with keyframes and transcript.
    Returns structured analysis following the meme-rep schema.

    Args:
        keyframe_paths: List of paths to keyframe images
        transcript: Video transcript text (can be None)
        api_key: Google Gemini API key

    Returns:
        MemeAnalysis dict with description, humor, topic, and template
    """
    # Configure Gemini API
    genai.configure(api_key=api_key)

    # Define the schema for structured output
    schema = {
        "type": "object",
        "properties": {
            "description": {
                "type": "string",
                "description": "A paragraph (4-6 sentences) describing literally what is visible or happening in the video, without interpretation — who or what appears, what actions are shown, and any text that is visible."
            },
            "humor": {
                "type": "string",
                "description": "A few words (2-4 words max) identifying the type of humor, such as 'dark humor', 'absurdist comedy', 'situational irony', 'wordplay', 'slapstick', 'self-deprecating', etc."
            },
            "topic": {
                "type": "string",
                "description": "A few words (2-4 words max) naming the main subject or theme, such as 'workplace culture', 'social media', 'gaming', 'relationships', 'politics', etc."
            },
            "template": {
                "type": "string",
                "description": "A short sentence describing the structural format of the meme - how it's presented (e.g., 'side-by-side comparison format', 'reaction video with text overlay', 'before/after progression', 'screenshot compilation', 'POV format with captions'). Describe the actual FORMAT structure, not just naming a template."
            },
            "sound_description": {
                "type": "string",
                "description": "Audio information will be provided separately. Just pass through the provided sound description."
            }
        },
        "required": ["description", "humor", "topic", "template", "sound_description"]
    }

    # Use Gemini Exp 1206 (latest experimental model, Gemini 2.5 Flash) for vision capabilities with structured output
    model = genai.GenerativeModel(
        'gemini-2.5-flash-lite',
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": schema
        }
    )

    # Load images
    images = []
    for path in keyframe_paths:
        if os.path.exists(path):
            images.append(Image.open(path))

    # Build prompt
    prompt = """Analyze this YouTube Short/meme video based on the provided keyframes"""

    if transcript:
        prompt += f" and transcript.\n\nTranscript: {transcript}"
    else:
        prompt += "."

    prompt += """

Please provide a structured analysis with:

1. **description**: A detailed paragraph (4-6 sentences) describing literally what you see happening in the video. Include who or what appears, what actions are shown, any text visible, and the sequence of events. Be objective and descriptive.

2. **humor**: Just a few words (2-4 words) identifying the type of humor used (e.g., "dark humor", "absurdist comedy", "situational irony", "wordplay", "slapstick", etc.).

3. **topic**: Just a few words (2-4 words) naming the main subject or theme (e.g., "workplace culture", "social media", "gaming", "relationships", etc.).

4. **template**: A short sentence describing the structural FORMAT of how the meme is presented - the visual/narrative structure used (e.g., "side-by-side comparison format", "reaction video with text overlay", "before/after progression", "screenshot compilation", "POV format with captions", "dialogue over gameplay footage"). Focus on describing HOW the content is structured, not just naming a meme template.

5. **sound_description**: Use this value: "{sound_desc}"."""

    # Format the prompt with sound description
    formatted_prompt = prompt.format(sound_desc=sound_description or "No audio information available")

    # Create content list with prompt and images
    content = [formatted_prompt] + images

    # Generate response
    response = model.generate_content(content)

    # Parse JSON response
    import json
    analysis = json.loads(response.text)

    return analysis


if __name__ == "__main__":
    # Test - requires API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Please set GEMINI_API_KEY environment variable")
    else:
        test_frames = ["keyframes/OIs4CdJ8uE4_frame_000.jpg"]
        test_transcript = "Sample transcript text"
        if all(os.path.exists(f) for f in test_frames):
            analysis = analyze_video_content(test_frames, test_transcript, api_key)
            print(f"Analysis: {analysis}")
