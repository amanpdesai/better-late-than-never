"""
Main pipeline for analyzing YouTube Shorts videos
"""
import os
import csv
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional
from dotenv import load_dotenv

from video_downloader import download_video
from keyframe_extractor import extract_keyframes
from transcript_extractor import get_transcript
from llm_analyzer import analyze_video_content
from audio_recognizer import recognize_audio


def process_video(
    url: str,
    api_key: str,
    output_dir: str = "output",
    num_keyframes: int = 5
) -> Dict[str, any]:
    """
    Process a single YouTube Shorts video through the entire pipeline.

    Args:
        url: YouTube video URL
        api_key: Gemini API key
        output_dir: Directory for output files
        num_keyframes: Number of keyframes to extract

    Returns:
        Dictionary with processing results
    """
    print(f"\n{'='*60}")
    print(f"Processing video: {url}")
    print(f"{'='*60}")

    result = {
        'url': url,
        'success': False,
        'error': None,
        'analysis': None,
        'transcript': None,
        'keyframes': []
    }

    try:
        # Step 1: Download video
        print("\n[1/4] Downloading video...")
        video_path = download_video(url, os.path.join(output_dir, "downloads"))
        print(f"✓ Downloaded to: {video_path}")

        # Step 2, 3 & 4: Extract keyframes, transcript, and recognize audio in parallel
        print("\n[2/5] Extracting keyframes, transcript, and recognizing audio in parallel...")

        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all three tasks in parallel
            keyframe_future = executor.submit(
                extract_keyframes,
                video_path,
                num_keyframes,
                os.path.join(output_dir, "keyframes")
            )
            transcript_future = executor.submit(get_transcript, video_path, api_key)
            audio_future = executor.submit(recognize_audio, video_path, api_key)

            # Wait for all to complete
            keyframe_paths = keyframe_future.result()
            transcript = transcript_future.result()
            sound_description = audio_future.result()

        print(f"✓ Extracted {len(keyframe_paths)} keyframes")
        if transcript:
            print(f"✓ Retrieved transcript ({len(transcript)} characters)")
        else:
            print("⚠ No transcript available (will analyze using keyframes only)")
        print(f"✓ Audio recognition: {sound_description}")

        result['keyframes'] = keyframe_paths
        result['transcript'] = transcript

        # Step 5: Analyze with Gemini
        print("\n[3/5] Analyzing with Gemini...")
        analysis = analyze_video_content(keyframe_paths, transcript, api_key, sound_description)
        print(f"✓ Analysis complete")

        # Move sound_description into analysis dict
        analysis['sound_description'] = sound_description

        result['analysis'] = analysis
        result['success'] = True

        print("\n" + "="*60)
        print("ANALYSIS RESULTS:")
        print("="*60)
        print(f"\nDescription:\n{analysis['description']}\n")
        print(f"Humor: {analysis['humor']}\n")
        print(f"Topic: {analysis['topic']}\n")
        print(f"Template: {analysis['template']}\n")
        print(f"Sound: {analysis['sound_description']}")
        print("="*60)

        # Cleanup: Delete downloaded video and audio files, keep keyframes
        print("\n[4/5] Cleaning up temporary files...")
        try:
            # Delete video file
            if os.path.exists(video_path):
                os.remove(video_path)
                print(f"✓ Deleted video file")

            # Delete audio file
            audio_path = video_path.rsplit('.', 1)[0] + '_audio.mp3'
            if os.path.exists(audio_path):
                os.remove(audio_path)
                print(f"✓ Deleted audio file")

            print(f"✓ Kept keyframes in {os.path.join(output_dir, 'keyframes')}")
        except Exception as cleanup_error:
            print(f"⚠ Cleanup warning: {cleanup_error}")

    except Exception as e:
        print(f"\n✗ Error processing video: {e}")
        result['error'] = str(e)

    return result


def load_videos_from_csv(csv_path: str, limit: Optional[int] = None) -> List[str]:
    """
    Load video URLs from CSV file.

    Args:
        csv_path: Path to CSV file
        limit: Maximum number of URLs to load (None for all)

    Returns:
        List of video URLs
    """
    urls = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if limit and i >= limit:
                break
            urls.append(row['url'])
    return urls


def main():
    """
    Main function to run the pipeline on the first video from the CSV.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Please set GEMINI_API_KEY in .env file")
        print("\nCreate a .env file with:")
        print('GEMINI_API_KEY=your-api-key-here')
        return

    # Load first video from CSV
    csv_path = "massive_global_shorts.csv"
    if not os.path.exists(csv_path):
        print(f"ERROR: CSV file not found: {csv_path}")
        return

    print("Loading videos from CSV...")
    urls = load_videos_from_csv(csv_path, limit=1)

    if not urls:
        print("No videos found in CSV")
        return

    print(f"Found {len(urls)} video(s) to process")

    # Process the first video
    result = process_video(urls[0], api_key)

    # Save result
    output_file = "output/analysis_result.json"
    os.makedirs("output", exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n\nResult saved to: {output_file}")


if __name__ == "__main__":
    main()
