"""
Template utilities for prompting Google Gemini models.

This module keeps the Gemini dependency optional so it can be imported without
installing google-generativeai. Callers are expected to install the package and
set the GEMINI_API_KEY environment variable before using the runtime pipeline.
"""

from __future__ import annotations
import os


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyDKBsOH3EWjxKGWpOE0PWDDIIbj1UwjdLI"

def get_gemini_api_key() -> str:
    """Retrieve the Gemini API key from the environment or raise if missing."""
    api_key = GEMINI_API_KEY
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set. "
            "Set it to your Google Gemini API key before using the GeminiPipeline."
        )
    return api_key

import json
import pathlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union

try:  # The pipeline can still build prompts without the client installed.
    import google.generativeai as genai  # type: ignore
except ImportError:  # pragma: no cover - only executed when the dependency is missing.
    genai = None  # type: ignore[assignment]


@dataclass
class PromptTemplate:
    """Structured representation of a Gemini prompt."""

    name: str
    system_instruction: str
    task: str
    input_placeholder: str = "{input}"
    guidelines: List[str] = field(default_factory=list)
    output_schema_hint: Optional[str] = None

    def build_user_message(self, *, context: Optional[str], user_input: str) -> str:
        """
        Render a user-facing prompt string using the provided context and input.

        The placeholder defined by input_placeholder is replaced with user_input.
        """
        blocks: List[str] = []
        if context:
            blocks.append(f"Context:\n{context.strip()}")
        blocks.append(f"Task:\n{self.task.strip()}")
        if self.guidelines:
            numbered = "\n".join(f"{idx+1}. {rule}" for idx, rule in enumerate(self.guidelines))
            blocks.append(f"Guidelines:\n{numbered}")
        rendered_input = self.input_placeholder.replace("{input}", user_input.strip())
        blocks.append(f"Input:\n{rendered_input}")
        if self.output_schema_hint:
            blocks.append(f"Expected Output:\n{self.output_schema_hint.strip()}")
        return "\n\n".join(blocks)

    def build_contents(self, *, context: Optional[str], user_input: str) -> List[Dict[str, List[Dict[str, str]]]]:
        """
        Build a Gemini-compatible content payload.

        Returns the list structure expected by GenerativeModel.generate_content.
        """
        return [
            {
                "role": "user",
                "parts": [{"text": self.build_user_message(context=context, user_input=user_input)}],
            }
        ]


class GeminiPipeline:
    """
    Convenience wrapper that ties together prompt templates and the Gemini client.

    Example:
        template = PromptTemplate(
            name="news-summarizer",
            system_instruction="You are a precise analyst who writes factual summaries.",
            task="Summarize the headline and key facts for the given article.",
            guidelines=[
                "Keep the summary under 120 words.",
                "Highlight named entities and locations.",
                "End with one bullet of potential follow-up questions.",
            ],
            output_schema_hint="- Headline: ...\\n- Summary: ...\\n- Follow-up: ...",
        )
        pipeline = GeminiPipeline(model_name="gemini-2.5-flash", template=template)
        response = pipeline.generate(user_input="...", context="...")
    """

    def __init__(
        self,
        *,
        model_name: str = "gemini-2.5-flash",
        template: PromptTemplate,
        generation_config: Optional[Dict] = None,
        safety_settings: Optional[List[Dict]] = None,
        api_key: Optional[str] = None,
    ) -> None:
        self.template = template
        self.model_name = model_name
        self.generation_config = generation_config or {
            "temperature": 0.2,
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 10000,
        }
        self.safety_settings = safety_settings
        self.api_key = api_key or get_gemini_api_key()
        if genai is None:
            raise RuntimeError(
                "google-generativeai is not installed. Install it with "
                "`pip install google-generativeai` before creating GeminiPipeline."
            )
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings,
            system_instruction=self.template.system_instruction,
        )

    def generate(self, *, user_input: str, context: Optional[str] = None) -> str:
        """
        Run the configured template and return the response text.

        The method raises if the Gemini response is empty or the client returns an error.
        """
        payload = self.template.build_contents(context=context, user_input=user_input)
        result = self.model.generate_content(payload)
        try:
            return _extract_text_from_result(result)
        except ValueError as exc:  # pragma: no cover - depends on remote service behaviour.
            raise RuntimeError(str(exc)) from exc


def default_template() -> PromptTemplate:
    """
    Provide a ready-to-use template for turning insights into an actionable viral video plan.
    """
    return PromptTemplate(
        name="viral-video-plan",
        system_instruction="You are a trend strategist who converts audience insights into actionable viral video briefs.",
        task="Design the hottest trending video concept based on the provided context, with clear execution steps.",
        guidelines=[
            "Ground every recommendation in the supplied context; flag any missing information.",
            "Deliver a hook, narrative arc, and visual direction that feel fresh yet achievable.",
            "Lay out the production plan as concrete, sequential actions (pre-production, production, post).",
            "Recommend distribution platforms, posting cadence, and engagement tactics.",
            "Define measurable success metrics and experimentation ideas with a complete and finished plan.",
            "Make it related to duolingo",
        ],
        output_schema_hint=(
            "Working Title: ...\n"
            "Concept Hook: ...\n"
            "Production Plan:\n"
            "- Step 1: ...\n"
            "- Step 2: ...\n"
            "Platform Strategy: ...\n"
            "Engagement & CTA: ...\n"
            "Metrics & Experiments: ...\n"
            "Risks or Unknowns: ..."
        ),
    )


def _load_embedding_file(path: pathlib.Path) -> Dict:
    raw = path.read_text(encoding="utf-8")
    return json.loads(raw)


def _format_frame_lines(frames: List[Dict], limit: Optional[int]) -> Tuple[str, int]:
    subset = frames[:limit] if limit else frames
    lines = []
    for frame in subset:
        timestamp = frame.get("timestamp_seconds", 0.0) if isinstance(frame, dict) else 0.0
        description = (
            frame.get("description")
            if isinstance(frame, dict)
            else str(frame)
        ) or "<missing description>"
        lines.append(f"{timestamp:6.2f}s | {description}")
    return "\n".join(lines), len(subset)


def _build_context_from_record(record: Dict, *, max_frames: Optional[int]) -> str:
    blocks: List[str] = []
    aggregate = record.get("aggregate_embedding")
    if isinstance(aggregate, list):
        blocks.append(f"Aggregate embedding length: {len(aggregate)}")
    frames = record.get("frames")
    if isinstance(frames, list):
        frame_section, frame_count = _format_frame_lines(frames, max_frames)
        if frame_section:
            blocks.append(f"Frame summaries (showing {frame_count}):\n{frame_section}")
    skip_keys = {"aggregate_embedding", "frames"}
    details: List[str] = []
    for key, value in record.items():
        if key in skip_keys:
            continue
        if value is None:
            continue
        formatted = _stringify_value(value)
        if formatted:
            details.append(f"{key}: {formatted}")
    if details:
        blocks.append("Record details:\n" + "\n".join(details))
    return "\n\n".join(blocks)


def _infer_label(record: Dict, idx: int) -> str:
    for key in ("id", "video_id", "title", "name", "source", "topic"):
        value = record.get(key)
        if isinstance(value, str) and value:
            return value
    description = record.get("description")
    if isinstance(description, str) and description:
        snippet = description.strip()
        if len(snippet) > 40:
            snippet = snippet[:37] + "..."
        return snippet
    return f"Item {idx}"


def _stringify_value(value) -> str:
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    if isinstance(value, list):
        if not value:
            return ""
        if all(isinstance(item, (str, int, float, bool)) for item in value):
            return "; ".join(str(item) for item in value)
        return f"{len(value)} items"
    if isinstance(value, dict):
        keys = ", ".join(sorted(value.keys()))
        return f"object with keys: {keys}"
    return ""


def build_context_from_embedding(
    data: Union[Dict, List],
    *,
    max_frames: Optional[int] = 20,
) -> str:
    """
    Convert a video embedding JSON dict into a context block for prompting Gemini.
    """
    if isinstance(data, dict):
        return _build_context_from_record(data, max_frames=max_frames)

    if isinstance(data, list):
        if data and all(isinstance(item, dict) and "timestamp_seconds" in item for item in data):
            frame_section, frame_count = _format_frame_lines(data, max_frames)
            if frame_section:
                return f"Frame summaries (showing {frame_count}):\n{frame_section}"
            return ""

        contexts: List[str] = []
        for idx, item in enumerate(data, start=1):
            if not isinstance(item, dict):
                continue
            label = _infer_label(item, idx)
            inner = build_context_from_embedding(item, max_frames=max_frames)
            if inner:
                contexts.append(f"{label}:\n{inner}")
        return "\n\n".join(contexts)

    return ""


def _extract_text_from_result(result) -> str:
    if hasattr(result, "text") and result.text:
        return result.text

    prompt_feedback = getattr(result, "prompt_feedback", None)
    prompt_feedback_reason = None
    if prompt_feedback is not None:
        prompt_feedback_reason = getattr(prompt_feedback, "block_reason", None) or (
            prompt_feedback.get("blockReason") if isinstance(prompt_feedback, dict) else None
        )

    candidates = getattr(result, "candidates", None)
    finish_reasons: List[str] = []
    if candidates:
        for candidate in candidates:
            finish_reason = getattr(candidate, "finish_reason", None) or (
                candidate.get("finishReason") if isinstance(candidate, dict) else None
            )
            if finish_reason is not None:
                finish_reasons.append(str(finish_reason))

            content = getattr(candidate, "content", None)
            parts = None
            if content is not None:
                parts = getattr(content, "parts", None) or (
                    content.get("parts") if isinstance(content, dict) else None
                )
            elif isinstance(candidate, dict):
                parts = candidate.get("content")
                if isinstance(parts, dict):
                    parts = parts.get("parts")

            if parts:
                for part in parts:
                    text = getattr(part, "text", None)
                    if text:
                        return text
                    if isinstance(part, dict):
                        text = part.get("text")
                        if text:
                            return text

    details = []
    if finish_reasons:
        details.append(f"finish_reason(s): {', '.join(sorted(set(finish_reasons)))}")
    if prompt_feedback_reason:
        details.append(f"prompt_feedback.block_reason: {prompt_feedback_reason}")
    if not details:
        details.append("no text parts were returned")

    raise ValueError("Gemini response did not include any text (" + "; ".join(details) + ").")


RELAXED_SAFETY_SETTINGS: List[Dict[str, str]] = [
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HARASSMENT_ABUSE", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUAL_CONTENT", "threshold": "BLOCK_NONE"},
]


def relaxed_safety_settings() -> List[Dict[str, str]]:
    """
    Return a copy of relaxed safety settings useful when the default policy blocks content.
    """
    return [dict(item) for item in RELAXED_SAFETY_SETTINGS]


def analyze_embedding_file(
    *,
    file_path: str,
    question: str,
    model_name: str = "gemini-2.5-flash",
    template: Optional[PromptTemplate] = None,
    max_frames: Optional[int] = 20,
    generation_config: Optional[Dict] = None,
    safety_settings: Optional[List[Dict]] = None,
    api_key: Optional[str] = None,
) -> str:
    """
    Load an embedding JSON file, build context, and query Gemini with the provided question.
    """
    data = _load_embedding_file(pathlib.Path(file_path))
    context = build_context_from_embedding(data, max_frames=max_frames)
    prompt_template = template or default_template()
    pipeline = GeminiPipeline(
        model_name=model_name,
        template=prompt_template,
        generation_config=generation_config,
        safety_settings=safety_settings,
        api_key=api_key or get_gemini_api_key(),
    )
    return pipeline.generate(user_input=question, context=context)


__all__ = [
    "PromptTemplate",
    "GeminiPipeline",
    "default_template",
    "relaxed_safety_settings",
    "build_context_from_embedding",
    "analyze_embedding_file",
]

if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Analyze a video embedding JSON file using Gemini."
    )
    parser.add_argument(
        "file_path",
        help="Path to the video embedding JSON file.",
    )
    parser.add_argument(
        "--question",
        default="Provide a detailed video production plan based on the content.",
        help="Question to ask about the video content.",
    )
    parser.add_argument(
        "--model-name",
        default="gemini-2.5-flash",
        help="Gemini model name to use (default: %(default)s).",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=20,
        help="Maximum number of frames to include in context (default: %(default)s).",
    )
    args = parser.parse_args()

    try:
        answer = analyze_embedding_file(
            file_path=args.file_path,
            question=args.question,
            model_name=args.model_name,
            max_frames=args.max_frames,
        )
        print("Gemini Response:\n")
        print(answer)
    except Exception as exc:
        print(f"[error] Analysis failed: {exc}", file=sys.stderr)
        sys.exit(1)
