import json
import os
import random
from typing import Dict, Optional

# === CONFIG ===
CLUSTERS_FILE = "meme_clusters.json"          # original with members + centroid
CHOICES_FILE  = "best_cluster_choices.json"   # LLM-picked clusters
KEY_FILE = "all_results.json"
OUTPUT_FILE   = "all_last_results.json"       # final combined result
ANALYSIS_FIELDS = ("description", "humor", "topic", "template")

# === Load files ===
if not os.path.exists(CLUSTERS_FILE):
    raise FileNotFoundError(f"{CLUSTERS_FILE} not found.")
if not os.path.exists(CHOICES_FILE):
    raise FileNotFoundError(f"{CHOICES_FILE} not found.")

with open(CLUSTERS_FILE, "r", encoding="utf-8") as f:
    clusters_data = json.load(f)

with open(CHOICES_FILE, "r", encoding="utf-8") as f:
    cluster_choices = json.load(f)

# === Load analysis details keyed by URL ===
def load_analysis_lookup(path: str) -> Dict[str, Dict[str, str]]:
    """Build a lookup of URL -> analysis metadata from the NDJSON results file."""
    if not os.path.exists(path):
        print(f"⚠️ Analysis file {path} not found.")
        return {}

    lookup: Dict[str, Dict[str, str]] = {}
    with open(path, "r", encoding="utf-8") as f:
        for idx, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                print(f"⚠️ Skipping malformed JSON on line {idx} of {path}: {exc}")
                continue

            url = record.get("url")
            analysis = record.get("analysis") or {}
            if not url:
                continue

            # Preserve the first occurrence of a URL; later duplicates are ignored.
            lookup.setdefault(url, analysis)

    return lookup


analysis_lookup = load_analysis_lookup(KEY_FILE)

# === Helper: get random + centroid ===
def sample_cluster(field_name: str, cluster_id: str):
    """Return a random member and centroid vector from a cluster."""
    field_data = clusters_data.get(field_name.replace(" ===", "").lower())
    if not field_data:
        print(f"⚠️ No data found for {field_name}")
        return None

    clusters = field_data.get("clusters", [])
    for cluster in clusters:
        if str(cluster["cluster_id"]) == str(cluster_id).replace("Cluster ", ""):
            members = cluster.get("members", [])
            centroid = cluster.get("centroid_vector")
            random_member = random.choice(members) if members else None
            return {
                "chosen_cluster": cluster_id,
                "random_sample": random_member,
                "centroid_vector": centroid
            }
    print(f"⚠️ Cluster {cluster_id} not found in {field_name}")
    return None


# === Build results from LLM choices ===
results = {}

for field_name, choice_str in cluster_choices.items():
    try:
        choice = json.loads(choice_str)
    except Exception:
        print(f"⚠️ Could not parse JSON for {field_name}")
        continue

    chosen_cluster = choice.get("chosen_cluster")
    if not chosen_cluster:
        continue

    entry = sample_cluster(field_name, chosen_cluster)
    if entry:
        entry["reason"] = choice.get("reason", "")
        random_sample = entry.get("random_sample")

        analysis_details: Optional[Dict[str, str]] = None
        if random_sample:
            url = (random_sample.get("id") or "").strip()
            if url:
                analysis_details = analysis_lookup.get(url)
                if not analysis_details and url.endswith("/"):
                    # Some URLs might include or omit trailing slashes; try without it.
                    analysis_details = analysis_lookup.get(url.rstrip("/"))
            else:
                print(f"⚠️ Random sample missing URL for {field_name}")

        if analysis_details:
            entry["analysis_summary"] = {
                field: analysis_details.get(field)
                for field in ANALYSIS_FIELDS
                if analysis_details.get(field) is not None
            }
        else:
            if random_sample:
                print(f"⚠️ No analysis found for {random_sample.get('id')}")

        results[field_name] = entry

# === Save final combined result ===
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n✅ Combined output saved to {OUTPUT_FILE}")
