#!/usr/bin/env python3
"""
Generate a meme image using OpenAI's Images API, grounding the prompt on
cluster references produced by the pipeline.
"""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
from typing import Dict, Iterable, Optional

from openai import OpenAI


DEFAULT_INPUT = Path("image-pipeline") / "output_with_centroid.json"


def _resolve_reference_path(path: Path) -> Path:
    if path.exists():
        return path
    if path.suffix == ".json":
        alt = path.with_suffix(".txt")
        if alt.exists():
            return alt
        alt_root = Path(path.name)
        if alt_root.exists():
            return alt_root
        alt_root_txt = alt_root.with_suffix(".txt")
        if alt_root_txt.exists():
            return alt_root_txt
    raise FileNotFoundError(f"reference file not found: {path}")


def load_references(path: Path) -> Dict[str, Dict]:
    resolved = _resolve_reference_path(path)
    raw = resolved.read_text(encoding="utf-8").strip()
    if not raw:
        raise ValueError(f"reference file is empty: {resolved}")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"failed to parse JSON from {resolved}: {exc}") from exc


def summarise_image(label: str, payload: Optional[Dict[str, str]]) -> Iterable[str]:
    if not payload:
        yield f"- {label}: (missing)"
        return
    description = payload.get("description") or payload.get("topic") or ""
    humor = payload.get("humor")
    template = payload.get("meme_template")
    parts = [f"- {label}: {description.strip()}".strip()]
    if humor:
        parts.append(f"  Humor: {humor.strip()}")
    if template:
        parts.append(f"  Template: {template.strip()}")
    yield from parts


def build_prompt(
    data: Dict[str, Dict],
    *,
    brand: str,
    product: Optional[str],
    tone: str,
    extra_instructions: Optional[str],
) -> str:
    sections: list[str] = []
    sections.append(
        f"Design a fresh, social-ready meme for {brand}{' ' + product if product else ''}. "
        f"Keep the tone {tone} and make it feel native to contemporary meme culture."
    )
    sections.append("Ground the concept in these reference clusters:")

    for category in ("DESCRIPTION", "HUMOR", "TOPIC", "MEME_TEMPLATE"):
        cluster = data.get(category)
        if not cluster:
            sections.append(f"* {category}: (no cluster data)")
            continue
        cluster_id = cluster.get("cluster_id", "?")
        sections.append(f"* {category} cluster {cluster_id}")
        random_lines = list(
            summarise_image("Random example", cluster.get("random_image")),
        )
        centroid_lines = list(
            summarise_image("Centroid example", cluster.get("centroid_image")),
        )
        sections.extend(random_lines)
        sections.extend(centroid_lines)

    sections.append(
        f"Deliver a single, coherent meme concept with visual details and overlaid copy that align with "
        f"the brand voice of {brand} while clearly riffing on the cited templates."
    )
    if extra_instructions:
        sections.append(f"Extra instructions: {extra_instructions}")

    sections.append(
        "Output only the visual description; avoid mentioning this prompt or the JSON explicitly."
    )
    return "\n".join(sections)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a meme image grounded in cluster references.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Path to augmented cluster JSON (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--brand",
        default="Lululemon",
        help="Brand to feature in the meme (default: Lululemon).",
    )
    parser.add_argument(
        "--product",
        help="Optional product focus to weave into the meme.",
    )
    parser.add_argument(
        "--tone",
        default="playfully aspirational with dry humor",
        help="Desired meme tone (default: playfully aspirational with dry humor).",
    )
    parser.add_argument(
        "--extra",
        help="Extra instructions appended to the prompt.",
    )
    parser.add_argument(
        "--model",
        default="gpt-image-1",
        help="OpenAI image model to use (default: gpt-image-1).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("meme.png"),
        help="Where to save the generated image (default: meme.png).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = load_references(args.input)
    prompt = build_prompt(
        data,
        brand=args.brand,
        product=args.product,
        tone=args.tone,
        extra_instructions=args.extra,
    )

    client = OpenAI()
    result = client.images.generate(
        model=args.model,
        prompt=prompt,
    )

    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)
    args.output.write_bytes(image_bytes)
    print(f"Saved meme to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
