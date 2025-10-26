import json
import os
import random
from openai import OpenAI

# === CONFIG ===
CLUSTERS_FILE = "cluster_summaries.json"   # contains labeled clusters
ALL_RESULTS_FILE = "all_results.json"      # contains meme metadata with URLs
OUTPUT_FILE = "best_cluster_choices_full.json"

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise EnvironmentError("❌ Missing OPENAI_API_KEY in environment.")
client = OpenAI(api_key=API_KEY)

# === Example user input ===
user_prompt = "I want to make a funny meme about dogs bonding with kids and family moments."

# === Load data ===
with open(CLUSTERS_FILE, "r", encoding="utf-8") as f:
    clusters = json.load(f)

if not os.path.exists(ALL_RESULTS_FILE):
    raise FileNotFoundError(f"{ALL_RESULTS_FILE} not found. Please provide your meme data.")
with open(ALL_RESULTS_FILE, "r", encoding="utf-8") as f:
    all_results = json.load(f)

# === Helper to ask GPT ===
def pick_best_cluster(user_prompt: str, category_name: str, clusters_dict: dict):
    cluster_descriptions = "\n".join(
        [f"{k}: {v['label']} ({v['description']})" for k, v in clusters_dict.items()]
    )

    prompt = f"""
The user wants to create a meme based on the following idea:

"{user_prompt}"

You are analyzing {category_name} meme clusters below.
Each cluster has a label and description.

Your task:
1. Read all clusters.
2. Pick the ONE cluster whose theme best matches the user's idea.
3. Respond in strict JSON format as:
{{"chosen_cluster": "<Cluster #>", "reason": "<why it matches>"}}

Clusters:
{cluster_descriptions}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a meme generation planner. Select the cluster that best aligns semantically "
                        "and emotionally with the user's idea."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Error picking cluster for {category_name}: {e}")
        return None


# === Helper: get centroid + random sample from chosen cluster ===
def get_cluster_details(category_name: str, chosen_cluster: str):
    """Get centroid and random meme from chosen cluster."""
    category = clusters.get(category_name)
    if not category:
        print(f"⚠️ No category found for {category_name}")
        return None

    cluster_key = chosen_cluster.strip()
    cluster_data = category.get(cluster_key)
    if not cluster_data:
        print(f"⚠️ Cluster {cluster_key} not found in {category_name}")
        return None

    # Random sample selection
    count = cluster_data.get("count", 0)
    label = cluster_data.get("label", "")
    desc = cluster_data.get("description", "")
    centroid_vec = cluster_data.get("centroid_vector", None)

    # Random sample placeholder (we don’t have IDs, so pick a pseudo-sample)
    random_sample = {
        "index": random.randint(0, max(count - 1, 0)),
        "label": label,
        "description": desc
    }

    return {
        "cluster_label": label,
        "centroid_vector": centroid_vec,
        "random_sample": random_sample,
        "cluster_size": count
    }


# === Run GPT + sample ===
results = {}

for field_name, field_clusters in clusters.items():
    print(f"\n🎯 Selecting best cluster for {field_name}...")
    choice_str = pick_best_cluster(user_prompt, field_name, field_clusters)
    if not choice_str:
        continue

    try:
        choice = json.loads(choice_str)
    except json.JSONDecodeError:
        print(f"⚠️ Could not parse GPT output for {field_name}: {choice_str}")
        continue

    chosen_cluster = choice.get("chosen_cluster")
    reason = choice.get("reason", "")

    cluster_details = get_cluster_details(field_name, chosen_cluster)
    if not cluster_details:
        continue

    results[field_name] = {
        "chosen_cluster": chosen_cluster,
        "reason": reason,
        **cluster_details
    }


# === Key into example meme data from all_results.json ===
example_meme = None
for meme_id, meme_data in all_results.items():
    if "https://www.youtube.com/watch?v=OIs4CdJ8uE4" in meme_id:
        example_meme = meme_data
        break

if example_meme:
    results["example_meme"] = example_meme
else:
    print("⚠️ Example meme URL not found in all_results.json.")


# === Save results ===
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n✅ Saved best cluster + random sample + centroid data to {OUTPUT_FILE}")
