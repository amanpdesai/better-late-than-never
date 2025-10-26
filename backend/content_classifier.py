"""
Content type classifier for determining whether to generate image or video.
"""

import os
from openai import OpenAI
from config import OPENAI_MODELS


def classify_content_type(prompt: str) -> str:
    """
    Classify whether the user wants an image or video based on their prompt.
    
    Args:
        prompt: User's natural language prompt
        
    Returns:
        "image" or "video"
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ No OpenAI API key found, defaulting to image generation")
        return "image"
    
    client = OpenAI(api_key=api_key)
    
    classification_prompt = f"""
Analyze the following user prompt and determine whether they want to generate an IMAGE or VIDEO meme.

User prompt: "{prompt}"

Consider these indicators for VIDEO generation:
- Keywords: "animated", "moving", "video", "short", "clip", "motion", "dynamic"
- Context: "TikTok-style", "reel", "story", "sequence", "action"
- Descriptions: "jumping", "running", "transforming", "changing", "flowing"

Consider these indicators for IMAGE generation:
- Keywords: "picture", "photo", "still", "static", "poster", "meme"
- Context: "social media post", "caption", "quote", "text overlay"
- Descriptions: "funny", "relatable", "comparison", "before/after"

Respond with ONLY one word: either "image" or "video"

If the prompt is ambiguous or doesn't clearly indicate motion/animation, default to "image".
"""

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODELS["content_classifier"],
            messages=[
                {
                    "role": "system",
                    "content": "You are a content type classifier. Analyze prompts and respond with only 'image' or 'video'."
                },
                {"role": "user", "content": classification_prompt}
            ],
            max_tokens=10,
            temperature=0.1
        )
        
        result = response.choices[0].message.content.strip().lower()
        
        if result in ["image", "video"]:
            print(f"🎯 Classified prompt as: {result}")
            return result
        else:
            print(f"⚠️ Unexpected classification result: {result}, defaulting to image")
            return "image"
            
    except Exception as e:
        print(f"❌ Error in content classification: {e}")
        return "image"
