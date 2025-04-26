#!/usr/bin/env python3
import os
import argparse
import time
import hashlib
import cv2
from moviepy.editor import VideoFileClip

def get_video_hash(video_path):
    """Generate a hash for video identification based on file name and size"""
    file_stats = os.stat(video_path)
    file_size = file_stats.st_size
    base_name = os.path.basename(video_path)
    hash_input = f"{base_name}-{file_size}"
    return hashlib.md5(hash_input.encode()).hexdigest()

def is_already_processed(video_path, processed_videos_file):
    """Check if a video has already been processed"""
    video_hash = get_video_hash(video_path)
    
    if not os.path.exists(processed_videos_file):
        return False
        
    with open(processed_videos_file, 'r') as f:
        processed_hashes = f.read().splitlines()
        
    return video_hash in processed_hashes

def mark_as_processed(video_path, processed_videos_file):
    """Mark a video as processed by recording its hash"""
    video_hash = get_video_hash(video_path)
    
    with open(processed_videos_file, 'a+') as f:
        f.write(f"{video_hash}\n")

def extract_one_frame_per_second(video_path, output_dir, segment_name):
    """Extract one frame per second from a video segment"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps

    count = 0
    while count <= duration:
        frame_no = int(count * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
        success, frame = cap.read()

        if not success:
            break

        frame_filename = f"{segment_name}_frame_{int(count):03d}.png"
        output_path = os.path.join(output_dir, frame_filename)
        cv2.imwrite(output_path, frame)
        print(f"Saved frame: {output_path}")

        count += 1

    cap.release()

def split_video(video_path, output_dir, frame_output_dir, segment_duration=5):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filename = os.path.basename(video_path)
    name, _ = os.path.splitext(filename)
    
    try:
        clip = VideoFileClip(video_path)
        duration = int(clip.duration)
        segments = duration // segment_duration

        for i in range(segments + 1):
            start_time = i * segment_duration
            end_time = min((i + 1) * segment_duration, duration)
            
            if end_time <= start_time:
                continue
                
            segment = clip.subclip(start_time, end_time)

            segment_filename = f"{name}_segment_{i+1:03d}.mp4"
            segment_path = os.path.join(output_dir, segment_filename)

            segment.write_videofile(segment_path, 
                                    codec="libx264", 
                                    audio_codec="aac",
                                    temp_audiofile=f"temp-audio-{i}.m4a", 
                                    remove_temp=True)
            
            print(f"Created segment {i+1}/{segments+1}: {segment_path}")

            # Burada her segmentten frame çıkar
            extract_one_frame_per_second(segment_path, frame_output_dir, f"{name}_segment_{i+1:03d}")
        
        clip.close()

        print(f"Video split complete. {segments+1} segments created in '{output_dir}'")
        return True
    except Exception as e:
        print(f"Error processing {video_path}: {str(e)}")
        return False

def process_videos(input_dir, output_dir, frame_output_dir, segment_duration, processed_videos_file):
    """
    Process all videos in input directory that haven't been processed yet
    """
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(frame_output_dir):
        os.makedirs(frame_output_dir)
        
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
    
    videos = []
    for file in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file)
        if os.path.isfile(file_path) and os.path.splitext(file)[1].lower() in video_extensions:
            videos.append(file_path)
    
    if not videos:
        print(f"No videos found in {input_dir}")
        return
    
    for video_path in videos:
        if is_already_processed(video_path, processed_videos_file):
            print(f"Skipping {video_path} (already processed)")
            continue
            
        print(f"Processing {video_path}...")
        success = split_video(video_path, output_dir, frame_output_dir, segment_duration)
        
        if success:
            mark_as_processed(video_path, processed_videos_file)

def main():
    parser = argparse.ArgumentParser(description="Split videos into segments and extract one frame per second")
    parser.add_argument("-i", "--input-dir", default="BeforeSplit", 
                        help="Directory containing videos to split (default: BeforeSplit)")
    parser.add_argument("-o", "--output-dir", default="AfterSplit", 
                        help="Directory to save output segments (default: AfterSplit)")
    parser.add_argument("-f", "--frame-dir", default="ExtractedFrames",
                        help="Directory to save extracted frames (default: ExtractedFrames)")
    parser.add_argument("-d", "--duration", type=int, default=5, choices=range(5, 11),
                        help="Duration of each segment in seconds (5-10)")
    parser.add_argument("-w", "--watch", action="store_true",
                        help="Watch the input directory for new videos")
    parser.add_argument("-t", "--interval", type=int, default=60,
                        help="Interval in seconds to check for new videos (only with --watch)")
    
    args = parser.parse_args()
    
    processed_videos_file = ".processed_videos"
    
    if args.watch:
        print(f"Watching {args.input_dir} for new videos...")
        try:
            while True:
                process_videos(args.input_dir, args.output_dir, args.frame_dir, args.duration, processed_videos_file)
                print(f"Waiting {args.interval} seconds before next check...")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("Watch mode stopped.")
    else:
        process_videos(args.input_dir, args.output_dir, args.frame_dir, args.duration, processed_videos_file)

if __name__ == "__main__":
    main()