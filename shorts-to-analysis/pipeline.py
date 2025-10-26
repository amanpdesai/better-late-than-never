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


def load_api_keys() -> List[str]:
    """
    Load multiple API keys from environment.
    Supports GEMINI_API_KEY_1, GEMINI_API_KEY_2, etc.

    Returns:
        List of API keys
    """
    keys = []

    # Try numbered keys first
    i = 1
    while True:
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if key:
            keys.append(key)
            i += 1
        else:
            break

    # If no numbered keys, try single key
    if not keys:
        single_key = os.getenv("GEMINI_API_KEY")
        if single_key:
            keys.append(single_key)

    return keys


def main():
    """
    Main function to run the pipeline on the first video from the CSV.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Get API keys from environment
    api_keys = load_api_keys()
    if not api_keys:
        print("ERROR: Please set GEMINI_API_KEY or GEMINI_API_KEY_1, GEMINI_API_KEY_2, etc. in .env file")
        print("\nCreate a .env file with:")
        print('GEMINI_API_KEY=your-api-key-here')
        print('\nOr for multiple keys:')
        print('GEMINI_API_KEY_1=first-key')
        print('GEMINI_API_KEY_2=second-key')
        print('GEMINI_API_KEY_3=third-key')
        return

    print(f"Loaded {len(api_keys)} API key(s)")

    # Rate limit tracking: 10 calls per minute per key
    # Each video makes ~3-4 API calls (transcript upload, audio upload, analysis, maybe retries)
    # So we can process ~2-3 videos per key per minute
    CALLS_PER_MINUTE_PER_KEY = 10
    CALLS_PER_VIDEO = 4  # Conservative estimate (transcript, audio, analysis, potential retry)

    current_key_index = 0
    calls_this_minute = {i: 0 for i in range(len(api_keys))}
    minute_start_time = {}

    import time

    # Load first video from CSV
    csv_path = "massive_global_shorts.csv"
    if not os.path.exists(csv_path):
        print(f"ERROR: CSV file not found: {csv_path}")
        return

    print("Loading videos from CSV...")
    urls = load_videos_from_csv(csv_path)

    if not urls:
        print("No videos found in CSV")
        return

    print(f"Found {len(urls)} video(s) to process")
    print(f"Estimated time: ~{len(urls) * 60 / (len(api_keys) * 2):.0f} seconds ({len(urls) * 60 / (len(api_keys) * 2) / 60:.1f} minutes)")
    print("\n" + "="*60)

    # Create output directory
    os.makedirs("output", exist_ok=True)
    results_file = "output/all_results.jsonl"  # JSONL format for incremental saves

    # Track progress
    successful = 0
    failed = 0
    start_time = time.time()

    # Process all videos
    for idx, url in enumerate(urls):
        print(f"\n{'='*60}")
        print(f"Video {idx + 1}/{len(urls)}")
        print(f"Progress: {idx / len(urls) * 100:.1f}% | Success: {successful} | Failed: {failed}")
        print(f"Elapsed: {time.time() - start_time:.1f}s")
        print(f"{'='*60}")

        # Check if we need to wait for rate limit
        if current_key_index in minute_start_time:
            elapsed = time.time() - minute_start_time[current_key_index]
            if elapsed < 60 and calls_this_minute[current_key_index] + CALLS_PER_VIDEO > CALLS_PER_MINUTE_PER_KEY:
                # Try to rotate to another key that has capacity
                found_available_key = False
                for i in range(len(api_keys)):
                    check_key_index = (current_key_index + i + 1) % len(api_keys)
                    if check_key_index not in minute_start_time:
                        # Fresh key
                        current_key_index = check_key_index
                        found_available_key = True
                        break
                    else:
                        elapsed_check = time.time() - minute_start_time[check_key_index]
                        if elapsed_check >= 60:
                            # Reset this key's counter
                            calls_this_minute[check_key_index] = 0
                            minute_start_time[check_key_index] = time.time()
                            current_key_index = check_key_index
                            found_available_key = True
                            break
                        elif calls_this_minute[check_key_index] + CALLS_PER_VIDEO <= CALLS_PER_MINUTE_PER_KEY:
                            # This key has capacity
                            current_key_index = check_key_index
                            found_available_key = True
                            break

                if not found_available_key:
                    # All keys are rate limited, wait for the current one to reset
                    wait_time = 60 - elapsed
                    print(f"\n⏳ All API keys are rate limited. Waiting {wait_time:.1f}s for key {current_key_index + 1} to reset...")
                    time.sleep(wait_time)
                    calls_this_minute[current_key_index] = 0
                    minute_start_time[current_key_index] = time.time()

        # Initialize tracking for this key if needed
        if current_key_index not in minute_start_time:
            minute_start_time[current_key_index] = time.time()
            calls_this_minute[current_key_index] = 0

        api_key = api_keys[current_key_index]
        print(f"Using API key {current_key_index + 1}/{len(api_keys)} (calls this minute: {calls_this_minute[current_key_index]}/{CALLS_PER_MINUTE_PER_KEY})")

        try:
            result = process_video(url, api_key)
            calls_this_minute[current_key_index] += CALLS_PER_VIDEO

            if result['success']:
                successful += 1
            else:
                failed += 1

            # Save result incrementally (append to JSONL file)
            with open(results_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')

        except Exception as e:
            # If rate limited, try next key
            if "429" in str(e) or "quota" in str(e).lower() or "rate" in str(e).lower():
                print(f"\n⚠ Rate limit hit on key {current_key_index + 1}, rotating to next key...")
                current_key_index = (current_key_index + 1) % len(api_keys)
                api_key = api_keys[current_key_index]

                # Initialize tracking for new key if needed
                if current_key_index not in minute_start_time:
                    minute_start_time[current_key_index] = time.time()
                    calls_this_minute[current_key_index] = 0

                print(f"Retrying with API key {current_key_index + 1}/{len(api_keys)}")
                try:
                    result = process_video(url, api_key)
                    calls_this_minute[current_key_index] += CALLS_PER_VIDEO

                    if result['success']:
                        successful += 1
                    else:
                        failed += 1

                    # Save result incrementally
                    with open(results_file, 'a', encoding='utf-8') as f:
                        f.write(json.dumps(result, ensure_ascii=False) + '\n')
                except Exception as retry_error:
                    print(f"✗ Failed after retry: {retry_error}")
                    failed += 1
                    # Save error result
                    error_result = {'url': url, 'success': False, 'error': str(retry_error)}
                    with open(results_file, 'a', encoding='utf-8') as f:
                        f.write(json.dumps(error_result, ensure_ascii=False) + '\n')
            else:
                print(f"✗ Error: {e}")
                failed += 1
                # Save error result
                error_result = {'url': url, 'success': False, 'error': str(e)}
                with open(results_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(error_result, ensure_ascii=False) + '\n')

    # Final summary
    elapsed_total = time.time() - start_time
    print(f"\n\n{'='*60}")
    print("BATCH PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"Total videos: {len(urls)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total time: {elapsed_total:.1f}s ({elapsed_total / 60:.1f} minutes)")
    print(f"Average time per video: {elapsed_total / len(urls):.1f}s")
    print(f"\nResults saved to: {results_file}")
    print(f"(Each line is a JSON object)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
