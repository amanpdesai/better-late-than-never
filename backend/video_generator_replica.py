"""
Video generator with topic-aware cluster matching.
Enhanced to use semantic cluster matching like the image pipeline.
"""

import json
import os
import re
import sys
import time
import random
from pathlib import Path
from typing import Any, Dict, List

from openai import OpenAI
from config import OPENAI_MODELS, VIDEO_DURATION_SECONDS, VIDEO_RESOLUTION, POLL_SECONDS, CLUSTER_DATA_PATHS

# Add image-pipeline to path so we can import query modules
IMAGE_PIPELINE_DIR = Path(__file__).resolve().parent.parent / "image-pipeline"
if str(IMAGE_PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(IMAGE_PIPELINE_DIR))

# Add project root for gemini_pipeline import
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


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


# Removed old URL-based download functions - now using OpenAI's download_content method


def build_simple_prompt(user_prompt: str) -> str:
    """
    Build a simple, direct prompt using ONLY the user's request.
    No cluster labels, no example_meme attributes - just clean user intent.

    This approach minimizes moderation risk by avoiding any contamination.
    """
    return f"""
Create a short-form meme video (5-10 seconds) for social media.

**Topic:** {user_prompt}

**Requirements:**
- Modern, trendy TikTok/Instagram Reels style
- Fun and engaging visuals
- Upbeat, trendy music or sounds
- Bold text overlays if relevant
- High energy pacing
- Relatable and shareable content

**Style:**
- Keep it light, funny, and positive
- Focus on the specific topic mentioned above
- Use current meme formats and trends
- Make it visually appealing and dynamic

The video should be optimized for social media sharing and appeal to a broad audience.
"""


def build_prompt(data: dict, user_prompt: str = None, cluster_labels: dict = None) -> str:
    """
    Build prompt for Sora API using cluster labels instead of example_meme attributes.

    Args:
        data: Dictionary containing cluster information
        user_prompt: Original user request to ensure topic relevance
        cluster_labels: Dictionary of cluster labels from cluster_labels_dict.json

    NOTE: We now use cluster labels (generic, topic-appropriate) instead of
    example_meme attributes (which may contain off-topic content like guns).
    """
    # Use cluster labels instead of example_meme attributes to avoid contamination
    description = ""
    humor = ""
    topic = ""
    template = ""

    if cluster_labels:
        # Get labels for matched clusters from cluster_labels_dict.json
        # This ensures we use generic, topic-appropriate descriptions
        desc_cluster = data.get("DESCRIPTION", {}).get("chosen_cluster", "")
        humor_cluster = data.get("HUMOR", {}).get("chosen_cluster", "")
        topic_cluster = data.get("TOPIC", {}).get("chosen_cluster", "")
        template_cluster = data.get("MEME_TEMPLATE", {}).get("chosen_cluster", "")

        description = cluster_labels.get("DESCRIPTION ===", {}).get(desc_cluster, "")
        humor = cluster_labels.get("HUMOR ===", {}).get(humor_cluster, "")
        topic = cluster_labels.get("TOPIC ===", {}).get(topic_cluster, "")
        template = cluster_labels.get("MEME_TEMPLATE ===", {}).get(template_cluster, "")

        # Clean up quotes
        description = description.strip('"')
        humor = humor.strip('"')
        topic = topic.strip('"')
        template = template.strip('"')

        print(f"📝 Using cluster labels (not example_meme attributes):")
        print(f"  Description: {description}")
        print(f"  Humor: {humor}")
        print(f"  Topic: {topic}")
        print(f"  Template: {template}")

    # Build the core topic from user prompt
    if user_prompt:
        # Prioritize user prompt over cluster topic
        topic_line = f"**PRIMARY TOPIC:** {user_prompt}"
        if topic:
            topic_line += f"\n**Meme Style Context:** {topic}"
    else:
        topic_line = f"**Topic:** {topic}" if topic else ""

    summary_parts = []
    for field, entry in data.items():
        if isinstance(entry, dict) and "chosen_cluster" in entry:
            label = entry.get("cluster_label") or ""
            summary_parts.append(f"{field}: {label}")

    cluster_summary = "\n".join(summary_parts)

    # Build prompt with heavy emphasis on user request
    prompt = f"""
Generate a short, visually engaging meme video.

**PRIMARY USER REQUEST:** {user_prompt or "Create a trendy meme video"}
⚠️ THIS IS THE MAIN TOPIC - THE VIDEO MUST BE ABOUT THIS! ⚠️

**Style Guidelines:**
- Description Style: {description if description else "Modern, relatable"}
- Humor Style: {humor if humor else "Witty and trending"}
{topic_line}
- Visual Template: {template if template else "Dynamic short-form"}

**Format Requirements:**
- Modern short-form meme (TikTok/Instagram Reels style)
- 5-10 seconds long
- Attention-grabbing pacing
- Bold caption overlays
- Trending sounds and music

**CRITICAL CONSTRAINTS:**
1. The video MUST focus exclusively on: {user_prompt or "the requested topic"}
2. DO NOT include any unrelated themes, objects, or content
3. All visual and audio elements must directly relate to: {user_prompt or "the main request"}
4. Stay on-topic throughout the entire video
"""

    return prompt


def sanitize_prompt_with_gemini(sora_prompt: str, original_user_request: str) -> str:
    """
    Use Gemini to intelligently sanitize a Sora prompt.

    This removes moderation-triggering content while preserving the user's original intent.

    Args:
        sora_prompt: The cluster-aware prompt that may contain trigger words
        original_user_request: The user's original request (ground truth)

    Returns:
        Sanitized prompt safe for OpenAI moderation
    """
    try:
        from gemini_pipeline import GeminiPipeline, PromptTemplate

        print("🧠 Using Gemini to sanitize prompt for OpenAI moderation...")

        sanitization_template = PromptTemplate(
            name="openai-prompt-sanitizer",
            system_instruction=(
                "You are an expert at rewriting video generation prompts to comply with "
                "content moderation policies while preserving creative intent. Your goal is to "
                "remove any references to violence, weapons, inappropriate content, or other "
                "policy-violating elements while keeping the prompt focused on the user's "
                "original creative request."
            ),
            task=(
                "Rewrite the provided video generation prompt to be compliant with OpenAI's "
                "moderation policies. Remove ANY references to: guns, weapons, violence, "
                "shooting, combat, war, or similar content. Keep the prompt focused on the "
                "user's original topic and ensure the output still achieves their creative goal."
            ),
            guidelines=[
                "Remove all mentions of weapons, violence, guns, shooting, combat, war, military, attacks, etc.",
                "Preserve the user's original creative intent and topic",
                "Keep style guidelines (humor, template, format) that are appropriate",
                "Maintain the video format requirements (duration, style, etc.)",
                "If cluster labels seem violent/inappropriate, replace with generic equivalents",
                "Output ONLY the sanitized prompt, no explanations or commentary",
                "The sanitized prompt should be ready to send directly to Sora API",
            ],
            output_schema_hint="A clean, moderation-safe video generation prompt"
        )

        context = f"""
ORIGINAL USER REQUEST (ground truth - this is what they want):
{original_user_request}

CLUSTER-AWARE PROMPT (may contain trigger words from YouTube shorts):
{sora_prompt}
"""

        pipeline = GeminiPipeline(
            model_name="gemini-2.5-flash-lite",
            template=sanitization_template
        )

        sanitized = pipeline.generate(
            user_input="Sanitize this prompt for OpenAI moderation while preserving the user's creative intent",
            context=context
        )

        print(f"✅ Gemini sanitization complete")
        return sanitized.strip()

    except Exception as e:
        print(f"⚠️ Gemini sanitization failed: {e}")
        print(f"⚠️ Falling back to keyword-based sanitization")
        # Fallback to our regex-based sanitization
        return sora_prompt


def query_clusters_for_prompt(user_prompt: str, top_k: int = 3) -> Dict[str, str]:
    """
    Query meme clusters using Gemini to find best matches for user prompt.
    Returns a dict mapping category names to cluster IDs.

    Args:
        user_prompt: User's natural language request
        top_k: Number of top clusters to consider

    Returns:
        Dict like {"DESCRIPTION": "5", "HUMOR": "12", "TOPIC": "8", "MEME_TEMPLATE": "3"}
    """
    try:
        # Import query modules (these are in image-pipeline directory)
        from query_meme_clusters import run_query
        from query_get_matching_image_rand import parse_matches

        print(f"🔍 Querying clusters for: '{user_prompt}'")

        # Use Gemini to match prompt to clusters
        gemini_response = run_query(
            question=user_prompt,
            top_k=top_k,
            model="gemini-2.5-flash-lite"
        )

        print(f"📊 Gemini response:\n{gemini_response}\n")

        # Parse the matches from Gemini's response
        matches = parse_matches(gemini_response)

        print(f"✅ Cluster matches: {matches}")
        return matches

    except Exception as e:
        print(f"⚠️ Error querying clusters: {e}")
        print(f"⚠️ Falling back to generic cluster selection")
        return {}


def select_example_meme_from_clusters(
    matches: Dict[str, str],
    all_results: Dict[str, Any],
    meme_clusters_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Select an appropriate example meme from the matched clusters.

    Args:
        matches: Dict mapping category to cluster ID (e.g., {"TOPIC": "8"})
        all_results: Dict of all available memes with their analysis
        meme_clusters_data: Optional meme_clusters.json data for better selection

    Returns:
        Selected meme data dict
    """
    if not matches or not all_results:
        # Fallback: return first available meme
        return next(iter(all_results.values())) if all_results else {}

    print(f"🎯 Selecting example meme from matched clusters...")

    # Try to load meme_clusters.json for better matching
    if meme_clusters_data is None and CLUSTER_DATA_PATHS.get("meme_clusters"):
        try:
            with open(CLUSTER_DATA_PATHS["meme_clusters"], 'r') as f:
                meme_clusters_data = json.load(f)
        except Exception as e:
            print(f"⚠️ Could not load meme_clusters.json: {e}")
            meme_clusters_data = {}

    # Priority order for cluster matching: TOPIC > MEME_TEMPLATE > HUMOR > DESCRIPTION
    priority_order = ["TOPIC", "MEME_TEMPLATE", "HUMOR", "DESCRIPTION"]

    selected_meme = None

    # Try to find a meme from the matched clusters
    for category in priority_order:
        cluster_id = matches.get(category)
        if not cluster_id:
            continue

        print(f"  Checking {category} cluster {cluster_id}...")

        # Get meme files from this cluster
        cluster_memes = []
        if meme_clusters_data and category in meme_clusters_data:
            cluster_key = cluster_id if isinstance(cluster_id, str) else str(cluster_id)
            cluster_memes = meme_clusters_data.get(category, {}).get(cluster_key, [])

        # Try to find matching meme in all_results
        for cluster_meme in cluster_memes[:5]:  # Check first 5 from cluster
            meme_file = cluster_meme.get("file", "") if isinstance(cluster_meme, dict) else str(cluster_meme)

            # Search for this meme in all_results
            for meme_id, meme_data in all_results.items():
                if meme_file in meme_id or meme_id in meme_file:
                    print(f"  ✅ Found matching meme from {category} cluster: {meme_file[:50]}...")
                    selected_meme = meme_data
                    break

            if selected_meme:
                break

        if selected_meme:
            break

    # Fallback: if no cluster-based match, pick a random meme
    if not selected_meme:
        print("  ⚠️ No cluster-based match found, using random meme")
        selected_meme = random.choice(list(all_results.values())) if all_results else {}

    return selected_meme


class VideoGeneratorReplica:
    """Video generator with topic-aware cluster matching and contamination prevention."""

    def __init__(self, cluster_data: Dict[str, Any]):
        self.cluster_data = cluster_data
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.cluster_labels = self._load_cluster_labels()

    def _load_cluster_labels(self) -> Dict[str, Any]:
        """Load cluster labels from cluster_labels_dict.json."""
        try:
            labels_path = CLUSTER_DATA_PATHS.get("cluster_labels_dict")
            if labels_path and Path(labels_path).exists():
                with open(labels_path, 'r') as f:
                    labels = json.load(f)
                    print(f"✅ Loaded cluster labels from {labels_path}")
                    return labels
            else:
                print(f"⚠️ cluster_labels_dict.json not found at {labels_path}")
                return {}
        except Exception as e:
            print(f"⚠️ Error loading cluster labels: {e}")
            return {}

    def _sanitize_prompt(self, prompt: str, user_prompt: str) -> str:
        """
        Remove moderation-triggering keywords that aren't in the user's original request.

        This prevents contamination from example_meme attributes causing moderation blocks.
        """
        # Keywords that commonly trigger moderation
        moderation_keywords = [
            "gun", "guns", "weapon", "weapons", "shooting", "shoot", "firearm", "firearms",
            "rifle", "pistol", "bullet", "ammunition", "armed", "violence", "violent",
            "war", "military", "combat", "attack", "bomb", "explosive", "explosives",
            "kill", "killing", "death", "dead", "murder", "blood", "bloody"
        ]

        user_lower = user_prompt.lower()
        sanitized = prompt
        removed = []

        for keyword in moderation_keywords:
            # Only remove if keyword is NOT in user's original request
            if keyword not in user_lower:
                # Case-insensitive replacement
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                if pattern.search(sanitized):
                    removed.append(keyword)
                    # Replace with empty string or generic term
                    sanitized = pattern.sub("", sanitized)

        # Clean up extra spaces from removals
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()

        if removed:
            print(f"🧹 Sanitized prompt - removed keywords: {removed}")

        return sanitized

    def _check_prompt_contamination(self, sora_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Check if the Sora prompt contains off-topic keywords that aren't in user's request.

        This helps detect when example_meme contamination leaks through.
        For example: user asks for "Lululemon" but prompt contains "gun", "weapon", "shooting"
        """
        # Common off-topic keywords to watch for (especially gun/weapon related)
        watchlist_keywords = [
            "gun", "guns", "weapon", "weapons", "shooting", "shoot", "firearm",
            "rifle", "pistol", "bullet", "ammunition", "armed", "violence",
            "war", "military", "combat", "attack", "bomb", "explosive"
        ]

        prompt_lower = sora_prompt.lower()
        user_lower = user_prompt.lower()

        detected_keywords = []
        for keyword in watchlist_keywords:
            # If keyword is in Sora prompt but NOT in user's request, flag it
            if keyword in prompt_lower and keyword not in user_lower:
                detected_keywords.append(keyword)

        return {
            "contaminated": len(detected_keywords) > 0,
            "keywords": detected_keywords,
            "severity": "high" if len(detected_keywords) > 2 else "medium" if detected_keywords else "none"
        }

    def generate_video(self, prompt: str, use_simple_mode: bool = False) -> Dict[str, Any]:
        """
        Generate video with cluster-aware mode (default) or simple mode.

        Args:
            prompt: User's request
            use_simple_mode: If True, use simple direct prompt (no YouTube shorts context).
                           If False (DEFAULT), use cluster matching with Gemini sanitization.

        DEFAULT (cluster-aware): Uses YouTube shorts clusters + Gemini sanitization
        Simple mode: Just uses user's request directly without cluster context
        """
        try:
            mode = "SIMPLE MODE" if use_simple_mode else "CLUSTER-AWARE MODE"
            print(f"\n{'='*80}")
            print(f"🎬 VIDEO GENERATION PIPELINE - {mode}")
            print(f"{'='*80}")
            print(f"User prompt: {prompt}\n")

            if use_simple_mode:
                print("📝 Using SIMPLE MODE - direct user request only (safer for moderation)")
                return self._generate_video_simple(prompt)
            else:
                print("📝 Using CLUSTER-AWARE MODE - with Gemini matching")
                return self._generate_video_with_clusters(prompt)

        except Exception as e:
            return {
                "status": "error",
                "message": f"Video generation failed: {str(e)}",
                "code": "VIDEO_GENERATION_FAILED"
            }

    def _generate_video_simple(self, prompt: str) -> Dict[str, Any]:
        """Generate video using simple, direct prompt (no cluster contamination)."""
        try:
            print("STEP 1: Building simple, direct prompt...")
            video_prompt = build_simple_prompt(prompt)

            # Save prompt to file
            prompt_log_path = Path("last_video_prompt_simple.txt")
            with open(prompt_log_path, 'w') as f:
                f.write("="*80 + "\n")
                f.write("SIMPLE MODE PROMPT (sent to Sora):\n")
                f.write("="*80 + "\n")
                f.write(video_prompt + "\n")
            print(f"📝 Prompt saved to: {prompt_log_path}")

            print("\n📝 Sora prompt:")
            print("-" * 80)
            print(video_prompt)
            print("-" * 80)

            print("\n🎬 Submitting to Sora...")

            # Submit job
            job = self.openai_client.videos.create(
                model=OPENAI_MODELS["video_generation"],
                prompt=video_prompt,
                seconds=VIDEO_DURATION_SECONDS,
                size=VIDEO_RESOLUTION,
            )

            job_id = getattr(job, "id", None)
            if not job_id:
                raise RuntimeError(f"Unexpected response when creating job: {job}")

            print(f"🕐 Job submitted: {job_id}, waiting for completion...")

            # Poll for completion
            while True:
                status = self.openai_client.videos.retrieve(job_id)
                state = getattr(status, "status", None) or getattr(status, "state", None)

                if state in ("completed", "succeeded", "ready"):
                    print("✅ Video generation complete!")
                    break
                if state in ("failed", "error"):
                    raise RuntimeError(f"❌ Generation failed: {status}")

                print(f"⏳ Status: {state or 'pending'}... waiting {POLL_SECONDS}s")
                time.sleep(POLL_SECONDS)

            # Download video
            print(f"⬇️ Downloading video content for job {job_id}")
            response = self.openai_client.videos.download_content(job_id)

            if hasattr(response, "read") and callable(response.read):
                video_data = response.read()
            elif hasattr(response, "content"):
                video_data = response.content
            else:
                video_data = response

            output_path = Path("generated_video.mp4")
            output_path.write_bytes(video_data)
            print(f"✅ Video downloaded to {output_path}")

            # Convert to base64
            import base64
            with open(output_path, 'rb') as f:
                video_data = f.read()
            video_base64 = base64.b64encode(video_data).decode('utf-8')

            # Clean up
            if output_path.exists():
                output_path.unlink()

            return {
                "status": "success",
                "content_type": "video",
                "data": video_base64,
                "metadata": {
                    "job_id": job_id,
                    "prompt": prompt,
                    "pipeline_version": "simple-mode-v1"
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Video generation failed: {str(e)}",
                "code": "VIDEO_GENERATION_FAILED"
            }

    def _generate_video_with_clusters(self, prompt: str) -> Dict[str, Any]:
        """Generate video with cluster matching (original complex approach)."""
        try:
            print(f"User prompt: {prompt}\n")

            all_results = self.cluster_data.get("all_results", {})

            # STEP 1: Query clusters using Gemini (same as image pipeline)
            print("STEP 1: Querying clusters with Gemini...")
            matches = query_clusters_for_prompt(prompt, top_k=3)

            # STEP 2: Select example meme from matched clusters
            print("\nSTEP 2: Selecting example meme from matched clusters...")
            example_meme = select_example_meme_from_clusters(
                matches,
                all_results,
                self.cluster_data.get("meme_clusters")
            )

            # STEP 3: Build data structure with MATCHED cluster information
            print("\nSTEP 3: Building data structure with matched clusters...")
            data = {
                "example_meme": example_meme,
                "DESCRIPTION": {
                    "chosen_cluster": matches.get("DESCRIPTION", "Cluster 1"),
                    "cluster_label": f"Description: {matches.get('DESCRIPTION', 'Generic')}"
                },
                "HUMOR": {
                    "chosen_cluster": matches.get("HUMOR", "Cluster 2"),
                    "cluster_label": f"Humor: {matches.get('HUMOR', 'Generic')}"
                },
                "TOPIC": {
                    "chosen_cluster": matches.get("TOPIC", "Cluster 3"),
                    "cluster_label": f"Topic: {matches.get('TOPIC', 'Generic')}"
                },
                "MEME_TEMPLATE": {
                    "chosen_cluster": matches.get("MEME_TEMPLATE", "Cluster 4"),
                    "cluster_label": f"Template: {matches.get('MEME_TEMPLATE', 'Generic')}"
                },
            }

            # Log the matched clusters
            for category, info in data.items():
                if category != "example_meme":
                    print(f"  {category}: {info['cluster_label']}")

            # STEP 4: Build prompt with cluster labels (not example_meme attributes)
            print("\nSTEP 4: Building enhanced Sora prompt with cluster labels...")
            video_prompt = build_prompt(
                data,
                user_prompt=prompt,
                cluster_labels=self.cluster_labels
            )

            # STEP 5: Check for contamination BEFORE sanitization
            print("\nSTEP 5: Checking for topic contamination...")
            contamination_check = self._check_prompt_contamination(video_prompt, prompt)
            if contamination_check["contaminated"]:
                print(f"⚠️ WARNING: Detected off-topic keywords: {contamination_check['keywords']}")
                print(f"⚠️ Severity: {contamination_check['severity']}")
                print("⚠️ Will use Gemini to sanitize...")

            # STEP 6: Use Gemini to intelligently sanitize prompt
            print("\nSTEP 6: Sanitizing prompt with Gemini AI...")
            video_prompt_sanitized = sanitize_prompt_with_gemini(video_prompt, prompt)

            # STEP 7: Save full prompt to file for debugging
            prompt_log_path = Path("last_video_prompt_cluster_aware.txt")
            with open(prompt_log_path, 'w') as f:
                f.write("="*80 + "\n")
                f.write("USER'S ORIGINAL REQUEST:\n")
                f.write("="*80 + "\n")
                f.write(prompt + "\n\n")
                f.write("="*80 + "\n")
                f.write("CLUSTER-AWARE PROMPT (with YouTube shorts context):\n")
                f.write("="*80 + "\n")
                f.write(video_prompt + "\n\n")
                f.write("="*80 + "\n")
                f.write("GEMINI-SANITIZED PROMPT (sent to Sora):\n")
                f.write("="*80 + "\n")
                f.write(video_prompt_sanitized + "\n")
            print(f"📝 Full prompt pipeline saved to: {prompt_log_path}")

            print("\n📝 Sanitized Sora prompt preview:")
            print("-" * 80)
            print(video_prompt_sanitized[:600] + "..." if len(video_prompt_sanitized) > 600 else video_prompt_sanitized)
            print("-" * 80)

            print("\n🎬 Submitting video generation request to Sora...")

            # Submit job with SANITIZED prompt to avoid moderation blocks
            job = self.openai_client.videos.create(
                model=OPENAI_MODELS["video_generation"],
                prompt=video_prompt_sanitized,  # Use sanitized version
                seconds=VIDEO_DURATION_SECONDS,
                size=VIDEO_RESOLUTION,
            )

            job_id = getattr(job, "id", None)
            if not job_id:
                raise RuntimeError(f"Unexpected response when creating job: {job}")

            print(f"🕐 Job submitted: {job_id}, waiting for completion...")

            # Poll exactly like original
            while True:
                status = self.openai_client.videos.retrieve(job_id)
                state = getattr(status, "status", None) or getattr(status, "state", None)

                if state in ("completed", "succeeded", "ready"):
                    print("✅ Video generation complete!")
                    break
                if state in ("failed", "error"):
                    raise RuntimeError(f"❌ Generation failed: {status}")

                print(f"⏳ Status: {state or 'pending'}... waiting {POLL_SECONDS}s")
                time.sleep(POLL_SECONDS)

            # Download video using the proper OpenAI method (like retrieve_video.py)
            print(f"⬇️ Downloading video content for job {job_id}")
            response = self.openai_client.videos.download_content(job_id)
            
            # Extract bytes from the response (like retrieve_video.py)
            if hasattr(response, "read") and callable(response.read):
                video_data = response.read()
            elif hasattr(response, "content"):
                video_data = response.content
            else:
                video_data = response
            
            output_path = Path("generated_video.mp4")
            output_path.write_bytes(video_data)
            print(f"✅ Video downloaded to {output_path}")
            
            # Convert to base64 for response
            import base64
            with open(output_path, 'rb') as f:
                video_data = f.read()
            video_base64 = base64.b64encode(video_data).decode('utf-8')
            
            # Clean up temp file
            if output_path.exists():
                output_path.unlink()
            
            return {
                "status": "success",
                "content_type": "video",
                "data": video_base64,
                "metadata": {
                    "job_id": job_id,
                    "prompt": prompt,
                    "matched_clusters": matches,
                    "contamination_detected": contamination_check.get("contaminated", False),
                    "trigger_keywords_found": contamination_check.get("keywords", []),
                    "gemini_sanitized": True,
                    "pipeline_version": "cluster-aware-gemini-sanitized-v3"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Video generation failed: {str(e)}",
                "code": "VIDEO_GENERATION_FAILED"
            }
