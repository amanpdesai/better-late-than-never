import os, json
import google.generativeai as genai
from PIL import Image

# === Config ===
MEME_DIR = "all_memes"
OUT_JSON = "meme_descriptions.json"
MAX_MEMES = 300
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

model = genai.GenerativeModel("gemini-2.5-flash")

# === Load existing data ===
if os.path.exists(OUT_JSON):
    with open(OUT_JSON, "r") as f:
        existing_data = json.load(f)
else:
    existing_data = {}

# === Collect images ===
images = [f for f in os.listdir(MEME_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
images = images[:MAX_MEMES]

# === Prompt ===
PROMPT = """
You are a meme analyst. 
Analyze this meme and produce a JSON object with 4 concise fields.
Each field should be one short sentence, clear and factual — good for retrieval and semantic search.

Example format:
{
  "description": "A man in armor proudly holds a cat on a rooftop, blending heroism and tenderness.",
  "humor": "Absurd contrast between toughness and affection.",
  "topic": "Heroic imagery mixed with domestic softness.",
  "meme_template": "3D-rendered cinematic parody of action scenes."
}
Now output only the JSON object, nothing else.
"""

# === Process each image ===
for img_name in images:
    if img_name in existing_data:
        print(f"Skipping {img_name} (already done)")
        continue

    img_path = os.path.join(MEME_DIR, img_name)
    print(f"Processing {img_name}...")

    try:
        img = Image.open(img_path)

        response = model.generate_content([PROMPT, img])

        # Attempt to parse JSON output directly
        text = response.text.strip()
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            # fallback: clean up extra text or formatting
            start = text.find("{")
            end = text.rfind("}") + 1
            parsed = json.loads(text[start:end])

        existing_data[img_name] = {"id": img_name, **parsed}

    except Exception as e:
        print(f"❌ Error on {img_name}: {e}")

# === Save results ===
with open(OUT_JSON, "w") as f:
    json.dump(existing_data, f, indent=2)

print(f"✅ Done. Saved {len(existing_data)} entries to {OUT_JSON}")
