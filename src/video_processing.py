import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import cv2
from moviepy.editor import VideoFileClip
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import shlex


def convert_h264_to_mp4(input_path, output_path):
    # Use FFmpeg to convert .h264 to .mp4 with optimized settings
    command = f'ffmpeg -i {shlex.quote(input_path)} -c:v copy -c:a copy {shlex.quote(output_path)}'
    subprocess.run(shlex.split(command), check=True)

def change_fps(cwd, input_video_path):
    output_dir = os.path.join(cwd, 'processed_videos')
    os.makedirs(output_dir, exist_ok=True)
    output_video_path = os.path.join(output_dir, f'{os.path.basename(input_video_path)[:-4]}_10_fps.mp4')

    if input_video_path.endswith('.h264'):
        # Convert .h264 to .mp4 if necessary
        mp4_output_path = input_video_path[:-5] + '.mp4'
        convert_h264_to_mp4(input_video_path, mp4_output_path)
        input_video_path = mp4_output_path

    # Load the video clip
    try:
        video_clip = VideoFileClip(input_video_path)
    except Exception as e:
        print(f"Error loading video file: {e}")
        return
    
    # Print the current FPS
    print(f"Current FPS: {video_clip.fps}")

    # Change the FPS to the target FPS
    new_video_clip = video_clip.set_fps(10)

    # Write the new video clip to a file
    new_video_clip.write_videofile(output_video_path, codec='libx264', fps=10, threads=4, preset='ultrafast')

    # Close the video clips
    video_clip.close()
    new_video_clip.close()


def create_graph_video(cwd, video_path):
    csv_path = f'{cwd}/data/{video_path.split("/")[-1].split("_")[1]}/csv_files/{ "_".join(video_path.split("/")[-1].split("_")[-6:-1])}.csv'
    
    # Load CSV data into a pandas DataFrame
    df = pd.read_csv(csv_path)

    # Ensure 'datetime' is in datetime format
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Create a figure with three subplots (3 rows, 1 column)
    fig, axs = plt.subplots(3, 1, figsize=(14, 7))

    # Precompute max values for scaling
    engine_speed_max = df['EngineSpeed'].max()
    fan_speed_max = df['FanSpeed'].max()
    fuel_rate_max = df['EngineFuelRateTMSCS'].max()

    # Plot Engine Speed
    axs[0].plot(df['datetime'], df['EngineSpeed'], label='Engine Speed')
    axs[0].plot(df['datetime'], df['NozGapOpen'] * engine_speed_max, label='NozGapOpen', linestyle='--')
    axs[0].legend()
    axs[0].set_xlabel('Time')
    axs[0].set_ylabel('Engine Speed (rpm)')
    axs[0].grid(True)

    # Plot Fan Speed
    axs[1].plot(df['datetime'], df['FanSpeed'], label='Fan Speed')
    axs[1].plot(df['datetime'], df['NozGapOpen'] * fan_speed_max, label='NozGapOpen', linestyle='--')
    axs[1].legend()
    axs[1].set_xlabel('Time')
    axs[1].set_ylabel('Fan Speed (rpm)')
    axs[1].grid(True)

    # Plot Fuel Rate
    axs[2].plot(df['datetime'], df['EngineFuelRateTMSCS'], label='Fuel Rate')
    axs[2].plot(df['datetime'], df['NozGapOpen'] * fuel_rate_max, label='NozGapOpen', linestyle='--')
    axs[2].legend()
    axs[2].set_xlabel('Time')
    axs[2].set_ylabel('Fuel Rate (L/h)')
    axs[2].grid(True)

    # Adjust layout to prevent overlap
    plt.tight_layout()

    # Initialize lines for the vertical marker on each subplot
    vertical_lines = [ax.axvline(x=df['datetime'].iloc[0], color='red', linestyle='--', linewidth=1) for ax in axs]

    # Define the update function for the animation
    def update(frame):
        datetime = df['datetime'].iloc[frame]
        for line in vertical_lines:
            line.set_xdata([datetime])
        return vertical_lines

    # Define writer parameters for saving the animation as MP4
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=10, metadata=dict(artist='Me'), bitrate=1800)  # Adjust bitrate as needed

    # Create the animation
    ani = animation.FuncAnimation(fig, update, frames=range(len(df)), blit=True)

    # Save the animation as an MP4 file
    output_path = f'{cwd}/processed_videos/{video_path.split("/")[-1][:-4]}_graph_video.mp4'
    ani.save(output_path, writer=writer)

    print(f'Animation saved to {output_path}')


def merge_videos(cwd, video_path):
    # Open video files
    graph_video_path = f'{cwd}/processed_videos/{video_path.split("/")[-1][:-4]}_graph_video.mp4'
    sweep_video_path = f'{cwd}/processed_videos/{video_path.split("/")[-1][:-4]}_10_fps.mp4'
    graph_video = cv2.VideoCapture(graph_video_path)
    sweep_video = cv2.VideoCapture(sweep_video_path)

    # Get video properties once
    graph_fps = graph_video.get(cv2.CAP_PROP_FPS)
    graph_width = int(graph_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    graph_height = int(graph_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    sweep_width = int(sweep_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    sweep_height = int(sweep_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    min_frames = min(int(graph_video.get(cv2.CAP_PROP_FRAME_COUNT)), int(sweep_video.get(cv2.CAP_PROP_FRAME_COUNT)))

    # Determine the aspect ratio for resizing the frames
    if sweep_height != 0:
        aspect_ratio = graph_height / sweep_height
    else:
        aspect_ratio = 1  # Default to 1 if sweep_height is 0 to avoid division by zero

    # Create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_path = f'{cwd}/processed_videos/{video_path.split("/")[-1]}'
    out = cv2.VideoWriter(output_path, fourcc, graph_fps, (int(graph_width + sweep_width * aspect_ratio), graph_height))

    # Pre-compute resized width
    resized_sweep_width = int(sweep_width * aspect_ratio)

    # Read, resize, and merge frames in a loop
    for _ in range(min_frames):
        ret_graph, frame_graph = graph_video.read()
        ret_sweep, frame_sweep = sweep_video.read()

        if not ret_graph or not ret_sweep:
            break

        # Resize sweep video to match the height of the graph video
        frame_sweep_resized = cv2.resize(frame_sweep, (resized_sweep_width, graph_height), interpolation=cv2.INTER_AREA)
        
        # Concatenate frames horizontally
        merged_frame = cv2.hconcat([frame_sweep_resized, frame_graph])

        # Write the frame to the output video
        out.write(merged_frame)

    # Release video objects and writer
    graph_video.release()
    sweep_video.release()
    out.release()

    print(f"Videos merged successfully! Merged video saved at: {output_path}")


def process_video(cwd, video_path):
    try:
        create_graph_video(cwd, video_path)
        print("Created graph video")
        change_fps(cwd, video_path)
        print("Changed FPS")
        merge_videos(cwd, video_path)
        print("Video merged successfully!")
        return video_path
    except Exception as e:
        print(f"Error processing video: {e}")
        return None

def process_videos(cwd, videos_to_process):
    processed_videos = []
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = [executor.submit(process_video, cwd, video_path) for video_path in videos_to_process]
        for future in as_completed(futures):
            result = future.result()
            if result:
                processed_videos.append(result)
    return processed_videos
