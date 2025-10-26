import json
import os
import numpy as np
import faiss
from openai import OpenAI
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# === CONFIG ===
JSON_FILE = "meme_descriptions.json"
CACHE_FILE = "emb_cache.json"
REPORT_FILE = "meme_clusters.txt"
EMBED_MODEL = "text-embedding-3-small"
# client = OpenAI()

# === Load memes ===
with open(JSON_FILE, "r") as f:
    memes = json.load(f)

# === Load or initialize cache ===
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        cache = json.load(f)
else:
    cache = {}

fields = ["description", "humor", "topic", "meme_template"]
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

# === Convert to numpy + FAISS ===
faiss_indexes = {}
for field in fields:
    vecs = np.array(vector_dbs[field]["vectors"]).astype("float32")
    index = faiss.IndexFlatL2(vecs.shape[1])
    index.add(vecs)
    faiss_indexes[field] = index

# === Create text report ===
with open(REPORT_FILE, "w", encoding="utf-8") as report:
    report.write("📊 MEME CLUSTER ANALYSIS REPORT\n")
    report.write("=" * 60 + "\n\n")

    plt.figure(figsize=(12, 10))

    for i, field in enumerate(fields, 1):
        vecs = np.array(vector_dbs[field]["vectors"])
        ids = vector_dbs[field]["ids"]
        n = len(vecs)
        if n < 2:
            continue

        perplexity = max(2, min(30, (n - 1) / 3))
        reduced = TSNE(n_components=2, random_state=42, perplexity=perplexity).fit_transform(vecs)

        # ---- Auto choose cluster count ----
        k = min(8, max(2, n // 10))
        kmeans = KMeans(n_clusters=k, random_state=42, n_init="auto").fit(vecs)
        labels = kmeans.labels_

        # ---- Plot ----
        plt.subplot(2, 2, i)
        scatter = plt.scatter(
            reduced[:, 0],
            reduced[:, 1],
            c=labels,
            cmap="tab10",
            s=50,
            alpha=0.8,
            edgecolor="none"
        )
        plt.title(f"{field.capitalize()} (n={n}, clusters={k})")
        plt.axis("off")

        # ---- Write cluster summary to file ----
        report.write(f"=== FIELD: {field.upper()} ===\n")
        report.write(f"Total memes analyzed: {n}\n")
        report.write(f"Auto-detected clusters: {k}\n")
        report.write("-" * 60 + "\n")

        for cluster_id in range(k):
            members = [ids[j] for j in range(n) if labels[j] == cluster_id]
            report.write(f"\n📁 Cluster {cluster_id + 1} — {len(members)} memes\n")
            report.write("-" * 40 + "\n")

            for meme_id in members:
                desc = memes[meme_id].get(field, "").replace("\n", " ").strip()
                report.write(f"• {meme_id}: {desc}\n")

            report.write("\n")
        report.write("=" * 60 + "\n\n")

plt.suptitle("Meme Semantic Spaces by Field (t-SNE + KMeans Clustering)", fontsize=14)
plt.tight_layout()
plt.savefig("meme_clusters.png", dpi=300)
plt.show()

print(f"✅ Full report saved to {REPORT_FILE}")
print("✅ Visualization saved to meme_clusters.png")
