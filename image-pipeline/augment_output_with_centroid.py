"""
Merge the text output of query_meme_clusters.py with centroid vectors from
meme_clusters.json. The script expects the Gemini output (including the random
image suggestions) in an input file, extracts the chosen clusters and sample
images, looks up the matching cluster centroids, and writes a consolidated
report.

Usage:
    python augment_output_with_centroid.py \
        --input-file output.txt \
        --output-file output_with_centroid.txt
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Any

DATA_DIR = Path(__file__).resolve().parent
MEME_CLUSTERS_PATH = DATA_DIR / "meme_clusters.json"

CATEGORY_KEY_MAP = {
    "DESCRIPTION": "description",
    "HUMOR": "humor",
    "TOPIC": "topic",
    "MEME_TEMPLATE": "meme_template",
}

BEST_MATCH_PATTERN = re.compile(
    r"Best\s+Match\s+(DESCRIPTION|HUMOR|TOPIC|MEME_TEMPLATE)\s*:\s*Cluster\s+(\d+)",
    re.IGNORECASE,
)
CATEGORY_HEADING_PATTERN = re.compile(
    r"^(DESCRIPTION|HUMOR|TOPIC|MEME_TEMPLATE)\s*(?:\(Cluster\s+(\d+)\))?$",
    re.IGNORECASE,
)
BULLET_PATTERN = re.compile(r"^\s*-\s*([^:]+)")


@dataclass
class ClusterSelection:
    cluster_id: str
    random_image_id: Optional[str]
    centroid_image_id: Optional[str]


def parse_best_matches(lines: Iterable[str]) -> Dict[str, str]:
    """Extract the category -> cluster id mapping from the Best Match section."""
    matches: Dict[str, str] = {}
    for line in lines:
        for category, cluster_id in BEST_MATCH_PATTERN.findall(line):
            matches[category.upper()] = cluster_id
    return matches


def parse_random_images(lines: Iterable[str]) -> Dict[str, str]:
    """
    Extract the first random image file listed under each category.

    The output from query_meme_clusters.py prints headings like
    'DESCRIPTION (Cluster 4)' followed by one or more bullet lines. We keep the
    first bullet we see for each category.
    """
    selections: Dict[str, str] = {}
    current_category: Optional[str] = None
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        header_match = CATEGORY_HEADING_PATTERN.match(line)
        if header_match:
            current_category = header_match.group(1).upper()
            continue
        if current_category and current_category not in selections:
            bullet_match = BULLET_PATTERN.match(line)
            if bullet_match:
                selections[current_category] = bullet_match.group(1).strip()
    return selections


def load_data() -> Dict[str, Any]:
    return json.loads(MEME_CLUSTERS_PATH.read_text(encoding="utf-8"))


def build_attribute_index(data: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """Create a lookup of image_id -> {dimension: text} across all categories."""
    index: Dict[str, Dict[str, str]] = {}
    for category, payload in data.items():
        clusters = payload.get("clusters", [])
        for entry in clusters:
            for member in entry.get("members", []):
                image_id = member.get("id") or member.get("file")
                if not image_id:
                    continue
                text = (
                    member.get("text")
                    or member.get("description")
                    or member.get("humor")
                    or member.get("topic")
                    or member.get("template")
                )
                if text is None:
                    continue
                bucket = index.setdefault(image_id, {})
                bucket[category] = text
    return index


def get_centroid_image_id(data: Dict[str, Any], category: str, cluster_id: str) -> Optional[str]:
    """Fetch the centroid representative meme id for the cluster."""
    category_key = CATEGORY_KEY_MAP.get(category.upper())
    if not category_key:
        return None
    clusters = data.get(category_key, {}).get("clusters", [])
    target = next(
        (entry for entry in clusters if str(entry.get("cluster_id")) == str(cluster_id)),
        None,
    )
    if not target:
        return None
    representative = target.get("representative_meme") or {}
    file_id = representative.get("id") or representative.get("file")
    return str(file_id) if file_id else None


def build_image_payload(image_id: Optional[str], attribute_index: Dict[str, Dict[str, str]]) -> Optional[Dict[str, Any]]:
    if not image_id:
        return None
    bucket = attribute_index.get(image_id, {})
    return {
        "id": image_id,
        "description": bucket.get("description"),
        "humor": bucket.get("humor"),
        "topic": bucket.get("topic"),
        "meme_template": bucket.get("meme_template"),
    }


def build_output(selections: Dict[str, ClusterSelection], attribute_index: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    for category in ("DESCRIPTION", "HUMOR", "TOPIC", "MEME_TEMPLATE"):
        data = selections.get(category)
        if not data:
            payload[category] = None
        else:
            payload[category] = {
                "cluster_id": data.cluster_id,
                "random_image": build_image_payload(data.random_image_id, attribute_index),
                "centroid_image": build_image_payload(data.centroid_image_id, attribute_index),
            }
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Augment query_meme_clusters output with centroid vectors.",
    )
    parser.add_argument(
        "--input-file",
        default="output.txt",
        help="Path to the query_meme_clusters output (default: output.txt).",
    )
    parser.add_argument(
        "--output-file",
        default="output_with_centroid.txt",
        help="Where to write the combined output (default: output_with_centroid.txt).",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        parser.error(f"Input file not found: {input_path}")

    lines = input_path.read_text(encoding="utf-8").splitlines()
    best_matches = parse_best_matches(lines)
    random_images = parse_random_images(lines)

    data = load_data()
    attribute_index = build_attribute_index(data)

    selections: Dict[str, ClusterSelection] = {}
    for category, cluster_id in best_matches.items():
        centroid = get_centroid_image_id(data, category, cluster_id)
        selections[category] = ClusterSelection(
            cluster_id=cluster_id,
            random_image_id=random_images.get(category),
            centroid_image_id=centroid,
        )

    output_data = build_output(selections, attribute_index)
    output_text = json.dumps(output_data, indent=2, ensure_ascii=True)
    print(output_text)
    Path(args.output_file).write_text(output_text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
