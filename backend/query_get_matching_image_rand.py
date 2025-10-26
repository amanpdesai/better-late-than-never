"""
Utility script to pick random meme images for the clusters predicted by the
Gemini query step. Given the \"Best Match\" summary and the meme_clusters.json
metadata, this returns a handful of representative images per category.

Examples:
    python query_get_matching_image_rand.py \\
        --matches-text \"Best Match DESCRIPTION: Cluster 4\\nBest Match HUMOR: Cluster 2\" \\
        --topic 4 --meme-template 7

    python query_get_matching_image_rand.py --matches-file best_matches.txt
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional

DATA_DIR = Path(__file__).resolve().parent
MEME_CLUSTERS_PATH = DATA_DIR / "meme_clusters.json"
CATEGORY_KEYS = ("DESCRIPTION", "HUMOR", "TOPIC", "MEME_TEMPLATE")


def load_meme_clusters(path: Path = MEME_CLUSTERS_PATH) -> Mapping[str, Mapping[str, List[Dict[str, str]]]]:
    """Load the precomputed meme cluster entries."""
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def parse_matches(text: str) -> Dict[str, str]:
    """
    Parse \"Best Match <CATEGORY>: Cluster <id>\" lines from the Gemini response.
    Returns a mapping of CATEGORY -> cluster_id string.
    """
    pattern = re.compile(
        r"Best\s+Match\s+(DESCRIPTION|HUMOR|TOPIC|MEME_TEMPLATE)\s*:\s*Cluster\s+(\d+)",
        re.IGNORECASE,
    )
    matches: Dict[str, str] = {}
    for category, cluster_id in pattern.findall(text):
        matches[category.upper()] = cluster_id
    return matches


def resolve_requested_clusters(
    parsed_matches: MutableMapping[str, str],
    *,
    description: Optional[str],
    humor: Optional[str],
    topic: Optional[str],
    meme_template: Optional[str],
) -> Dict[str, str]:
    """Combine parsed text matches with explicit CLI overrides."""
    override_map = {
        "DESCRIPTION": description,
        "HUMOR": humor,
        "TOPIC": topic,
        "MEME_TEMPLATE": meme_template,
    }
    for category, value in override_map.items():
        if value is not None:
            parsed_matches[category] = str(value)
    return dict(parsed_matches)


def pick_random_items(
    data: Mapping[str, Mapping[str, List[Dict[str, str]]]],
    category: str,
    cluster_id: str,
    *,
    count: int,
    rng: random.Random,
) -> List[Dict[str, str]]:
    """Return up to ``count`` random items from the requested cluster."""
    clusters = data.get(category, {})
    items = clusters.get(cluster_id)
    if not items:
        return []
    sample_count = min(count, len(items))
    if sample_count == 0:
        return []
    if sample_count == len(items):
        return list(items)
    return rng.sample(items, sample_count)


def iter_text_sources(args: argparse.Namespace) -> Iterable[str]:
    """Yield raw text from the available input sources."""
    if args.matches_file:
        yield Path(args.matches_file).read_text(encoding="utf-8")
    if args.matches_text:
        yield args.matches_text
    if not sys.stdin.isatty():
        stdin_text = sys.stdin.read().strip()
        if stdin_text:
            yield stdin_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Pick random images from meme_clusters.json for the predicted cluster matches.",
    )
    parser.add_argument(
        "--matches-file",
        help="Path to a text file containing the Gemini best-match summary.",
    )
    parser.add_argument(
        "--matches-text",
        help="Raw Gemini best-match summary as a string.",
    )
    parser.add_argument(
        "--description",
        help="Override cluster id for the DESCRIPTION category.",
    )
    parser.add_argument(
        "--humor",
        help="Override cluster id for the HUMOR category.",
    )
    parser.add_argument(
        "--topic",
        help="Override cluster id for the TOPIC category.",
    )
    parser.add_argument(
        "--meme-template",
        dest="meme_template",
        help="Override cluster id for the MEME_TEMPLATE category.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=2,
        help="Number of random images to return per category (default: 2).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Optional RNG seed for reproducible sampling.",
    )
    parser.add_argument(
        "--output-file",
        default="output.txt",
        help="Path to write the formatted output (default: output.txt). Use '-' to skip writing.",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    raw_matches: Dict[str, str] = {}
    for text in iter_text_sources(args):
        raw_matches.update(parse_matches(text))

    resolved = resolve_requested_clusters(
        raw_matches,
        description=args.description,
        humor=args.humor,
        topic=args.topic,
        meme_template=args.meme_template,
    )

    if not resolved:
        parser.error(
            "No clusters provided. Use --matches-text/--matches-file or specify category overrides.",
        )

    data = load_meme_clusters()
    rng = random.Random(args.seed)

    lines = []
    for category in CATEGORY_KEYS:
        cluster_id = resolved.get(category)
        heading = f"{category}"
        if cluster_id is not None:
            heading = f"{heading} (Cluster {cluster_id})"
        lines.append(heading)
        if not cluster_id:
            lines.append("  (no cluster provided)")
            continue
        entries = pick_random_items(data, category, cluster_id, count=args.count, rng=rng)
        if not entries:
            lines.append("  (cluster not found or contains no items)")
            continue
        for item in entries:
            file_name = item.get("file", "<unknown file>")
            detail = (
                item.get("description")
                or item.get("humor")
                or item.get("topic")
                or item.get("template")
            )
            if detail:
                lines.append(f"  - {file_name}: {detail}")
            else:
                lines.append(f"  - {file_name}")

    output_text = "\n".join(lines)
    print(output_text)

    if args.output_file and args.output_file != "-":
        Path(args.output_file).write_text(output_text + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
