"""
Image pipeline orchestrator that replicates image-pipeline-main.py exactly.
"""

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
from typing import Callable, Dict, List, Optional, Any

from config import CLUSTER_DATA_PATHS, DEFAULT_BRAND, DEFAULT_TONE, OPENAI_MODELS, GEMINI_MODEL
from utils import timing_decorator


def iso_now() -> str:
    """Return an ISO-8601 UTC timestamp without microseconds."""
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def ensure_directory(path: Path) -> None:
    """Create the directory at ``path`` if it does not already exist."""
    path.mkdir(parents=True, exist_ok=True)


def to_shell_command(parts: List[str]) -> str:
    """Render a command list so it is easy to read in logs and status files."""
    return " ".join(shlex.quote(part) for part in parts)


@dataclass
class RunContext:
    root_dir: Path
    pipeline_dir: Path
    status_path: Path
    logs_dir: Path
    query_output: Path
    augmented_output: Path
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


class ImagePipelineOrchestrator:
    """Replicates image-pipeline-main.py exactly."""
    
    def __init__(self):
        self.backend_dir = Path(__file__).parent
        self.pipeline_dir = self.backend_dir / "data" / "image-pipeline"
        
    def create_args(self, question: str, **kwargs) -> argparse.Namespace:
        """Create args object with defaults matching image-pipeline-main.py."""
        defaults = {
            "question": question,
            "top_k": 3,
            "model": GEMINI_MODEL,
            "random_count": 2,
            "random_seed": None,
            "no_random_images": False,
            "meme_brand": DEFAULT_BRAND,
            "meme_product": None,
            "meme_tone": DEFAULT_TONE,
            "meme_extra": None,
            "meme_model": OPENAI_MODELS["image_generation"],
        }
        defaults.update(kwargs)
        
        # Create a mock argparse.Namespace
        args = argparse.Namespace()
        for key, value in defaults.items():
            setattr(args, key, value)
        return args
    
    def create_context(self, args: argparse.Namespace) -> RunContext:
        """Create RunContext matching image-pipeline-main.py exactly."""
        root_dir = self.backend_dir
        pipeline_dir = self.pipeline_dir
        
        # Use the same paths as the original pipeline
        query_output = pipeline_dir / "output.txt"
        augmented_output = pipeline_dir / "output_with_centroid.json"
        meme_image_output = pipeline_dir / "meme.png"
        logs_dir = pipeline_dir / "logs"
        status_path = pipeline_dir / "pipeline_status.json"
        
        return RunContext(
            root_dir=root_dir,
            pipeline_dir=pipeline_dir,
            status_path=status_path,
            logs_dir=logs_dir,
            query_output=query_output,
            augmented_output=augmented_output,
            meme_image_output=meme_image_output,
        )
    
    def get_steps(self) -> List[StepConfig]:
        """Get steps matching image-pipeline-main.py exactly."""
        root_dir = self.backend_dir
        pipeline_dir = self.pipeline_dir
        
        return [
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
    
    @timing_decorator
    def run_pipeline(self, question: str, start_from: int = 4, **kwargs) -> Dict[str, Any]:
        """
        Run the image pipeline exactly like image-pipeline-main.py.
        
        Args:
            question: User's question/prompt
            start_from: Step index to start from (4 = skip steps 1-4, use pre-generated data)
            **kwargs: Additional arguments
            
        Returns:
            Dict containing the generated image path and metadata
        """
        try:
            # Create args and context exactly like image-pipeline-main.py
            args = self.create_args(question, **kwargs)
            ctx = self.create_context(args)
            steps = self.get_steps()
            
            # Start from specified step (default 4 = query step)
            start_index = start_from
            
            # Set up environment exactly like image-pipeline-main.py
            base_env = os.environ.copy()
            pythonpath_entries = [str(ctx.root_dir)]
            existing_pythonpath = base_env.get("PYTHONPATH")
            if existing_pythonpath:
                pythonpath_entries.append(existing_pythonpath)
            base_env["PYTHONPATH"] = os.pathsep.join(pythonpath_entries)
            
            print(f"🚀 Starting image pipeline from step {start_index + 1} ({steps[start_index].key})")
            
            # Run steps exactly like image-pipeline-main.py
            for idx in range(start_index, len(steps)):
                step = steps[idx]
                command = step.command_builder(args, ctx)
                command_string = to_shell_command(command)
                
                print(f"📋 Step {idx + 1}: {step.title}")
                print(f"   Command: {command_string}")
                
                start_time = time.time()
                try:
                    result = subprocess.run(
                        command,
                        cwd=str(step.workdir),
                        env=base_env,
                        capture_output=True,
                        text=True,
                    )
                    
                    duration = time.time() - start_time
                    
                    if result.returncode == 0:
                        print(f"✅ Step {idx + 1} completed in {duration:.2f}s")
                        continue
                    else:
                        print(f"❌ Step {idx + 1} failed with code {result.returncode}")
                        print(f"   Error: {result.stderr}")
                        raise RuntimeError(f"Step {idx + 1} ({step.title}) failed: {result.stderr}")
                        
                except Exception as e:
                    print(f"❌ Step {idx + 1} error: {e}")
                    raise
            
            # Check if meme image was generated
            if not ctx.meme_image_output.exists():
                raise RuntimeError("Meme image was not generated")
            
            print(f"🎉 Pipeline completed successfully!")
            print(f"📁 Generated meme: {ctx.meme_image_output}")
            
            return {
                "status": "success",
                "content_type": "image",
                "file_path": str(ctx.meme_image_output),
                "metadata": {
                    "question": question,
                    "steps_completed": len(steps) - start_index,
                    "pipeline_version": "image-pipeline-main.py-replica"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Pipeline failed: {str(e)}",
                "code": "PIPELINE_FAILED"
            }
