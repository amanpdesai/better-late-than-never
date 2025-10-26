"""
Interactive helper for querying meme clusters with Google Gemini.

The script ranks clusters based on keyword overlap with the user's question,
builds a compact context from the cluster metadata, and asks Gemini to answer.

Requirements:
    pip install google-generativeai
    export GEMINI_API_KEY="your-key"

Usage:
    python query_meme_clusters.py "Which clusters cover digital culture discourse?"
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

# Ensure the project root is importable so we can reuse the shared Gemini pipeline utilities.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from gemini_pipeline import GeminiPipeline, PromptTemplate  # type: ignore


DATA_DIR = Path(__file__).resolve().parent
CLUSTER_LABELS_PATH = DATA_DIR / "cluster_labels_dict.json"
MEME_CLUSTERS_PATH = DATA_DIR / "meme_clusters.txt"


@dataclass
class ClusterInfo:
    """Cached metadata for a single cluster."""

    cluster_id: int
    description_label: str
    humor_label: str
    topic_label: str
    template_label: str
    items: List[str]

    @property
    def meme_count(self) -> int:
        return len(self.items)

    def render_context_block(self, *, sample_size: int = 3) -> str:
        """Compress the cluster details into a short context paragraph."""
        sample_items = self.items[:sample_size] if sample_size else self.items
        bullet_lines = "\n".join(f"  • {entry}" for entry in sample_items)
        return (
            f"Cluster {self.cluster_id} "
            f"(≈{self.meme_count} memes)\n"
            f"- Description focus: {self.description_label}\n"
            f"- Humor style: {self.humor_label}\n"
            f"- Topic theme: {self.topic_label}\n"
            f"- Template pattern: {self.template_label}\n"
            f"- Sample memes:\n{bullet_lines}"
        )


def _load_cluster_labels(path: Path) -> Dict[int, Dict[str, str]]:
    """Load per-field labels from cluster_labels_dict.json."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    clusters: Dict[int, Dict[str, str]] = {}
    for field, field_labels in raw.items():
        for cluster_key, label in field_labels.items():
            match = re.search(r"Cluster\s+(\d+)", cluster_key)
            if not match:
                continue
            idx = int(match.group(1))
            clusters.setdefault(idx, {})[field] = label.strip().strip('"')
    return clusters


def _parse_meme_clusters(path: Path) -> Dict[int, List[str]]:
    """Parse the human-formatted meme_clusters.txt into structured bullets."""
    clusters: Dict[int, List[str]] = {}
    current_idx: int | None = None
    bullet_pattern = re.compile(r"^•\s*(.+)")
    header_pattern = re.compile(r"Cluster\s+(\d+)")

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        header_match = header_pattern.search(line)
        if line.startswith("📁") and header_match:
            current_idx = int(header_match.group(1))
            clusters.setdefault(current_idx, [])
            continue
        if current_idx is None:
            continue
        bullet_match = bullet_pattern.match(line)
        if bullet_match:
            clusters[current_idx].append(bullet_match.group(1).strip())
    return clusters


def _normalise_label(data: Dict[str, str], key: str, fallback: str) -> str:
    """Fetch and clean a label string."""
    label = data.get(key, fallback).strip()
    return re.sub(r"\s+", " ", label)


def _build_cluster_infos() -> Dict[int, ClusterInfo]:
    """Combine label metadata and meme listings into ClusterInfo objects."""
    labels_map = _load_cluster_labels(CLUSTER_LABELS_PATH)
    memes_map = _parse_meme_clusters(MEME_CLUSTERS_PATH)

    cluster_infos: Dict[int, ClusterInfo] = {}
    for idx, memes in memes_map.items():
        field_labels = labels_map.get(idx, {})
        cluster_infos[idx] = ClusterInfo(
            cluster_id=idx,
            description_label=_normalise_label(field_labels, "DESCRIPTION ===", "Unknown description"),
            humor_label=_normalise_label(field_labels, "HUMOR ===", "Unknown humor"),
            topic_label=_normalise_label(field_labels, "TOPIC ===", "Unknown topic"),
            template_label=_normalise_label(field_labels, "MEME_TEMPLATE ===", "Unknown template"),
            items=memes,
        )
    return cluster_infos


def _tokenise(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _score_cluster(tokens: List[str], info: ClusterInfo) -> int:
    """Score clusters by keyword overlap (simple term frequency)."""
    if not tokens:
        return 0
    haystack = " ".join(
        [info.description_label, info.humor_label, info.topic_label, info.template_label, " ".join(info.items)]
    ).lower()
    return sum(haystack.count(token) for token in tokens)


def select_top_clusters(cluster_infos: Dict[int, ClusterInfo], query: str, *, limit: int) -> List[ClusterInfo]:
    """Rank clusters and pick the most relevant ones for the question."""
    tokens = _tokenise(query)
    ranked: List[Tuple[int, ClusterInfo]] = []
    for info in cluster_infos.values():
        score = _score_cluster(tokens, info)
        ranked.append((score, info))
    ranked.sort(key=lambda pair: (-pair[0], pair[1].cluster_id))
    top = [info for score, info in ranked if score > 0][:limit]
    if not top:  # fall back to leading clusters to avoid empty context
        return [info for _, info in ranked[:limit]]
    return top


CLUSTER_ANALYST_TEMPLATE = PromptTemplate(
    name="meme-cluster-analyst",
    system_instruction=(
        "You are an expert cultural analyst specialising in online meme trends. "
        "Answer user questions strictly with the supplied cluster context. "
        "If the context is insufficient, give the most relevant answer regarding the closest matching cluster."
    ),
    task=(
        "Interpret the question, highlight any matching clusters, and synthesise insights "
        "grounded in the provided cluster descriptions and meme examples."
    ),
    guidelines=[
        "Reference clusters by number and explain why they are relevant.",
        "Use bullet points when listing clusters or recommendations.",
        "Call out missing information if the context does not contain an answer.",
        "Output only the cluster match numbers, categories, and best image matches in the specified format.",
    ],
    output_schema_hint="- Top Cluster Match Number: <cluster number> \n Cluster Category: <category> \n Best image match: <image URL> \n Second Match Number: <cluster number> \n Second Cluster Category: <category> \n Best image match: <image URL> \n Third Match Number: <cluster number> \n Third Cluster Category: <category> \n Best image match: <image URL>",
)


def build_context(clusters: List[ClusterInfo]) -> str:
    """Concatenate per-cluster blocks to feed Gemini."""
    return "\n\n".join(info.render_context_block() for info in clusters)


def run_query(question: str, *, top_k: int, model: str) -> str:
    """Load data, build context, and query Gemini."""
    cluster_infos = _build_cluster_infos()
    chosen_clusters = select_top_clusters(cluster_infos, question, limit=top_k)
    context = build_context(chosen_clusters)

    pipeline = GeminiPipeline(model_name=model, template=CLUSTER_ANALYST_TEMPLATE)
    return pipeline.generate(user_input=question, context=context)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query meme cluster ideas with Gemini.")
    parser.add_argument("question", help="The question you want to ask about the meme clusters.")
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of top clusters to surface as context (default: 3).",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        help="Gemini model name (default: gemini-2.5-flash or GEMINI_MODEL env var).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    answer = run_query(args.question, top_k=args.top_k, model=args.model)
    print(answer)


if __name__ == "__main__":
    main()
