import os
import sys
from io import BytesIO
from zipfile import ZipFile
import shutil

# Change the current working directory to the root of the project
def change_cwd():
    try:
        # Get the absolute path of the current script
        script_path = os.path.abspath(__file__)
        # Change the working directory to the root of the project
        os.chdir('/'.join(script_path.split('/')[:-2]))
        updated_cwd = os.getcwd()
        print('Current working directory:', updated_cwd)
        return updated_cwd
    except Exception as e:
        print('Error changing working directory:', e)
        sys.exit(1)

# Validate that log data exists within the target directory
def validate_files(files_to_process):
    try:
        for file_path in files_to_process:
            if not os.path.exists(file_path):
                # If file does not exist, remove it from the list
                print(f"File path {file_path} does not exist")
                files_to_process.remove(file_path)
                continue
            elif not file_path.endswith('.log'):
                # If file is not a log file, remove it from the list
                print(f"File path {file_path} is not a .log file")
                files_to_process.remove(file_path)
                os.remove(file_path)
                continue
        return files_to_process
    except Exception as e:
        print("Please provide a target directory: python3 run.py --target_dir /path/to/target_dir ", e)
        sys.exit(1)


def setup_sn_directories(cwd, sn_numbers):
    try:
        for sn in sn_numbers:
            if not os.path.exists(f'{cwd}/data/{sn}'):
                os.makedirs(f'{cwd}/data/{sn}')
                print(f'Created data/{sn} directory')
            
            if not os.path.exists(f'{cwd}/data/{sn}/log_files'):
                os.makedirs(f'{cwd}/data/{sn}/log_files')
                print(f'Created data/{sn}/log_files directory')

            if not os.path.exists(f'{cwd}/data/{sn}/csv_files'):
                os.makedirs(f'{cwd}/data/{sn}/csv_files')
                print(f'Created data/{sn}/csv_files directory')

            if not os.path.exists(f'{cwd}/data/{sn}/sweeping_csvs'):
                os.makedirs(f'{cwd}/data/{sn}/sweeping_csvs')
                print(f'Created data/{sn}/sweeping_csvs directory')

            if not os.path.exists(f'{cwd}/app/static/graphs/{sn}'):
                os.makedirs(f'{cwd}/app/static/graphs/{sn}')
                print(f'Created graphs/{sn} directory')

            if not os.path.exists(f'{cwd}/app/static/videos/{sn}'):
                os.makedirs(f'{cwd}/app/static/videos/{sn}')
                print(f'Created videos/{sn} directory')

    except Exception as e:
        print('Error setting up directories:', e)
        sys.exit(1)

# Create necessary directories for storing data and results if they do not already exist
def setup(cwd):
    try:
        if not os.path.exists(f'{cwd}/data'):
            os.makedirs(f'{cwd}/data')
            print('Created data directory')

        if not os.path.exists(f'{cwd}/uploads'):
            os.makedirs(f'{cwd}/uploads')
            print('Created uploads directory')

        if not os.path.exists(f'{cwd}/uploads/files'):
            os.makedirs(f'{cwd}/uploads/files')
            print('Created uploads/files directory')

        if not os.path.exists(f'{cwd}/uploads/videos'):
            os.makedirs(f'{cwd}/uploads/videos')
            print('Created uploads/videos directory')

        if not os.path.exists(f'{cwd}/app/static/graphs'):
            os.makedirs(f'{cwd}/app/static/graphs')
            print('Created static/graphs directory')

        if not os.path.exists(f'{cwd}/app/static/videos'):
            os.makedirs(f'{cwd}/app/static/videos')
            print('Created static/videos directory')

        if not os.path.exists(f'{cwd}/app/templates'):
            os.makedirs(f'{cwd}/app/static/videos')
            print('Created static/videos directory')

    except Exception as e:
        print('Error setting up directories:', e)
        sys.exit(1)

# Determine which trucks the data, in the given target directory, was taken from
def get_sn_numbers(files):
    try:
        # Extract SN numbers from log file names
        sn_numbers = list(set(f.split('/')[-1].split('_')[0] for f in files if f.endswith('.log')))
        if len(sn_numbers) == 0:
            print('No SN numbers found in log files')
            return []
        else:
            print('SN numbers found:', sn_numbers)
            return sn_numbers
    except Exception as e:
        print('Error getting SN numbers:', e)
        return []


# Extract uploaded files based on the file type
def extract_uploaded_files(cwd, uploaded_files, file_type):
    if file_type == 'log':
        supported_extensions = ['.log']
        directory_name = 'uploads/files'
    elif file_type == 'video':
        supported_extensions = ['.mp4', '.h264']
        directory_name = 'uploads/videos'
    else:
        raise ValueError("Unsupported file type. Use 'log' or 'video'.")

    # Create the upload directory if it does not exist
    upload_dir = os.path.join(cwd, directory_name)
    
    for file in uploaded_files:
        if any(file.filename.endswith(ext) for ext in supported_extensions):
            file.save(os.path.join(upload_dir, file.filename))
            print(f'File {file.filename} saved to {directory_name} directory')
        elif file.filename.endswith('.zip'):
            zip_file_stream = BytesIO(file.read())
            with ZipFile(zip_file_stream, 'r') as zip_file:
                zip_file.extractall(upload_dir)
                print(f'Files extracted from {file.filename}')
        else:
            print(f'Unsupported file type: {file.filename}')
            continue

    for item in os.listdir(upload_dir):
        item_path = os.path.join(upload_dir, item)
        if item.endswith('.zip'):
            os.remove(item_path)
            print(f'Removed zip file {item}')
        elif os.path.isdir(item_path):
            for sub_item in os.listdir(item_path):
                if any(sub_item.endswith(ext) for ext in supported_extensions):
                    shutil.move(os.path.join(item_path, sub_item), upload_dir)
                    print(f'Moved file {sub_item} to {directory_name} directory')
            shutil.rmtree(item_path)
            print(f'Removed directory {item}')
        elif not any(item.endswith(ext) for ext in supported_extensions):
            os.remove(item_path)
            print(f'Removed file {item}')

    # Get the paths of uploaded files
    uploaded_file_paths = [os.path.join(upload_dir, f) for f in os.listdir(upload_dir) if any(f.endswith(ext) for ext in supported_extensions)]

    return uploaded_file_paths

# Clear uploaded files
def clear_uploaded_files(cwd):
    try:
        for file in os.listdir(f'{cwd}/uploads/files'):
            os.remove(f'{cwd}/uploads/files/{file}')
        print('Uploaded files cleared')
    except Exception as e:
        print('Error clearing uploaded files:', e)
        sys.exit(1)

# Clear uploaded and processed videos
def clear_uploaded_videos(cwd):
    try:
        for video in os.listdir(f'{cwd}/uploads/videos'):
            os.remove(f'{cwd}/uploads/videos/{video}')
        print('Uploaded videos cleared')

        for video in os.listdir(f'{cwd}/app/static/videos'):
            if video.endswith('_graph_video.mp4') or video.endswith('_10_fps.mp4'):
                os.remove(f'{cwd}/app/static/videos/{video}')
        print('Processed videos cleared')

    except Exception as e:
        print('Error clearing uploaded videos:', e)
        sys.exit(1)


