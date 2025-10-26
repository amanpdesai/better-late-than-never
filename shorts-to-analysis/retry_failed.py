"""
Retry script to re-process failed videos from all_results.jsonl
Run this after the main pipeline completes to retry failures
"""
import json
import os
from pipeline_simple import main as run_pipeline

def get_failed_urls(results_file: str = "output/all_results.jsonl") -> list:
    """Extract URLs that failed processing"""
    failed_urls = []

    if not os.path.exists(results_file):
        print(f"Results file not found: {results_file}")
        return []

    with open(results_file, 'r') as f:
        for line in f:
            try:
                result = json.loads(line.strip())
                if not result.get('success', False):
                    failed_urls.append(result['url'])
            except:
                pass

    return failed_urls


def create_retry_csv(failed_urls: list, output_file: str = "retry_videos.csv"):
    """Create a CSV file with only failed videos for retry"""
    import csv

    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['url'])
        writer.writeheader()
        for url in failed_urls:
            writer.writerow({'url': url})

    print(f"Created {output_file} with {len(failed_urls)} failed videos")


def main():
    """
    Extract failed videos and prepare for retry

    Usage:
    1. Run this script to identify failures: python retry_failed.py
    2. Then modify pipeline_simple.py to use 'retry_videos.csv' instead
    3. Or manually run pipeline on the retry CSV
    """

    results_file = "output/all_results.jsonl"

    # Get failed URLs
    failed_urls = get_failed_urls(results_file)

    if not failed_urls:
        print("No failed videos found - all done!")
        return

    print(f"\nFound {len(failed_urls)} failed videos")

    # Analyze failure types
    failure_types = {}
    with open(results_file, 'r') as f:
        for line in f:
            try:
                result = json.loads(line.strip())
                if not result.get('success', False):
                    error = result.get('error', 'Unknown error')
                    # Categorize error
                    if 'Download failed' in error:
                        category = 'Download Error'
                    elif '429' in error or 'quota' in error.lower():
                        category = 'Rate Limit / Quota'
                    elif 'timeout' in error.lower():
                        category = 'Timeout'
                    else:
                        category = 'Other API Error'

                    failure_types[category] = failure_types.get(category, 0) + 1
            except:
                pass

    print("\nFailure breakdown:")
    for category, count in sorted(failure_types.items(), key=lambda x: -x[1]):
        print(f"  {category}: {count}")

    # Create retry CSV
    create_retry_csv(failed_urls)

    print(f"\nTo retry these videos:")
    print(f"1. Backup current results: cp output/all_results.jsonl output/all_results.jsonl.backup")
    print(f"2. Remove failed entries: grep '\"success\": true' output/all_results.jsonl > output/all_results_success_only.jsonl")
    print(f"3. Move the success-only file: mv output/all_results_success_only.jsonl output/all_results.jsonl")
    print(f"4. Rename retry CSV: mv retry_videos.csv massive_global_shorts.csv.backup && cp retry_videos.csv massive_global_shorts.csv")
    print(f"5. Run pipeline: python pipeline_simple.py")
    print(f"6. Restore original CSV: mv massive_global_shorts.csv.backup massive_global_shorts.csv")

    print(f"\nOr just manually edit pipeline_simple.py line 136 to use 'retry_videos.csv'")


if __name__ == "__main__":
    main()
