import json
import os
import math
import numpy as np
import faiss
from openai import OpenAI
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
import matplotlib.pyplot as plt

# === CONFIG ===
JSON_FILE = "all_results.jsonl"
CACHE_FILE = "emb_cache.json"
OUTPUT_JSON = "meme_clusters.json"
EMBED_MODEL = "text-embedding-3-small"

# Initialize OpenAI client
client = OpenAI(api_key="OPENAI_API_KEY_REMOVED")

# === Load memes from JSONL ===
memes = {}
with open(JSON_FILE, "r") as f:
    for idx, line in enumerate(f):
        data = json.loads(line)
        # Skip failed entries
        if not data.get("success", False):
            continue
        # Use URL as unique ID
        meme_id = data["url"]
        # Extract analysis data if available
        if "analysis" in data:
            memes[meme_id] = data["analysis"]

print(f"Loaded {len(memes)} successful meme analyses")

# === Load or initialize cache ===
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        cache = json.load(f)
else:
    cache = {}

fields = ["description", "humor", "topic", "template", "sound_description"]
vector_dbs = {field: {"ids": [], "vectors": []} for field in fields}

# === Collect embeddings ===
for meme_id, meme_data in memes.items():
    for field in fields:
        text = meme_data.get(field, "")
        if not text:
            continue
        cache_key = f"{meme_id}:{field}"
        if cache_key in cache:
            emb = cache[cache_key]
        else:
            emb = client.embeddings.create(model=EMBED_MODEL, input=text).data[0].embedding
            cache[cache_key] = emb
        vector_dbs[field]["ids"].append(meme_id)
        vector_dbs[field]["vectors"].append(emb)

# === Save updated cache ===
with open(CACHE_FILE, "w") as f:
    json.dump(cache, f)

# === Convert to numpy + FAISS + KMeans + t-SNE ===
result_json = {}
valid_fields = [field for field in fields if len(vector_dbs[field]["vectors"]) >= 2]
num_plots = len(valid_fields)
cols = rows = 1
if num_plots:
    cols = math.ceil(math.sqrt(num_plots))
    rows = math.ceil(num_plots / cols)
    plt.figure(figsize=(cols * 5, rows * 4))
else:
    plt.figure(figsize=(8, 6))
plot_idx = 0

for field in fields:
    vecs = np.array(vector_dbs[field]["vectors"]).astype("float32")
    ids = vector_dbs[field]["ids"]
    n = len(vecs)
    if n < 2:
        continue

    # --- Reduce for visualization ---
    perplexity = max(2, min(30, (n - 1) / 3))
    reduced = TSNE(n_components=2, random_state=42, perplexity=perplexity).fit_transform(vecs)

    # --- KMeans clustering ---
    k = min(8, max(2, n // 10))
    kmeans = KMeans(n_clusters=k, random_state=42, n_init="auto").fit(vecs)
    labels = kmeans.labels_
    centroids = kmeans.cluster_centers_

    # --- Find representative meme for each centroid ---
    closest_ids, _ = pairwise_distances_argmin_min(centroids, vecs)

    # --- Build JSON structure for this field ---
    clusters = []
    for cluster_id in range(k):
        members = [ids[j] for j in range(n) if labels[j] == cluster_id]
        centroid_vec = centroids[cluster_id].tolist()
        representative_id = ids[closest_ids[cluster_id]]

        clusters.append({
            "cluster_id": cluster_id + 1,
            "size": len(members),
            "centroid_vector": centroid_vec,
            "representative_meme": {
                "id": representative_id,
                "text": memes[representative_id].get(field, "")
            },
            "members": [
                {
                    "id": meme_id,
                    "text": memes[meme_id].get(field, "")
                }
                for meme_id in members
            ]
        })

    result_json[field] = {
        "total_memes": n,
        "num_clusters": k,
        "clusters": clusters
    }

    # --- Visualization ---
    if num_plots:
        plot_idx += 1
        plt.subplot(rows, cols, plot_idx)
        plt.scatter(reduced[:, 0], reduced[:, 1], c=labels, cmap="tab10", s=50, alpha=0.8)
        plt.scatter(
            reduced[closest_ids, 0],
            reduced[closest_ids, 1],
            color="black",
            s=150,
            marker="*",
            label="centroid"
        )
        plt.title(f"{field.capitalize()} (n={n}, clusters={k})")
        plt.axis("off")

# === Save JSON ===
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(result_json, f, indent=2, ensure_ascii=False)

plt.suptitle("Meme Semantic Spaces by Field (t-SNE + KMeans Clustering)", fontsize=14)
plt.tight_layout()
plt.savefig("meme_clusters.png", dpi=300)
plt.show()

print(f"✅ Cluster JSON saved to {OUTPUT_JSON}")
print("✅ Visualization saved to meme_clusters.png")
