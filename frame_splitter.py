#!/usr/bin/env python3
import os
import argparse
import time
import hashlib
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

def split_video(video_path, output_dir, segment_duration=5):
    """
    Split a video into segments of specified duration
    
    Args:
        video_path (str): Path to the video file
        output_dir (str): Directory to save the output segments
        segment_duration (int): Duration of each segment in seconds (default: 5)
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get video filename without extension
    filename = os.path.basename(video_path)
    name, _ = os.path.splitext(filename)
    
    try:
        # Load the video
        clip = VideoFileClip(video_path)
        
        # Calculate number of segments
        duration = int(clip.duration)
        segments = duration // segment_duration
        
        # Split the video into segments
        for i in range(segments + 1):
            start_time = i * segment_duration
            end_time = min((i + 1) * segment_duration, duration)
            
            # Skip if segment would be 0 seconds
            if end_time <= start_time:
                continue
                
            # Create subclip
            segment = clip.subclip(start_time, end_time)
            
            # Output file path
            output_path = os.path.join(output_dir, f"{name}_segment_{i+1:03d}.mp4")
            
            # Write segment to file
            segment.write_videofile(output_path, 
                                codec="libx264", 
                                audio_codec="aac",
                                temp_audiofile=f"temp-audio-{i}.m4a", 
                                remove_temp=True)
            
            print(f"Created segment {i+1}/{segments+1}: {output_path}")
        
        # Close the clip
        clip.close()
        
        print(f"Video split complete. {segments+1} segments created in '{output_dir}'")
        return True
    except Exception as e:
        print(f"Error processing {video_path}: {str(e)}")
        return False

def process_videos(input_dir, output_dir, segment_duration, processed_videos_file):
    """
    Process all videos in input directory that haven't been processed yet
    """
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
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
        success = split_video(video_path, output_dir, segment_duration)
        
        if success:
            mark_as_processed(video_path, processed_videos_file)

def main():
    parser = argparse.ArgumentParser(description="Split videos into segments of specified duration")
    parser.add_argument("-i", "--input-dir", default="BeforeSplit", 
                        help="Directory containing videos to split (default: BeforeSplit)")
    parser.add_argument("-o", "--output-dir", default="AfterSplit", 
                        help="Directory to save output segments (default: AfterSplit)")
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
                process_videos(args.input_dir, args.output_dir, args.duration, processed_videos_file)
                print(f"Waiting {args.interval} seconds before next check...")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("Watch mode stopped.")
    else:
        process_videos(args.input_dir, args.output_dir, args.duration, processed_videos_file)

if __name__ == "__main__":
    main() 