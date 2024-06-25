from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from stats import calculate_statistics
from data_processing import create_df, process_data
from plot_graphs import draw_plots
from utils import change_cwd, extract_uploaded_files, clear_uploaded_files, clear_uploaded_videos
from video_processing import process_videos
import mimetypes

# Initialize Flask app
app = Flask(__name__, static_folder='../webpages', static_url_path='')
CORS(app)  # Enable CORS for all routes

# Function to fetch all available SNs (Serial Numbers)
def get_sns():
    cwd = os.getcwd()  # Get current working directory
    if not os.path.exists(os.path.join(cwd, 'data')):
        return []
    # List directories in 'data' folder
    sn_list = [sn for sn in os.listdir(os.path.join(cwd, 'data')) if os.path.isdir(os.path.join(cwd, 'data', sn))]
    return sn_list

# Serve the main page
@app.route('/')
def index():
    return app.send_static_file('index.html')

# Route to get the list of SNs
@app.route('/get_sns')
def get_sns_route():
    sns = get_sns()
    return jsonify({'sns': sns})

# Route to get data based on SN and date range
@app.route('/get_data')
def get_data():
    sn = request.args.get('sn')
    start_date = request.args.get('start')
    end_date = request.args.get('end')

    cwd = os.getcwd()

    # Create dataframe with the data
    combined_df, total_fuel_consumed, num_of_files = create_df(cwd, sn, start_date, end_date)

    if combined_df.empty:
        return jsonify({'error': 'No sweeping data for this SN'})

    # Calculate statistics and draw plots
    nozgap_event_durations, nozgapopen_stats_dict, fuel_dicts, dfs = calculate_statistics(combined_df)
    draw_plots(cwd, sn, dfs, nozgap_event_durations)

    data = {
        "total_fuel_consumed": total_fuel_consumed,
        "num_of_files": num_of_files,
        "nozgapopen_stats_dict": nozgapopen_stats_dict,
        "fuel_dicts": fuel_dicts,
        "graphs": [f'/graphs/{sn}/{graph}' for graph in os.listdir(f'{cwd}/graphs/{sn}') if graph.endswith('.png')]
    }

    return jsonify(data)

# Route to serve graph images
@app.route('/graphs/<sn>/<filename>')
def get_graph(sn, filename):
    graph_dir = os.path.join(os.getcwd(), 'graphs', sn)
    return send_from_directory(graph_dir, filename)

# Route to upload files
@app.route('/upload_files', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({'error': 'No files part in the request'}), 400

    uploaded_files = request.files.getlist('files')

    cwd = change_cwd()
    files_to_process = extract_uploaded_files(cwd, uploaded_files, 'log')
    data_processed = process_data(cwd, files_to_process)
    clear_uploaded_files(cwd)

    if data_processed:
        return jsonify({'message': 'Files successfully uploaded and processed'}), 200
    else:
        return jsonify({'error': 'No new files to process'}), 400

# Route to upload videos
@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video part in the request'}), 400
    
    uploaded_videos = request.files.getlist('video')
    
    cwd = change_cwd()
    videos_to_process = extract_uploaded_files(cwd, uploaded_videos, 'video')

    # Check for new videos to process
    new_videos_to_process = [vid_path for vid_path in videos_to_process if not os.path.exists(vid_path.replace('uploaded_videos', 'processed_videos'))]
    videos_processed = [vid_path.replace('uploaded_videos', 'processed_videos') for vid_path in videos_to_process if vid_path not in new_videos_to_process]
    if new_videos_to_process:
        videos_processed = process_videos(cwd, new_videos_to_process) + videos_processed
    clear_uploaded_videos(cwd)
    
    video_urls = [f'/processed_videos/{os.path.basename(video)}' for video in videos_processed]
    
    return jsonify({'video_urls': video_urls}), 200

# Route to serve processed videos
@app.route('/processed_videos/<filename>')
def get_processed_video(filename):
    video_dir = os.path.join(os.getcwd(), 'processed_videos')
    mime_type, _ = mimetypes.guess_type(filename)
    return send_from_directory(video_dir, filename, mimetype=mime_type)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
