#!/usr/bin/env python3
import argparse
import hashlib
import os
import time

import cv2

# moviepy is no longer needed as segment splitting is removed
# from moviepy.video.io.VideoFileClip import VideoFileClip


def get_video_hash(video_path):
    """Generate a hash for video identification based on file name and size."""
    file_stats = os.stat(video_path)
    file_size = file_stats.st_size
    base_name = os.path.basename(video_path)
    hash_input = f"{base_name}-{file_size}"
    return hashlib.md5(hash_input.encode()).hexdigest()


def is_already_processed(video_path, processed_videos_file):
    """Check if a video has already been processed."""
    video_hash = get_video_hash(video_path)

    if not os.path.exists(processed_videos_file):
        return False

    with open(processed_videos_file, "r") as f:
        processed_hashes = f.read().splitlines()

    return video_hash in processed_hashes


def mark_as_processed(video_path, processed_videos_file):
    """Mark a video as processed by recording its hash."""
    video_hash = get_video_hash(video_path)

    with open(processed_videos_file, "a+") as f:
        f.write(f"{video_hash}\n")


def extract_all_frames(video_path, output_dir, file_prefix):
    """Extracts all frames from the video and saves them as PNGs."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file: {video_path}")
        return 0

    frame_index = 0

    print(f"Starting extraction for: {video_path}")

    # Loop continuously reading frames until success is False (end of video)
    while True:
        success, frame = cap.read()

        if not success:
            break

        # File naming convention: [Video Name]_frame_[000000].png
        # Using 6 digits for frame index
        frame_filename = f"{file_prefix}_frame_{frame_index:06d}.png"
        output_path = os.path.join(output_dir, frame_filename)

        # Save frame in PNG format
        cv2.imwrite(output_path, frame)

        frame_index += 1

    cap.release()
    print(f"✅ Extraction complete. Total frames saved: {frame_index}")
    return frame_index


def process_videos(input_dir, frame_output_dir, processed_videos_file):
    """
    Process all videos in the input directory.
    (No segment splitting, only frame extraction).
    """
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
    if not os.path.exists(frame_output_dir):
        os.makedirs(frame_output_dir)

    video_extensions = [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv"]

    videos = []
    for file in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file)
        if (
            os.path.isfile(file_path)
            and os.path.splitext(file)[1].lower() in video_extensions
        ):
            videos.append(file_path)

    if not videos:
        print(f"Error: No videos found in {input_dir}.")
        return

    for video_path in videos:
        if is_already_processed(video_path, processed_videos_file):
            print(f"Skipping: {video_path} (already processed)")
            continue

        filename_base = os.path.splitext(os.path.basename(video_path))[0]

        # Call the function that extracts all frames
        frame_count = extract_all_frames(video_path, frame_output_dir, filename_base)

        if frame_count > 0:
            mark_as_processed(video_path, processed_videos_file)


def main():
    parser = argparse.ArgumentParser(
        description="Extracts all frames from videos in an input directory."
    )
    parser.add_argument(
        "-i",
        "--input-dir",
        default="BeforeSplit",
        help="Directory containing videos to process (default: BeforeSplit)",
    )
    parser.add_argument(
        "-f",
        "--frame-dir",
        default="ExtractedFrames",
        help="Directory to save extracted frames (default: ExtractedFrames)",
    )
    parser.add_argument(
        "-w",
        "--watch",
        action="store_true",
        help="Watch the input directory for new videos.",
    )
    parser.add_argument(
        "-t",
        "--interval",
        type=int,
        default=60,
        help="Interval in seconds to check for new videos (only with --watch)",
    )

    args = parser.parse_args()

    processed_videos_file = ".processed_videos"

    if args.watch:
        print(f"👁️ Watching {args.input_dir} for new videos...")
        try:
            while True:
                process_videos(
                    args.input_dir,
                    args.frame_dir,
                    processed_videos_file,
                )
                print(f"Waiting {args.interval} seconds before next check...")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("Watch mode stopped.")
    else:
        process_videos(
            args.input_dir,
            args.frame_dir,
            processed_videos_file,
        )


if __name__ == "__main__":
    main()
