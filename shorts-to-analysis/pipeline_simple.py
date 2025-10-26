"""
Simple reliable pipeline: Download sequentially, process in parallel
"""
import os
import csv
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
from dotenv import load_dotenv
import time
import threading

from video_downloader import download_video
from keyframe_extractor import extract_keyframes
from transcript_extractor import extract_audio_from_video, get_transcript
from llm_analyzer import analyze_video_content
from audio_recognizer import analyze_audio_with_gemini


# Import key pool from parallel version
import sys
sys.path.insert(0, os.path.dirname(__file__))
from pipeline_parallel import RateLimitedAPIKeyPool, load_api_keys, load_completed_urls, get_transcript_from_audio, analyze_audio_with_gemini_direct


def download_and_prepare_all_sequential(urls: List[str], output_dir: str = "output") -> Dict[str, tuple]:
    """
    Download videos ONE AT A TIME (sequential) to avoid yt-dlp conflicts.
    Returns mapping of URL -> (video_path, audio_path)
    """
    download_dir = os.path.join(output_dir, "downloads")
    os.makedirs(download_dir, exist_ok=True)

    url_to_paths = {}
    failed = []

    print(f"\nDownloading {len(urls)} videos sequentially (reliable mode)...")
    start_time = time.time()

    for idx, url in enumerate(urls):
        try:
            # Download video
            video_path = download_video(url, download_dir)

            # Extract audio
            audio_path = extract_audio_from_video(video_path)

            url_to_paths[url] = (video_path, audio_path)

            if (idx + 1) % 25 == 0 or (idx + 1) == len(urls):
                elapsed = time.time() - start_time
                rate = (idx + 1) / elapsed if elapsed > 0 else 0
                remaining = len(urls) - (idx + 1)
                eta = remaining / rate if rate > 0 else 0
                print(f"  Downloaded: {idx + 1}/{len(urls)} ({(idx+1)/len(urls)*100:.1f}%) | "
                      f"Rate: {rate:.2f}/s | ETA: {eta/60:.1f} min | Failed: {len(failed)}")

        except Exception as e:
            failed.append((url, str(e)))
            print(f"  ✗ Failed: {url[:50]}... - {str(e)[:50]}")

    elapsed = time.time() - start_time
    print(f"\nDownload complete: {len(url_to_paths)} successful, {len(failed)} failed in {elapsed:.1f}s ({elapsed/60:.1f} min)")

    return url_to_paths, failed


def process_single_video_simple(url: str, video_path: str, audio_path: str, key_pool: RateLimitedAPIKeyPool, output_dir: str = "output") -> Dict:
    """Process pre-downloaded video with API calls"""

    result = {
        'url': url,
        'success': False,
        'error': None,
        'analysis': None,
        'transcript': None,
        'keyframes': []
    }

    try:
        # Extract keyframes (local, no API)
        keyframe_paths = extract_keyframes(video_path, 5, os.path.join(output_dir, "keyframes"))

        # Get API keys
        transcript_key = key_pool.get_key()
        audio_key = key_pool.get_key()

        # API calls in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            transcript_future = executor.submit(get_transcript_from_audio, audio_path, transcript_key)
            audio_future = executor.submit(analyze_audio_with_gemini_direct, audio_path, audio_key)

            transcript = transcript_future.result()
            sound_description = audio_future.result()

        result['keyframes'] = keyframe_paths
        result['transcript'] = transcript

        # Final analysis
        analysis_key = key_pool.get_key()
        analysis = analyze_video_content(keyframe_paths, transcript, analysis_key, sound_description)
        analysis['sound_description'] = sound_description

        result['analysis'] = analysis
        result['success'] = True

        # Cleanup
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except:
            pass

    except Exception as e:
        result['error'] = str(e)

    return result


def main():
    load_dotenv()

    api_keys = load_api_keys()
    if not api_keys:
        print("ERROR: No API keys found")
        return

    print(f"Loaded {len(api_keys)} API key(s)")

    os.makedirs("output", exist_ok=True)
    results_file = "output/all_results.jsonl"

    # Load videos
    csv_path = "massive_global_shorts.csv"
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        all_urls = [row['url'] for row in reader]

    print(f"Found {len(all_urls)} total videos")

    # Check completed
    completed_urls = load_completed_urls(results_file)
    if completed_urls:
        print(f"Already processed: {len(completed_urls)}")
        remaining_urls = [url for url in all_urls if url not in completed_urls]
    else:
        remaining_urls = all_urls

    if not remaining_urls:
        print("All done!")
        return

    print(f"Remaining: {len(remaining_urls)}")

    # PIPELINED APPROACH: Download next while processing current
    print(f"\n{'='*60}")
    print("PIPELINED PROCESSING")
    print("Downloading next video while processing current")
    print(f"{'='*60}")

    key_pool = RateLimitedAPIKeyPool(api_keys, calls_per_minute=10)

    successful = 0
    failed = 0
    start_time = time.time()
    output_dir = "output"
    download_dir = os.path.join(output_dir, "downloads")
    os.makedirs(download_dir, exist_ok=True)

    # Use ONLY 1 download at a time to avoid yt-dlp conflicts
    download_executor = ThreadPoolExecutor(max_workers=1)
    process_executor = ThreadPoolExecutor(max_workers=len(api_keys) * 2)

    pending_downloads = {}
    pending_processes = {}

    # Start first download
    if len(remaining_urls) > 0:
        url = remaining_urls[0]
        print(f"\n[Download] Starting: {url[:60]}...")
        future = download_executor.submit(download_video, url, download_dir)
        pending_downloads[future] = url

    processed_count = 0
    download_idx = 1  # Next URL to download
    last_status_time = time.time()

    while pending_downloads or pending_processes or download_idx < len(remaining_urls):
        # Status update every 2 seconds
        if time.time() - last_status_time > 2:
            print(f"  [Status] Downloading: {len(pending_downloads)} | Processing: {len(pending_processes)} | "
                  f"Completed: {processed_count}/{len(remaining_urls)}")
            last_status_time = time.time()

        # Check completed downloads
        done_downloads = [f for f in pending_downloads if f.done()]
        for future in done_downloads:
            url = pending_downloads.pop(future)
            try:
                video_path = future.result()
                print(f"  [Download] ✓ Complete: {url[:60]}...")

                # Extract audio
                print(f"  [Audio Extract] Extracting from {url[:60]}...")
                audio_path = extract_audio_from_video(video_path)
                print(f"  [Audio Extract] ✓ Complete")

                # Submit for processing
                print(f"  [Process] Starting API processing for {url[:60]}...")
                process_future = process_executor.submit(
                    process_single_video_simple, url, video_path, audio_path, key_pool, output_dir
                )
                pending_processes[process_future] = url

                # Start next download if available
                if download_idx < len(remaining_urls):
                    next_url = remaining_urls[download_idx]
                    print(f"\n[Download] Starting: {next_url[:60]}...")
                    next_future = download_executor.submit(download_video, next_url, download_dir)
                    pending_downloads[next_future] = next_url
                    download_idx += 1

            except Exception as e:
                print(f"  [Download] ✗ Failed: {str(e)[:100]}")
                # Save download error
                error_result = {'url': url, 'success': False, 'error': f'Download failed: {str(e)}'}
                with open(results_file, 'a') as f:
                    f.write(json.dumps(error_result, ensure_ascii=False) + '\n')
                failed += 1

                # Start next download even after failure
                if download_idx < len(remaining_urls):
                    next_url = remaining_urls[download_idx]
                    print(f"\n[Download] Starting: {next_url[:60]}...")
                    next_future = download_executor.submit(download_video, next_url, download_dir)
                    pending_downloads[next_future] = next_url
                    download_idx += 1

        # Check completed processing
        done_processes = [f for f in pending_processes if f.done()]
        for future in done_processes:
            url = pending_processes.pop(future)
            try:
                result = future.result()

                if result['success']:
                    successful += 1
                    print(f"  [Process] ✓ Success: {url[:60]}...")
                else:
                    failed += 1
                    print(f"  [Process] ✗ Failed: {url[:60]}...")

                with open(results_file, 'a') as f:
                    f.write(json.dumps(result, ensure_ascii=False) + '\n')

                processed_count += 1
                if processed_count % 5 == 0 or processed_count == len(remaining_urls):
                    elapsed = time.time() - start_time
                    rate = processed_count / elapsed * 60 if elapsed > 0 else 0
                    remaining_count = len(remaining_urls) - processed_count
                    eta = remaining_count / rate if rate > 0 else 0
                    print(f"\n{'='*60}")
                    print(f"  Progress: {processed_count}/{len(remaining_urls)} ({processed_count/len(remaining_urls)*100:.1f}%)")
                    print(f"  Success: {successful} | Failed: {failed}")
                    print(f"  Rate: {rate:.1f}/min | ETA: {eta:.1f} min")
                    print(f"{'='*60}\n")

            except Exception as e:
                failed += 1
                print(f"  [Process] ✗ Exception: {str(e)[:100]}")

        # Small sleep to prevent busy-waiting
        time.sleep(0.5)

    # Cleanup
    download_executor.shutdown(wait=True)
    process_executor.shutdown(wait=True)

    # Summary
    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print("COMPLETE")
    print(f"{'='*60}")
    print(f"Total: {len(remaining_urls)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Time: {elapsed/60:.1f} minutes")
    print(f"Throughput: {len(remaining_urls)/elapsed*60:.1f} videos/min")
    print(f"Results: {results_file}")


if __name__ == "__main__":
    main()
