import json
import os
from typing import List
from openai import OpenAI

# === CONFIG ===
INPUT_JSON = "meme_clusters.json"
OUTPUT_JSON = "cluster_summaries.json"

# === Load API key from environment ===
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise EnvironmentError("❌ Missing OPENAI_API_KEY in environment. Please export it before running.")

client = OpenAI(api_key=API_KEY)

# === Function to generate a distinctive cluster label ===
def generate_cluster_label(descriptions: List[str], field_name: str, cluster_num: str) -> str:
    """Generate a short distinctive label summarizing a meme cluster."""

    descriptions_text = "\n".join([f"- {desc}" for desc in descriptions])

    prompt = f"""You are analyzing a meme cluster within the category '{field_name}'.
Below are example descriptions of memes in Cluster {cluster_num}.

Your goal:
1. Identify what makes this cluster distinctive and unique compared to others.
2. Summarize its defining characteristics in a concise way.
3. Output a short, catchy label (≤8 words) that best represents the essence of this cluster.

Descriptions:
{descriptions_text}

Label:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert meme analyst. "
                        "Your goal is to summarize clusters into concise, catchy thematic labels."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=30,
            temperature=0.4,
        )

        label = response.choices[0].message.content.strip()
        return label

    except Exception as e:
        print(f"❌ Error generating label for {field_name} Cluster {cluster_num}: {e}")
        return "Distinctive Meme Cluster"


# === Load clusters JSON ===
if not os.path.exists(INPUT_JSON):
    raise FileNotFoundError(f"{INPUT_JSON} not found. Run the clustering script first.")

with open(INPUT_JSON, "r", encoding="utf-8") as f:
    clusters_data = json.load(f)

# === Build formatted summary output ===
summary_output = {}

for field_name, field_data in clusters_data.items():
    print(f"\n🧩 Processing {field_name.upper()} ({field_data['num_clusters']} clusters)")
    field_summary = {}

    for cluster in field_data["clusters"]:
        cluster_num = cluster["cluster_id"]
        members = cluster.get("members", [])
        descriptions = [m["text"] for m in members if m["text"]]

        if not descriptions:
            label = "Empty Cluster"
        else:
            label = generate_cluster_label(descriptions, field_name, cluster_num)

        field_summary[f"Cluster {cluster_num}"] = {
            "label": label,
            "count": len(members),
            "description": f"Contains {len(members)} memes with distinctive characteristics: {label}"
        }

        print(f"  ✅ Cluster {cluster_num} → {label}")

    summary_output[f"{field_name.upper()} ==="] = field_summary

# === Save summary JSON in same directory as input ===
input_dir = os.path.dirname(os.path.abspath(INPUT_JSON))
output_path = os.path.join(input_dir, OUTPUT_JSON)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(summary_output, f, indent=2, ensure_ascii=False)

print(f"\n✅ Summary JSON saved to {output_path}")
