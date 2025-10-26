#!/usr/bin/env python3
"""
Submit a Sora generation job using grounded meme cluster metadata, poll until
completion, and download the resulting video. If the OpenAI response schema ever
changes, the raw payload is saved to `last_video_status.json` for inspection.
"""

import json
import os
import time
import urllib.request
from pathlib import Path
from typing import Any, Iterable

from openai import OpenAI


INPUT_FILE = Path("all_last_results.json")
OUTPUT_VIDEO = Path("meme_output.mp4")
STATUS_SNAPSHOT = Path("last_video_status.json")
POLL_SECONDS = 10
MODEL_NAME = "sora-2"
VIDEO_DURATION_SECONDS = "8"
VIDEO_RESOLUTION = "720x1280"


def _model_to_dict(obj: Any) -> Any:
    """Convert OpenAI SDK objects to plain Python structures."""
    if isinstance(obj, dict):
        return {k: _model_to_dict(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_model_to_dict(item) for item in obj]

    model_dump = getattr(obj, "model_dump", None)
    if callable(model_dump):
        return _model_to_dict(model_dump())

    json_method = getattr(obj, "json", None)
    if callable(json_method):
        try:
            return json.loads(json_method())
        except Exception:
            pass

    return obj


def _find_video_urls(payload: Any) -> Iterable[str]:
    """Walk a nested payload looking for potential download URLs."""
    if isinstance(payload, dict):
        for key, value in payload.items():
            if isinstance(value, str) and value.startswith("http"):
                if key.endswith("url") or value.endswith(".mp4"):
                    yield value
            else:
                yield from _find_video_urls(value)
    elif isinstance(payload, list):
        for item in payload:
            yield from _find_video_urls(item)


def _download_video(url: str, destination: Path) -> None:
    with urllib.request.urlopen(url) as response:
        data = response.read()
    destination.write_bytes(data)


def build_prompt(data: dict) -> str:
    example_meme = data.get("example_meme", {})
    analysis = example_meme.get("analysis", {})

    description = analysis.get("description", "")
    humor = analysis.get("humor", "")
    topic = analysis.get("topic", "")
    template = analysis.get("template", "")
    sound_desc = analysis.get("sound_description", "")

    summary_parts = []
    for field, entry in data.items():
        if isinstance(entry, dict) and "chosen_cluster" in entry:
            label = entry.get("cluster_label") or ""
            summary_parts.append(f"{field}: {label}")

    cluster_summary = "\n".join(summary_parts)

    return f"""
Generate a short, visually engaging meme video inspired by the following attributes:

**Meme Description:**
{description}

**Humor Style:** {humor}
**Topic:** {topic}
**Visual Template:** {template}
**Audio Style:** {sound_desc}

**Cluster Summary Context:**
{cluster_summary}

The result should look like a modern short-form meme (TikTok-style), 5–10 seconds long,
with attention-grabbing pacing, bold caption overlays, and sounds that match the chaotic, humorous tone.
"""


def main() -> int:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("❌ Missing OPENAI_API_KEY in environment.")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"{INPUT_FILE} not found. Run decide_best_part_2.py first.")

    data = json.loads(INPUT_FILE.read_text(encoding="utf-8"))
    prompt = build_prompt(data)

    client = OpenAI(api_key=api_key)

    try:
        print("🎬 Submitting video generation request...")
        job = client.videos.create(
            model=MODEL_NAME,
            prompt=prompt,
            seconds=VIDEO_DURATION_SECONDS,
            size=VIDEO_RESOLUTION,
        )

        print(job.id)

        job_id = getattr(job, "id", None)
        if not job_id:
            raise RuntimeError(f"Unexpected response when creating job: {job}")

        print(f"🕐 Job submitted: {job_id}, waiting for completion...")

        while True:
            status = client.videos.retrieve(job_id)
            print(job.id)
            print(status)
            print()
            state = getattr(status, "status", None) or getattr(status, "state", None)

            if state in ("completed", "succeeded", "ready"):
                print("✅ Video generation complete!")
                break
            if state in ("failed", "error"):
                STATUS_SNAPSHOT.write_text(
                    json.dumps(_model_to_dict(status), indent=2),
                    encoding="utf-8",
                )
                raise RuntimeError(f"❌ Generation failed. See {STATUS_SNAPSHOT}.")

            print(f"⏳ Status: {state or 'pending'}... waiting {POLL_SECONDS}s")
            time.sleep(POLL_SECONDS)

        status_dict = _model_to_dict(status)
        video_urls = list(_find_video_urls(status_dict))
        if not video_urls:
            STATUS_SNAPSHOT.write_text(
                json.dumps(status_dict, indent=2),
                encoding="utf-8",
            )
            raise ValueError(
                "❌ No video URL found in response. Saved payload to last_video_status.json for debugging."
            )

        video_url = video_urls[0]
        
        print(f"⬇️  Downloading video from {video_url}")
        _download_video(video_url, OUTPUT_VIDEO)
        print(f"✅ Meme video saved to: {OUTPUT_VIDEO}")

    except Exception as exc:
        print(f"❌ Error generating video with Sora API: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())