from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from stats import calculate_statistics
from data_processing import create_df, process_data
from plot_graphs import draw_plots
from utils import change_cwd, extract_uploaded_files, clear_uploaded_files, clear_uploaded_videos, setup
from video_processing import process_video

cwd = change_cwd()
setup(cwd)
STATIC_DIR = os.path.join(cwd, 'app/static')
VIDEO_DIR = os.path.join(cwd, 'app/static/videos')
GRAPH_DIR = os.path.join(cwd, 'app/static/graphs')
TEMPLATES_DIR = os.path.join(cwd, 'app/templates')

# Initialize Flask app
app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='/static')
CORS(app)  # Enable CORS for all routes

# Serve the main page
@app.route('/')
def index():
    return send_from_directory(TEMPLATES_DIR, 'index.html')

# Route to get the list of SNs
@app.route('/get_sns')
def get_sns_route():
    if not os.path.exists(os.path.join(cwd, 'data')):
        sn_list = []
    else:
        sn_list = [sn for sn in os.listdir(os.path.join(cwd, 'data')) if os.path.isdir(os.path.join(cwd, 'data', sn))]
    return jsonify({'sns': sn_list})

# Route to get data based on SN and date range
@app.route('/get_data')
def get_data():
    sn = request.args.get('sn')
    start_date = request.args.get('start')
    end_date = request.args.get('end')

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
        "graphs": [f'/graphs/{sn}/{graph}' for graph in os.listdir(f'{cwd}/app/static/graphs/{sn}') if graph.endswith('.png')]
    }

    return jsonify(data)

# Route to serve graph images
@app.route('/graphs/<sn>/<filename>')
def get_graph(sn, filename):
    return app.send_static_file(f'graphs/{sn}/{filename}')

# Route to upload files
@app.route('/upload_files', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({'error': 'No files part in the request'}), 400

    uploaded_files = request.files.getlist('files')

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
    
    dropped_vids = request.files.getlist('video')
    valid_vids = [v for v in dropped_vids if v.filename.endswith('.mp4') or v.filename.endswith('.h264')]
    vids_to_upload = [v for v in valid_vids if v.filename not in os.listdir(os.path.join(VIDEO_DIR, v.filename.split('_')[1]))]
    processed_vids = [v.filename for v in valid_vids if v.filename in os.listdir(os.path.join(VIDEO_DIR, v.filename.split('_')[1]))]
    uploaded_vidnames = [os.path.basename(vid_path) for vid_path in extract_uploaded_files(cwd, vids_to_upload, 'video')]
    for vid_name in uploaded_vidnames:
        sn = vid_name.split('_')[1]
        if vid_name not in os.listdir(os.path.join(VIDEO_DIR, sn)):
            if process_video(cwd, os.path.join('uploads/videos', vid_name)) == True:
                processed_vids.append(vid_name)
    clear_uploaded_videos(cwd)
    processed_urls =[f'/videos/{vidname.split('_')[1]}/{vidname}' for vidname in processed_vids] 
    clear_uploaded_videos(cwd)
    print(processed_urls)
    return jsonify({'video_urls': processed_urls}), 200        
            

# Route to serve processed videos
@app.route('/videos/<sn>/<filename>')
def get_processed_video(sn, filename):
    return app.send_static_file(f'videos/{sn}/{filename}')

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
