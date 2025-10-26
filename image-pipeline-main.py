#!/usr/bin/env python3
"""
Orchestrate the image pipeline end-to-end and emit progress updates as JSON.

The pipeline stitches together the standalone scripts under ``image-pipeline/``
and records status snapshots after every transition so a UI can reflect live
progress.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
import time
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional


def iso_now() -> str:
    """Return an ISO-8601 UTC timestamp without microseconds."""
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def ensure_directory(path: Path) -> None:
    """Create the directory at ``path`` if it does not already exist."""
    path.mkdir(parents=True, exist_ok=True)


def to_shell_command(parts: List[str]) -> str:
    """Render a command list so it is easy to read in logs and status files."""
    return " ".join(shlex.quote(part) for part in parts)


def write_status(
    status_path: Path,
    *,
    overall_status: str,
    current_step_index: Optional[int],
    steps_state: List[Dict[str, object]],
    run_info: Dict[str, object],
) -> None:
    """Persist the latest pipeline status for external consumers."""
    payload: Dict[str, object] = {
        "overall_status": overall_status,
        "updated_at": iso_now(),
        "current_step_index": current_step_index,
        "current_step_key": None,
        "current_step_title": None,
        "steps": steps_state,
    }
    if current_step_index is not None and 0 <= current_step_index < len(steps_state):
        payload["current_step_key"] = steps_state[current_step_index]["key"]
        payload["current_step_title"] = steps_state[current_step_index]["title"]
    payload.update(run_info)
    status_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True))


@dataclass
class RunContext:
    root_dir: Path
    pipeline_dir: Path
    status_path: Path
    logs_dir: Path
    query_output: Path
    augmented_output: Path
    meme_image_output: Path
    meme_image_output: Path


StepBuilder = Callable[[argparse.Namespace, RunContext], List[str]]


@dataclass
class StepConfig:
    key: str
    title: str
    command_builder: StepBuilder
    workdir: Path


def build_generate_descriptions_command(_: argparse.Namespace, ctx: RunContext) -> List[str]:
    return [sys.executable, str(ctx.pipeline_dir / "generate_descriptions.py")]


def build_vector_db_command(_: argparse.Namespace, ctx: RunContext) -> List[str]:
    return [sys.executable, str(ctx.pipeline_dir / "vectorDB.py")]


def build_translate_command(_: argparse.Namespace, ctx: RunContext) -> List[str]:
    return [sys.executable, str(ctx.pipeline_dir / "translate.py")]


def build_cluster_labels_command(_: argparse.Namespace, ctx: RunContext) -> List[str]:
    return [sys.executable, str(ctx.pipeline_dir / "generate_cluster_labels.py")]


def build_query_command(args: argparse.Namespace, ctx: RunContext) -> List[str]:
    command = [
        sys.executable,
        str(ctx.pipeline_dir / "query_meme_clusters.py"),
        args.question,
        "--top-k",
        str(args.top_k),
        "--model",
        args.model,
        "--output-file",
        str(ctx.query_output),
    ]
    if not args.no_random_images:
        command.append("--with-random-images")
        command.extend(["--random-count", str(args.random_count)])
        if args.random_seed is not None:
            command.extend(["--random-seed", str(args.random_seed)])
    return command


def build_augment_command(_: argparse.Namespace, ctx: RunContext) -> List[str]:
    return [
        sys.executable,
        str(ctx.pipeline_dir / "augment_output_with_centroid.py"),
        "--input-file",
        str(ctx.query_output),
        "--output-file",
        str(ctx.augmented_output),
    ]


def build_generate_meme_command(args: argparse.Namespace, ctx: RunContext) -> List[str]:
    command = [
        sys.executable,
        str(ctx.root_dir / "generate_meme_image_from_refs.py"),
        "--input",
        str(ctx.augmented_output),
        "--output",
        str(ctx.meme_image_output),
        "--brand",
        args.meme_brand,
        "--tone",
        args.meme_tone,
        "--model",
        args.meme_model,
    ]
    if args.meme_product:
        command.extend(["--product", args.meme_product])
    if args.meme_extra:
        command.extend(["--extra", args.meme_extra])
    return command


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the image pipeline end-to-end with progress tracking.",
    )
    parser.add_argument(
        "--question",
        required=True,
        help="User question for query_meme_clusters.py.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="How many clusters to include as Gemini context (default: 3).",
    )
    parser.add_argument(
        "--model",
        default="gemini-2.5-flash-lite",
        help="Gemini model name (default: gemini-2.5-flash-lite).",
    )
    parser.add_argument(
        "--status-file",
        help="Where to write the pipeline status JSON (default: image-pipeline/pipeline_status.json).",
    )
    parser.add_argument(
        "--logs-dir",
        help="Directory for per-step logs (default: image-pipeline/logs).",
    )
    parser.add_argument(
        "--query-output",
        help="File path for the Gemini query output (default: image-pipeline/output.txt).",
    )
    parser.add_argument(
        "--augmented-output",
        help="File path for the centroid-augmented output (default: image-pipeline/output_with_centroid.json).",
    )
    parser.add_argument(
        "--meme-image-output",
        help="File path for the generated meme image (default: image-pipeline/meme.png).",
    )
    parser.add_argument(
        "--random-count",
        type=int,
        default=2,
        help="Random image suggestions per category (default: 2).",
    )
    parser.add_argument(
        "--random-seed",
        type=int,
        help="Optional seed for random image sampling.",
    )
    parser.add_argument(
        "--no-random-images",
        action="store_true",
        help="Disable random image sampling in the Gemini query step.",
    )
    parser.add_argument(
        "--start-from",
        help=(
            "Step index (1-based) or step key to resume from "
            "(default: run all steps from the beginning)."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned steps without executing them.",
    )
    parser.add_argument(
        "--meme-brand",
        default="Lululemon",
        help="Brand name passed to generate_meme_image_from_refs.py (default: Lululemon).",
    )
    parser.add_argument(
        "--meme-product",
        help="Optional product name for meme generation.",
    )
    parser.add_argument(
        "--meme-tone",
        default="playfully aspirational with dry humor",
        help="Tone description for meme generation.",
    )
    parser.add_argument(
        "--meme-extra",
        help="Extra instructions for meme generation.",
    )
    parser.add_argument(
        "--meme-model",
        default="gpt-image-1",
        help="OpenAI image model to use when generating the meme (default: gpt-image-1).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    root_dir = Path(__file__).resolve().parent
    pipeline_dir = root_dir / "image-pipeline"
    if not pipeline_dir.exists():
        print(f"error: pipeline directory not found: {pipeline_dir}", file=sys.stderr)
        return 1

    if args.random_count < 1 and not args.no_random_images:
        print("error: --random-count must be at least 1 when random images are enabled.", file=sys.stderr)
        return 1

    status_path = Path(args.status_file) if args.status_file else pipeline_dir / "pipeline_status.json"
    logs_dir = Path(args.logs_dir) if args.logs_dir else pipeline_dir / "logs"
    query_output = Path(args.query_output) if args.query_output else pipeline_dir / "output.txt"
    augmented_output = Path(args.augmented_output) if args.augmented_output else pipeline_dir / "output_with_centroid.json"
    meme_image_output = Path(args.meme_image_output) if args.meme_image_output else pipeline_dir / "meme.png"

    ensure_directory(status_path.parent)
    ensure_directory(logs_dir)
    ensure_directory(query_output.parent)
    ensure_directory(augmented_output.parent)
    ensure_directory(meme_image_output.parent)

    ctx = RunContext(
        root_dir=root_dir,
        pipeline_dir=pipeline_dir,
        status_path=status_path,
        logs_dir=logs_dir,
        query_output=query_output,
        augmented_output=augmented_output,
        meme_image_output=meme_image_output,
    )

    steps: List[StepConfig] = [
        StepConfig(
            key="descriptions",
            title="Generate meme descriptions",
            command_builder=build_generate_descriptions_command,
            workdir=pipeline_dir,
        ),
        StepConfig(
            key="vector-db",
            title="Build embedding indexes and clusters",
            command_builder=build_vector_db_command,
            workdir=pipeline_dir,
        ),
        StepConfig(
            key="translate",
            title="Translate cluster report to JSON",
            command_builder=build_translate_command,
            workdir=pipeline_dir,
        ),
        StepConfig(
            key="labels",
            title="Generate cluster labels",
            command_builder=build_cluster_labels_command,
            workdir=pipeline_dir,
        ),
        StepConfig(
            key="query",
            title="Query clusters with Gemini",
            command_builder=build_query_command,
            workdir=pipeline_dir,
        ),
        StepConfig(
            key="augment",
            title="Augment query output with centroid data",
            command_builder=build_augment_command,
            workdir=pipeline_dir,
        ),
        StepConfig(
            key="generate-meme",
            title="Generate final meme image",
            command_builder=build_generate_meme_command,
            workdir=root_dir,
        ),
    ]

    def resolve_start_index(raw: Optional[str]) -> int:
        if raw is None or not raw.strip():
            return 0
        value = raw.strip()
        if value.isdigit():
            index = int(value) - 1
        else:
            index = next((idx for idx, step in enumerate(steps) if step.key == value), -1)
        if index < 0 or index >= len(steps):
            raise ValueError(
                f"invalid --start-from value '{value}'. Use 1-{len(steps)} or one of: "
                + ", ".join(step.key for step in steps),
            )
        return index

    try:
        start_index = resolve_start_index(args.start_from)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    base_env = os.environ.copy()
    pythonpath_entries = [str(root_dir)]
    existing_pythonpath = base_env.get("PYTHONPATH")
    if existing_pythonpath:
        pythonpath_entries.append(existing_pythonpath)
    base_env["PYTHONPATH"] = os.pathsep.join(pythonpath_entries)

    step_logs: List[Path] = []
    steps_state: List[Dict[str, object]] = []
    for index, step in enumerate(steps, start=1):
        log_path = logs_dir / f"{index:02d}_{step.key}.log"
        step_logs.append(log_path)
        try:
            log_reference = str(log_path.relative_to(root_dir))
        except ValueError:
            log_reference = str(log_path)
        steps_state.append(
            {
                "key": step.key,
                "title": step.title,
                "status": "skipped" if index - 1 < start_index else "pending",
                "log_file": log_reference,
                "command": None,
                "started_at": None,
                "finished_at": None,
                "duration_seconds": None,
                "returncode": None,
                "error": None,
            }
        )

    run_started_at = iso_now()
    run_id = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    run_info: Dict[str, object] = {
        "run_id": run_id,
        "started_at": run_started_at,
        "question": args.question,
        "status_file": str(status_path),
        "logs_dir": str(logs_dir),
        "query_output": str(query_output),
        "augmented_output": str(augmented_output),
        "start_from_index": start_index + 1,
        "start_from_key": steps[start_index].key,
        "meme_image_output": str(meme_image_output),
    }

    write_status(
        status_path,
        overall_status="pending",
        current_step_index=None,
        steps_state=steps_state,
        run_info=run_info,
    )

    if args.dry_run:
        print("Dry run: planned steps")
        for idx in range(start_index, len(steps)):
            step = steps[idx]
            command = step.command_builder(args, ctx)
            print(f"{idx + 1:02d}. {step.title}")
            print(f"    cwd: {step.workdir}")
            print(f"    cmd: {to_shell_command(command)}")
        return 0

    overall_status = "running"
    current_step_index: Optional[int] = None

    for idx, (step, step_state) in enumerate(zip(steps, steps_state)):
        if idx < start_index:
            continue
        current_step_index = idx
        command = step.command_builder(args, ctx)
        command_string = to_shell_command(command)
        step_state["command"] = command_string
        step_state["status"] = "running"
        step_state["started_at"] = iso_now()
        write_status(
            status_path,
            overall_status=overall_status,
            current_step_index=current_step_index,
            steps_state=steps_state,
            run_info=run_info,
        )

        ensure_directory(step_logs[idx].parent)
        start_time = time.time()
        try:
            with step_logs[idx].open("w", encoding="utf-8") as log_file:
                log_file.write(f"# Step: {step.title}\n")
                log_file.write(f"# Command: {command_string}\n")
                log_file.write(f"# Started: {step_state['started_at']}\n\n")
                log_file.flush()
                result = subprocess.run(
                    command,
                    cwd=str(step.workdir),
                    env=base_env,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
        except KeyboardInterrupt:
            duration = time.time() - start_time
            step_state["duration_seconds"] = round(duration, 3)
            step_state["finished_at"] = iso_now()
            step_state["returncode"] = None
            step_state["status"] = "failed"
            step_state["error"] = "Interrupted by user"
            overall_status = "failed"
            write_status(
                status_path,
                overall_status=overall_status,
                current_step_index=None,
                steps_state=steps_state,
                run_info=run_info,
            )
            print("\nPipeline interrupted by user.", file=sys.stderr)
            return 130

        duration = time.time() - start_time
        step_state["duration_seconds"] = round(duration, 3)
        step_state["finished_at"] = iso_now()
        step_state["returncode"] = result.returncode

        if result.returncode == 0:
            step_state["status"] = "completed"
            current_step_index = None
            write_status(
                status_path,
                overall_status=overall_status,
                current_step_index=None,
                steps_state=steps_state,
                run_info=run_info,
            )
            continue

        step_state["status"] = "failed"
        step_state["error"] = f"Command exited with code {result.returncode}"
        overall_status = "failed"
        current_step_index = None
        write_status(
            status_path,
            overall_status=overall_status,
            current_step_index=None,
            steps_state=steps_state,
            run_info=run_info,
        )
        print(
            f"Pipeline halted at step {idx + 1} ({step.title}). See {step_logs[idx]} for details.",
            file=sys.stderr,
        )
        return result.returncode or 1

    overall_status = "completed"
    write_status(
        status_path,
        overall_status=overall_status,
        current_step_index=None,
        steps_state=steps_state,
        run_info=run_info,
    )
    print("Pipeline completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
