"""
Module for extracting key frames from videos using OpenCV
"""
import cv2
import numpy as np
from typing import List
import os
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks


def extract_keyframes(video_path: str, num_frames: int = 5, output_dir: str = "keyframes") -> List[str]:
    """
    Extract key frames using adaptive clustering based on visual content changes.
    Identifies distinct scenes and moments rather than forcing equal distribution.

    Args:
        video_path: Path to the video file
        num_frames: Number of key frames to extract
        output_dir: Directory to save extracted frames

    Returns:
        List of paths to the extracted frame images
    """
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")

    # Get video properties
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    print(f"  Analyzing {total_frames} frames across {total_frames/fps:.1f}s video...")

    # Pass 1: Calculate multiple visual features for each frame
    prev_gray = None
    prev_hist = None
    frame_scores = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Calculate histogram for color distribution changes
        hist = cv2.calcHist([gray], [0], None, [32], [0, 256])
        hist = cv2.normalize(hist, hist).flatten()

        if prev_gray is not None and prev_hist is not None:
            # 1. Frame difference (motion/change)
            motion_score = np.mean(cv2.absdiff(prev_gray, gray))

            # 2. Histogram difference (scene/lighting change)
            hist_score = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CHISQR)

            # 3. Edge detection (visual complexity/interest)
            edges = cv2.Canny(gray, 50, 150)
            edge_score = np.sum(edges) / edges.size

            # Combine scores (weighted)
            combined_score = (motion_score * 0.4) + (hist_score * 0.4) + (edge_score * 100)

            frame_scores.append({
                'idx': frame_idx,
                'score': combined_score,
                'motion': motion_score,
                'hist': hist_score,
                'edges': edge_score,
                'time': frame_idx / fps
            })

        prev_gray = gray
        prev_hist = hist
        frame_idx += 1

    cap.release()

    if not frame_scores:
        # Fallback: just sample evenly
        selected_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int).tolist()
    else:
        # Pass 2: Adaptive selection strategy
        # Find peaks (local maxima) in the score curve
        scores_array = np.array([f['score'] for f in frame_scores])

        # Smooth the signal to reduce noise
        smoothed = gaussian_filter1d(scores_array, sigma=fps)  # smooth over ~1 second

        # Find significant peaks (scene changes)
        peaks, _ = find_peaks(
            smoothed,
            distance=int(fps * 0.5),  # minimum 0.5s between peaks
            prominence=np.percentile(smoothed, 60)  # only significant peaks
        )

        print(f"  Found {len(peaks)} significant scene changes/peaks")

        # Strategy: Combine guaranteed coverage + peak detection
        # Always include: first frame, last frame, and top peaks

        guaranteed_frames = [
            0,  # Start
            total_frames - 1  # End
        ]

        # Get frames at peak positions
        peak_frames = [frame_scores[p]['idx'] for p in peaks]

        # Combine all candidates
        candidate_frames = set(guaranteed_frames + peak_frames)

        # Score each candidate by their importance
        candidate_scores = []
        for frame_idx in candidate_frames:
            if frame_idx < len(frame_scores):
                score_data = frame_scores[frame_idx] if frame_idx < len(frame_scores) else {'score': 0}
                candidate_scores.append((frame_idx, score_data.get('score', 0)))
            else:
                # For first/last frames that might not be in frame_scores
                candidate_scores.append((frame_idx, 0))

        # Sort by score and take top N
        candidate_scores.sort(key=lambda x: x[1], reverse=True)
        selected_indices = sorted([idx for idx, _ in candidate_scores[:num_frames]])

        # Ensure we have start and end coverage if not naturally selected
        if 0 not in selected_indices:
            selected_indices[0] = 0
        if total_frames - 1 not in selected_indices:
            selected_indices[-1] = total_frames - 1

        # Print debug info
        print(f"  Selected frames:")
        for idx in selected_indices:
            time_sec = idx / fps
            score_info = next((f for f in frame_scores if f['idx'] == idx), None)
            if score_info:
                print(f"    Frame {idx} @ {time_sec:.1f}s - score: {score_info['score']:.1f}")
            else:
                print(f"    Frame {idx} @ {time_sec:.1f}s")

    # Extract the selected frames
    cap = cv2.VideoCapture(video_path)
    video_id = os.path.splitext(os.path.basename(video_path))[0]
    extracted_paths = []

    for i, frame_idx in enumerate(selected_indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()

        if ret:
            frame_path = os.path.join(output_dir, f'{video_id}_frame_{i:03d}.jpg')
            cv2.imwrite(frame_path, frame)
            extracted_paths.append(frame_path)

    cap.release()
    return extracted_paths


if __name__ == "__main__":
    # Test extraction
    test_video = "downloads/OIs4CdJ8uE4.mp4"
    if os.path.exists(test_video):
        frames = extract_keyframes(test_video)
        print(f"Extracted {len(frames)} frames:")
        for frame in frames:
            print(f"  {frame}")
