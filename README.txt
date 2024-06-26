# Sweeping Data Analysis and Visualization

This project is a web-based application for analyzing and visualizing sweeping truck data. The application provides functionalities for uploading log files and videos, processing data, generating statistics, and visualizing the results with plots and merged videos.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Functions](#functions)
- [Acknowledgments](#acknowledgments)

## Installation

1. **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Install the required dependencies
    ```bash
    pip install -r requirements.txt
    python3 app.py
    ```

## Usage

1. Upload log files:
    . Navigate to the '/upload_files' endpoints.
    . Select and upload the videos.
2. Upload videos:
    . Navigate to the '/upload_video'
    . Select and upload the videos
3. View available Serial Numbers (SNs):
    . Access the '/get_sns' endpoint to retrieve a list of available SNs.
4. Retrieve data and generate plots:
    . Use the '/get_data' endpoint with parameters 'sn', 'start', and 'end'
    to retrieve data and generate plots.
5. View generated plots and videos:
    . Access the '/graphs/<sn>/<filename>' and '/processed_videos/<filename>'
    endpoints to view the generated plots and processed videos.
   
## Project Structure

. app.py: Main Flask application, handles routing and API endpoints.
. data_processing.py: Functions for processing log files, creating CSV files, and generating data frames.
. plot_graphs.py: Functions for generating plots from the processed data.
. stats.py: Functions for calculating statistics from the data.
. utils.py: Utility functions for file handling and directory management.
. video_processing.py: Functions for processing and merging videos.
. combine_stats.py: Functions for combining past and new statistics.

## API Endpoints

. /: Serve the main page.
. /get_sns: Get the list of available Serial Numbers (SNs).
. /get_data: Get data and generate plots for a given SN and date range.
. /graphs/<sn>/<filename>: Serve the generated plot images.
. /upload_files: Upload log files.
. /upload_video: Upload videos.
. /processed_videos/<filename>: Serve the processed videos.

## Functions

# app.py
. get_sns(): Fetch all available SNs.
. index(): Serve the main page.
. get_sns_route(): Route to get the list of SNs.
. get_data(): Route to get data based on SN and date range.
. get_graph(sn, filename): Route to serve graph images.
. upload_files(): Route to upload log files.
. upload_video(): Route to upload videos.
. get_processed_video(filename): Route to serve processed videos.

# data_processing.py
. extract_log_files(): Extract log files from the target directory.
. create_csv_files(): Create CSV files from log files.
. create_sweeping_csv(): Create CSV files with sweeping data.
. create_df(): Create a DataFrame for a specific SN and date range.
. process_data(): Main function to process uploaded log files.

# plot_graphs.py
. plot_nozgapopen_durations_dist(): Plot distribution of NozGapOpen event durations.
. plot_corr_matrix(): Plot correlation matrix.
. plot_total_nozgapopen_duration_per_bin(): Plot total NozGapOpen duration per bin.
. plot_fuel_rate_dist(): Plot distribution of fuel rate.
. plot_fan_speed_dist(): Plot distribution of fan speed.
. plot_engine_speed_dist(): Plot distribution of engine speed.
. draw_plots(): Generate all plots.

# stats.py
count_nozgapopen_events(): Record durations of NozGapOpen events.
calculate_fuel_statistics(): Calculate statistics for fuel rate, engine speed, and fan speed.
nozgapopen_statistics(): Calculate statistics for NozGapOpen events.
calculate_statistics(): Calculate overall statistics.

# utils.py
. change_cwd(): Change the current working directory to the root of the project.
. validate_files(): Validate that log data exists within the target directory.
. setup(): Create necessary directories for storing data and results.
. get_sn_numbers(): Determine which trucks the data was taken from.
. extract_uploaded_files(): Extract uploaded files based on the file type.
. clear_uploaded_files(): Clear uploaded files.
. clear_uploaded_videos(): Clear uploaded and processed videos.

# video_processing.py
convert_h264_to_mp4(): Convert .h264 video files to .mp4.
change_fps(): Change the frame rate of videos.
create_graph_video(): Create a graph video from CSV data.
merge_videos(): Merge graph and sweep videos.
process_video(): Process a single video.
process_videos(): Process multiple videos in parallel.

# combine_stats.py
. weighted_median(): Compute the weighted median of two datasets.
. combined_mean(): Compute the combined mean of two datasets.
. combined_stdev(): Compute the combined standard deviation of two datasets.
. combined_proportion(): Compute the combined proportion of two datasets.
. combine_nozgapopen_stats(): Combine NozGapOpen statistics from past and new data.
. combine_fuel_stats(): Combine fuel statistics from past and new data.
. combine_results(): Combine both NozGapOpen stats and fuel stats.
. process_past_results(): Process past results and combine with new results.
. past_results_check(): Check if there are past results for a specific serial number.
. get_past_results(): Retrieve past results from a specified file.

# Acknowledgments
This project was developed to provide a comprehensive analysis and visualization tool for sweeping truck data, facilitating better data-driven decisions.
