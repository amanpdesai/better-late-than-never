"""
Parallel pipeline for analyzing YouTube Shorts videos
Uses multiple workers to process videos concurrently
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
from transcript_extractor import get_transcript
from llm_analyzer import analyze_video_content
from audio_recognizer import recognize_audio


class RateLimitedAPIKeyPool:
    """Thread-safe API key pool with rate limiting"""

    def __init__(self, api_keys: List[str], calls_per_minute: int = 10):
        self.api_keys = api_keys
        self.calls_per_minute = calls_per_minute
        self.lock = threading.Lock()
        self.key_usage = {i: {'calls': 0, 'reset_time': time.time() + 60} for i in range(len(api_keys))}
        self.current_key_index = 0

    def get_key(self) -> str:
        """Get an available API key, waiting if necessary"""
        with self.lock:
            while True:
                # Try to find an available key
                for i in range(len(self.api_keys)):
                    check_index = (self.current_key_index + i) % len(self.api_keys)

                    # Check if this key's minute has reset
                    if time.time() >= self.key_usage[check_index]['reset_time']:
                        self.key_usage[check_index] = {'calls': 0, 'reset_time': time.time() + 60}

                    # Check if key has capacity
                    if self.key_usage[check_index]['calls'] < self.calls_per_minute:
                        self.current_key_index = check_index
                        self.key_usage[check_index]['calls'] += 1
                        return self.api_keys[check_index]

                # All keys exhausted, wait for the nearest reset
                min_wait = min(self.key_usage[i]['reset_time'] - time.time() for i in range(len(self.api_keys)))
                if min_wait > 0:
                    print(f"  [Rate Limit] All keys exhausted, waiting {min_wait:.1f}s...")
                    time.sleep(min_wait + 0.1)


def process_single_video(url: str, video_path: str, audio_path: str, key_pool: RateLimitedAPIKeyPool, output_dir: str = "output") -> Dict:
    """Process a single pre-downloaded video (with audio already extracted) using API calls"""

    result = {
        'url': url,
        'success': False,
        'error': None,
        'analysis': None,
        'transcript': None,
        'keyframes': []
    }

    try:
        # Video and audio are already downloaded and extracted
        # Only do keyframe extraction (local, no API) and API calls

        # Extract keyframes (no API calls, but CPU intensive)
        keyframe_paths = extract_keyframes(
            video_path,
            5,
            os.path.join(output_dir, "keyframes")
        )

        # Get API keys for transcript/audio analysis (both make API calls)
        transcript_key = key_pool.get_key()
        audio_key = key_pool.get_key()

        # Process transcript and audio description in parallel with API
        # Note: audio_path is already available, no need to extract
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Modified transcript function to accept audio_path directly
            transcript_future = executor.submit(get_transcript_from_audio, audio_path, transcript_key)
            audio_future = executor.submit(analyze_audio_with_gemini_direct, audio_path, audio_key)

            transcript = transcript_future.result()
            sound_description = audio_future.result()

        result['keyframes'] = keyframe_paths
        result['transcript'] = transcript

        # Get another key for final analysis
        analysis_key = key_pool.get_key()

        # Analyze with Gemini
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
        print(f"✗ Error processing {url}: {e}")

    return result


def get_transcript_from_audio(audio_path: str, api_key: str) -> Optional[str]:
    """Get transcript directly from pre-extracted audio file"""
    import google.generativeai as genai
    import time

    # Simplified version that doesn't re-extract audio
    max_retries = 3
    for attempt in range(max_retries):
        try:
            genai.configure(api_key=api_key)
            audio_file = genai.upload_file(audio_path)

            while audio_file.state.name == "PROCESSING":
                time.sleep(2)
                audio_file = genai.get_file(audio_file.name)

            if audio_file.state.name == "FAILED":
                raise Exception("Audio file processing failed")

            model = genai.GenerativeModel('gemini-2.5-flash')
            prompt = "Please transcribe all the speech in this audio file. Provide only the transcription text, nothing else."
            response = model.generate_content([prompt, audio_file])

            return response.text
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                return None
    return None


def analyze_audio_with_gemini_direct(audio_path: str, api_key: str) -> str:
    """Analyze audio directly from pre-extracted audio file"""
    from audio_recognizer import analyze_audio_with_gemini
    return analyze_audio_with_gemini(audio_path, api_key)


def load_api_keys() -> List[str]:
    """Load multiple API keys from environment"""
    keys = []
    i = 1
    while True:
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if key:
            keys.append(key)
            i += 1
        else:
            break

    if not keys:
        single_key = os.getenv("GEMINI_API_KEY")
        if single_key:
            keys.append(single_key)

    return keys


def load_videos_from_csv(csv_path: str, limit: Optional[int] = None) -> List[str]:
    """Load video URLs from CSV file"""
    urls = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if limit and i >= limit:
                break
            urls.append(row['url'])
    return urls


def load_completed_urls(results_file: str) -> set:
    """Load URLs that have already been processed"""
    completed = set()
    if os.path.exists(results_file):
        with open(results_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    result = json.loads(line.strip())
                    completed.add(result['url'])
                except:
                    pass
    return completed


def batch_download_and_prepare_videos(urls: List[str], output_dir: str = "output") -> tuple:
    """
    Download all videos AND extract audio in parallel using many threads.
    Returns mapping of URL -> (video_path, audio_path)
    """
    from transcript_extractor import extract_audio_from_video
    import re

    download_dir = os.path.join(output_dir, "downloads")
    os.makedirs(download_dir, exist_ok=True)

    url_to_paths = {}
    failed_downloads = []

    # Track which video IDs are being downloaded to prevent duplicates
    downloading_lock = threading.Lock()
    downloading_ids = set()

    print(f"\nDownloading and preparing {len(urls)} videos in parallel...")
    start_time = time.time()

    def download_and_extract_audio(url):
        try:
            # Extract video ID from URL to prevent duplicate downloads
            video_id_match = re.search(r'(?:v=|/)([a-zA-Z0-9_-]{11})', url)
            if not video_id_match:
                return (url, None, None, "Could not extract video ID from URL")

            video_id = video_id_match.group(1)

            # Check if already being downloaded
            with downloading_lock:
                if video_id in downloading_ids:
                    return (url, None, None, "Duplicate video ID - skipping")
                downloading_ids.add(video_id)

            try:
                # Download video
                video_path = download_video(url, download_dir)

                # Extract audio immediately
                audio_path = extract_audio_from_video(video_path)

                return (url, video_path, audio_path, None)
            finally:
                # Remove from downloading set
                with downloading_lock:
                    downloading_ids.discard(video_id)

        except Exception as e:
            return (url, None, None, str(e))

    # Use even fewer threads to be safe - yt-dlp really doesn't like parallelism
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(download_and_extract_audio, url): url for url in urls}

        completed = 0
        for future in as_completed(futures):
            try:
                url, video_path, audio_path, error = future.result(timeout=120)  # 2 min timeout per video
                completed += 1

                if error:
                    failed_downloads.append((url, error))
                else:
                    url_to_paths[url] = (video_path, audio_path)

                if completed % 25 == 0 or completed == len(urls):
                    elapsed = time.time() - start_time
                    rate = completed / elapsed if elapsed > 0 else 0
                    print(f"  Prepared: {completed}/{len(urls)} ({completed/len(urls)*100:.1f}%) | "
                          f"Rate: {rate:.1f}/s | "
                          f"Failed: {len(failed_downloads)}")
            except Exception as e:
                completed += 1
                url = futures.get(future, "unknown")
                failed_downloads.append((url, str(e)))

    elapsed = time.time() - start_time
    print(f"\nPreparation complete: {len(url_to_paths)} successful, {len(failed_downloads)} failed in {elapsed:.1f}s")

    return url_to_paths, failed_downloads


def main():
    """Main function with parallel processing"""

    # Load environment
    load_dotenv()

    # Get API keys
    api_keys = load_api_keys()
    if not api_keys:
        print("ERROR: No API keys found in .env file")
        return

    print(f"Loaded {len(api_keys)} API key(s)")

    # Create output directory
    os.makedirs("output", exist_ok=True)
    results_file = "output/all_results.jsonl"

    # Load videos from CSV
    csv_path = "massive_global_shorts.csv"
    if not os.path.exists(csv_path):
        print(f"ERROR: CSV file not found: {csv_path}")
        return

    print("Loading videos from CSV...")
    all_urls = load_videos_from_csv(csv_path)

    if not all_urls:
        print("No videos found in CSV")
        return

    print(f"Found {len(all_urls)} total video(s) in CSV")

    # Check for already completed videos (resume capability)
    completed_urls = load_completed_urls(results_file)
    if completed_urls:
        print(f"Found {len(completed_urls)} already processed videos")
        remaining_urls = [url for url in all_urls if url not in completed_urls]
        print(f"Resuming with {len(remaining_urls)} remaining videos")
    else:
        remaining_urls = all_urls
        print("Starting fresh processing")

    if not remaining_urls:
        print("All videos have already been processed!")
        return

    # STEP 1: Download all videos AND extract audio first with many threads
    print(f"\n{'='*60}")
    print("STEP 1: DOWNLOADING VIDEOS AND EXTRACTING AUDIO")
    print(f"{'='*60}")
    url_to_paths, failed_downloads = batch_download_and_prepare_videos(remaining_urls)

    # Save failed downloads
    if failed_downloads:
        print(f"\n⚠ {len(failed_downloads)} videos failed to download")
        for url, error in failed_downloads[:5]:  # Show first 5
            print(f"  - {url}: {error}")
        # Save these as errors
        for url, error in failed_downloads:
            error_result = {'url': url, 'success': False, 'error': f'Download failed: {error}'}
            with open(results_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(error_result, ensure_ascii=False) + '\n')

    # STEP 2: Process downloaded videos with API calls
    print(f"\n{'='*60}")
    print("STEP 2: PROCESSING VIDEOS WITH API")
    print(f"{'='*60}")

    videos_per_minute = len(api_keys) * 10 / 4
    estimated_minutes = len(url_to_paths) / videos_per_minute
    print(f"Estimated processing time: ~{estimated_minutes:.1f} minutes")

    # Create API key pool
    key_pool = RateLimitedAPIKeyPool(api_keys, calls_per_minute=10)

    # Process with parallel workers
    num_workers = len(api_keys) * 3
    print(f"Starting {num_workers} parallel workers...")
    print(f"Results will be saved to: {results_file}\n")

    successful = 0
    failed = 0
    completed = 0
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Submit all processing tasks (video_path, audio_path)
        future_to_url = {
            executor.submit(process_single_video, url, video_path, audio_path, key_pool): url
            for url, (video_path, audio_path) in url_to_paths.items()
        }

        # Process results as they complete
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            completed += 1

            try:
                result = future.result()

                if result['success']:
                    successful += 1
                else:
                    failed += 1

                # Save result incrementally
                with open(results_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(result, ensure_ascii=False) + '\n')

                # Progress update every 10 videos
                if completed % 10 == 0 or completed == len(urls):
                    elapsed = time.time() - start_time
                    rate = completed / elapsed * 60 if elapsed > 0 else 0
                    remaining = len(urls) - completed
                    eta = remaining / rate if rate > 0 else 0

                    print(f"Progress: {completed}/{len(urls)} ({completed/len(urls)*100:.1f}%) | "
                          f"Success: {successful} | Failed: {failed} | "
                          f"Rate: {rate:.1f} videos/min | "
                          f"ETA: {eta:.1f} min")

            except Exception as e:
                failed += 1
                error_result = {'url': url, 'success': False, 'error': str(e)}
                with open(results_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(error_result, ensure_ascii=False) + '\n')

    # Final summary
    elapsed_total = time.time() - start_time
    print(f"\n{'='*60}")
    print("BATCH PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"Total videos: {len(urls)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total time: {elapsed_total:.1f}s ({elapsed_total / 60:.1f} minutes)")
    print(f"Average: {elapsed_total / len(urls):.1f}s per video")
    print(f"Throughput: {len(urls) / elapsed_total * 60:.1f} videos/minute")
    print(f"\nResults saved to: {results_file}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
