#!/usr/bin/env python3
"""
Lightweight Flask wrapper for the image pipeline orchestrator.

POST /pipeline/run
{
  "question": "...",                # required
  "start_from": "query" | "3",      # optional
  "top_k": 3,                       # optional overrides
  "model": "gemini-2.5-flash-lite", # optional overrides
  "random_count": 2,
  "random_seed": 42,
  "no_random_images": true,
  "dry_run": false
}
"""

from __future__ import annotations

import os
import threading
import uuid
from pathlib import Path
from typing import Dict, Optional

from flask import Flask, jsonify, render_template, request
import subprocess
import json


app = Flask(__name__)

REPO_ROOT = Path(__file__).resolve().parent
PIPELINE_SCRIPT = REPO_ROOT / "image-pipeline-main.py"
PIPELINE_DIR = REPO_ROOT / "image-pipeline"
LOGS_ROOT = PIPELINE_DIR / "logs"
STATUS_ROOT = PIPELINE_DIR


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _build_command(
    *,
    question: str,
    status_path: Path,
    logs_dir: Path,
    start_from: Optional[str],
    overrides: Dict[str, Optional[str]],
) -> list[str]:
    cmd = [
        "python3",
        str(PIPELINE_SCRIPT),
        "--question",
        question,
        "--status-file",
        str(status_path),
        "--logs-dir",
        str(logs_dir),
    ]
    if start_from:
        cmd.extend(["--start-from", start_from])

    for key, value in overrides.items():
        if value is None:
            continue
        if value == "":
            cmd.append(f"--{key}")
        else:
            cmd.extend([f"--{key}", str(value)])
    return cmd


def _launch_pipeline_async(command: list[str]) -> None:
    def runner() -> None:
        env = os.environ.copy()
        existing = env.get("PYTHONPATH")
        env["PYTHONPATH"] = os.pathsep.join(
            [str(REPO_ROOT)] + ([existing] if existing else [])
        )
        subprocess.run(
            command,
            cwd=str(REPO_ROOT),
            env=env,
            check=False,
        )

    threading.Thread(target=runner, daemon=True).start()


@app.post("/pipeline/run")
def run_pipeline() -> tuple:
    payload = request.get_json(silent=True) or {}
    question = payload.get("question")
    if not question:
        return jsonify({"error": "Missing required field 'question'."}), 400

    start_from = payload.get("start_from")

    run_id = uuid.uuid4().hex[:12]
    logs_dir = LOGS_ROOT / run_id
    status_file = STATUS_ROOT / f"pipeline_status_{run_id}.json"
    _ensure_dir(logs_dir)
    _ensure_dir(status_file.parent)

    overrides: Dict[str, Optional[str]] = {}
    if "top_k" in payload:
        overrides["top-k"] = payload["top_k"]
    if "model" in payload:
        overrides["model"] = payload["model"]
    if "random_count" in payload:
        overrides["random-count"] = payload["random_count"]
    if "random_seed" in payload:
        overrides["random-seed"] = payload["random_seed"]
    if payload.get("no_random_images"):
        overrides["no-random-images"] = ""
    if payload.get("dry_run"):
        overrides["dry-run"] = ""

    command = _build_command(
        question=question,
        status_path=status_file,
        logs_dir=logs_dir,
        start_from=start_from,
        overrides=overrides,
    )
    _launch_pipeline_async(command)

    return (
        jsonify(
            {
                "run_id": run_id,
                "command": command,
                "status_file": str(status_file),
                "logs_dir": str(logs_dir),
            }
        ),
        202,
    )


@app.get("/")
def index() -> str:
    return render_template("index.html")


@app.get("/pipeline/status/<run_id>")
def pipeline_status(run_id: str):
    path = STATUS_ROOT / f"pipeline_status_{run_id}.json"
    if not path.exists():
        return jsonify({"error": "status not found"}), 404
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return jsonify({"error": f"failed to parse status: {exc}"}), 500
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
