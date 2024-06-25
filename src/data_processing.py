import os
import sys
import shutil
import csv
import pandas as pd
from utils import validate_files, get_sn_numbers, setup
from concurrent.futures import ProcessPoolExecutor

# Extract log files from target directory and copy them to data/sn_number/log_files
def extract_log_files(cwd, files, sn_numbers):
    all_files_already_exist = True
    # Dictionary to store log file names for each SN number
    log_file_names = {}
    try:
        # Iterate over each SN number to find corresponding log files
        for sn in sn_numbers:
            log_files = [f.split('/')[-1] for f in files if f.split('/')[-1].startswith(sn) and f.endswith('.log')]
            log_file_names[sn] = log_files

            # Copy log files to their respective directories if they don't already exist
            for log_file_name in log_file_names[sn]:
                if not os.path.exists(f'{cwd}/data/{sn}/log_files/{log_file_name}'):
                    shutil.copy(f'{cwd}/uploaded_files/{log_file_name}', f'{cwd}/data/{sn}/log_files')
                    all_files_already_exist = False

        # Return a message if all files already exist
        if all_files_already_exist:
            print('All log files already exist in data directory')
            return []
        else:
            print(f'Copied log files for {sn}')
            return log_file_names
    except Exception as e:
        print('Error copying log files:', e)
        return []

# Create csv files from the extracted log files copied to data/sn_number/log_files
def create_csv_files(cwd, sn_numbers, log_file_names):
    # Iterate over each SN number to process its log files
    for sn in sn_numbers:
        log_files = log_file_names[sn]
        for log_file in log_files:
            try:
                with open(f'{cwd}/data/{sn}/log_files/{log_file}', 'r') as f:
                    lines = f.readlines()
                    csv_file = log_file.replace('.log', '.csv')
                    # Create CSV files if they don't already exist
                    if not os.path.exists(f'{cwd}/data/{sn}/csv_files/{csv_file}'):
                        with open(f'{cwd}/data/{sn}/csv_files/{csv_file}', 'w') as c:
                            writer = csv.writer(c)
                            prev_line = ''
                            start_of_data = False
                            for line in lines:
                                if prev_line.startswith('[data]'):
                                    start_of_data = True
                                if start_of_data:
                                    writer.writerow(line.split(' '))
                                elif prev_line.startswith('[column names]'):
                                    writer.writerow(line.split(' '))
                                prev_line = line
                        print(f'Created {csv_file} for {sn}')
                        # Create sweeping CSV if the created CSV is not empty
                        if not os.path.getsize(f'{cwd}/data/{sn}/csv_files/{csv_file}') == 0:
                            create_sweeping_csv(cwd, sn, csv_file)
            except Exception as e:
                print(f'Error creating csv file from: {log_file}', e)
                continue

# Create new csvs consisting of only rows where the truck is sweeping
def create_sweeping_csv(cwd, sn, csv_file):
    try:
        df = pd.read_csv(f'{cwd}/data/{sn}/csv_files/{csv_file}')

        time_interval_hours = 0.1 / 3600
        df['fuel_consumed'] = df['EngineFuelRateTMSCS'] * time_interval_hours
        df['cumulative_fuel_consumed'] = df['fuel_consumed'].cumsum()
        df['datetime'] = pd.to_datetime('-'.join(csv_file.split('_')[1:4]) + ' ' + df['time'], format='%Y-%m-%d %H:%M:%S.%f')
        df.to_csv(f'{cwd}/data/{sn}/csv_files/{csv_file}', index=False)

        # Create new CSV with only rows that have Nozzle1downTMSCS or Nozzle2downTMSCS == 1.0
        df = df[((df['Nozzle1downTMSCS'] == 1.0) | (df['Nozzle2downTMS'] == 1.0))]
        if df.empty:
            print(f'No sweeping data in {csv_file}')
            return ''
        
        df.to_csv(f'{cwd}/data/{sn}/sweeping_csvs/{csv_file}', index=False)
        print(f'Created sweeping csv file for {csv_file} in {sn}')
        return csv_file
    except Exception as e:
        print(f'Error writing sweeping csv file: {csv_file}', e)
        sys.exit(1)

# Filter files based on dates in the file name format 'SN213390_YYYY_MM_DD_HHMM.csv'
def filter_file_dates(file_name, start_date, end_date):
    try:
        # Extract the date part from the file name
        date_str = file_name.split('_')[1:4]  # ['YYYY', 'MM', 'DD']
        file_date = pd.to_datetime('-'.join(date_str), format='%Y-%m-%d')
        return start_date <= file_date <= end_date
    except (ValueError, IndexError):
        return False

# Process a single file by reading it and filtering by date range
def process_file(file_path, start_date, end_date):
    try:
        df = pd.read_csv(file_path)
        # Convert datetime column to pandas datetime
        df['datetime'] = pd.to_datetime(df['datetime'])
        # Filter by date range
        df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]
        if df.empty:
            return pd.DataFrame(), 0
        csv_fuel_consumed = df['TotalFuelConsumption'].iloc[-1] - df['TotalFuelConsumption'].iloc[0]
        csv_fuel_consumed = csv_fuel_consumed if csv_fuel_consumed is not None else 0
        return df, csv_fuel_consumed
    except Exception as e:
        print(f'Error reading sweeping csv file: {file_path}', e)
        return pd.DataFrame(), 0

# Create a dataframe for a specific SN number and date range
def create_df(cwd, sn, start_date, end_date):
    data_dir = f'{cwd}/data/{sn}/sweeping_csvs'
    data_files = os.listdir(data_dir)

    # Convert start_date and end_date to datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter files by date range
    data_files = [f for f in data_files if filter_file_dates(f, start_date, end_date)]

    print(f'Creating dataframe for {sn}, between {start_date} and {end_date}...')
    total_fuel_consumption = []
    combined_df = pd.DataFrame()
    num_of_files = 0

    # Use ProcessPoolExecutor to process files in parallel
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_file, f'{data_dir}/{csv_file}', start_date, end_date) for csv_file in data_files]
        for future in futures:
            df, fuel_consumed = future.result()
            if not df.empty:
                combined_df = pd.concat([combined_df, df])
                total_fuel_consumption.append(fuel_consumed)
                num_of_files += 1

    # Total Fuel Consumed
    total_fuel_consumed = sum(total_fuel_consumption)

    print("Dataframe created")
    return combined_df, total_fuel_consumed, num_of_files


# Main function to process data
def process_data(cwd, files_to_process):
    # Validate and select files to process
    validated_files_to_process = validate_files(files_to_process)
    if validated_files_to_process == []:
        print('No new files to process')
        return False
    print('Uploaded files validated:', validated_files_to_process)

    # Retrieve SN numbers from the validated files
    sn_numbers = get_sn_numbers(validated_files_to_process)
    if sn_numbers == []:
        print('No SN numbers in data')
        return False
    print('SN numbers in data retrived:', sn_numbers)

    # Setup directories for the SN numbers
    setup(cwd, sn_numbers)
    print("Directories setup")

    # Extract log files
    log_file_names = extract_log_files(cwd, validated_files_to_process, sn_numbers)
    if log_file_names == []:
        print('No new log files to process')
        return False
    print("Log files extracted")

    # Create CSV files from log files
    create_csv_files(cwd, sn_numbers, log_file_names)
    print("CSV files created")

    return True
