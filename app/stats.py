import os
import pandas as pd

# Record the duration of each NozGapOpen event
def count_nozgapopen_events(combined_df):
    nozgap_event_durations = []  # List to store durations of NozGapOpen events
    event_count = 0  # Counter for the duration of the current NozGapOpen event
    nozgap_event = False  # Flag to indicate if a NozGapOpen event is ongoing

    try:
        for index, row in combined_df.iterrows():
            current_nozgap = row['NozGapOpen']
            
            if current_nozgap == 1.0:
                if not nozgap_event:
                    nozgap_event = True  # Start a new NozGapOpen event
                    event_count = 1  # Initialize the event counter
                else:
                    event_count += 1  # Continue counting the current event
            else:  # current_nozgap == 0.0
                if nozgap_event:
                    nozgap_event = False  # End the current NozGapOpen event
                    nozgap_event_duration = event_count * 0.1  # Calculate the duration in seconds
                    nozgap_event_durations.append(nozgap_event_duration)  # Store the duration
                    event_count = 0  # Reset the counter

        # If the dataframe ends with an open event, record its duration
        if nozgap_event:
            nozgap_event_duration = event_count * 0.1
            nozgap_event_durations.append(nozgap_event_duration)

        return nozgap_event_durations
    except Exception as e:
        print('Error counting nozgapopen events:', e)
        return []

# Calculate statistics for fuel rate, engine speed, and fan speed
def calculate_fuel_statistics(df):
    try:
        fuel_stats_dict = {
            'Total Time (hrs)': (len(df) * 0.1) / 3600,  # Convert total time from seconds to hours
            'Total Fuel Consumed (L)': df['fuel_consumed'].sum(),
            'Mean Fuel Rate (L/hr)': df['EngineFuelRateTMSCS'].mean(),
            'Median Fuel Rate (L/hr)': df['EngineFuelRateTMSCS'].median(),
            'Stdev Fuel Rate (L/hr)': df['EngineFuelRateTMSCS'].std(),
            'Max Fuel Rate (L/hr)': df['EngineFuelRateTMSCS'].max(),
            'Min Fuel Rate (L/hr)': df['EngineFuelRateTMSCS'].min(),

            'Mean Engine Speed (rpm)': df['EngineSpeed'].mean(),
            'Median Engine Speed (rpm)': df['EngineSpeed'].median(),
            'Stdev Engine Speed (rpm)': df['EngineSpeed'].std(),
            'Max Engine Speed (rpm)': df['EngineSpeed'].max(),
            'Min Engine Speed (rpm)': df['EngineSpeed'].min(),

            'Mean Fan Speed (rpm)': df['FanSpeed'].mean(),
            'Median Fan Speed (rpm)': df['FanSpeed'].median(),
            'Stdev Fan Speed (rpm)': df['FanSpeed'].std(),
            'Max Fan Speed (rpm)': df['FanSpeed'].max(),
            'Min Fan Speed (rpm)': df['FanSpeed'].min()
        }
        return fuel_stats_dict
    except Exception as e:
        print('Error calculating fuel statistics:', e)
        return {}

# Calculate statistics for NozGapOpen events
def nozgapopen_statistics(df):
    nozgap_event_durations = count_nozgapopen_events(df)
    if nozgap_event_durations == []:
        print('No NozGapOpen events')
        return {}
    try:
        nozgapopen_stats_dict = {
            'Total NozGapOpen Duration (hrs)': sum(nozgap_event_durations) / 3600,
            'Mean NozGapOpen Duration (s)': sum(nozgap_event_durations) / len(nozgap_event_durations),
            'Median NozGapOpen Duration (s)': sorted(nozgap_event_durations)[len(nozgap_event_durations) // 2],
            'Stdev NozGapOpen Duration (mins)': pd.Series(nozgap_event_durations).std() / 60,
            'Max NozGapOpen Duration (mins)': max(nozgap_event_durations) / 60,
            'Min NozGapOpen Duration (s)': min(nozgap_event_durations),
            'NozGapOpen Event Count': len(nozgap_event_durations),
            'Proportion NozGapOpen %': (sum(nozgap_event_durations) / (len(df) * 0.1)) * 100
        }
        return nozgap_event_durations, nozgapopen_stats_dict
    except Exception as e:
        print('Error calculating nozgapopen statistics:', e)
        return {}

# Calculate overall statistics
def calculate_statistics(combined_df):
    print("Calculating statistics...")
    try:
        fuel_dicts = {}  # Dictionary to store fuel statistics
        dfs = {
            'All Data': combined_df,
            'Nozzle Open': combined_df[combined_df['NozGapOpen'] == 1.0],
            'Nozzle Closed': combined_df[combined_df['NozGapOpen'] != 1.0]
        }
        for key in dfs.keys():
            if key == 'All Data':
                nozgap_event_durations, nozgapopen_stats_dict = nozgapopen_statistics(dfs[key])
            fuel_dicts[key] = calculate_fuel_statistics(dfs[key])
        
        return nozgap_event_durations, nozgapopen_stats_dict, fuel_dicts, dfs
    except Exception as e:
        print('Error calculating statistics:', e)
        return [], {}, {}, {}

# Write statistics to files
def write_statistics(cwd, sn, total_fuel_consumed, num_of_files, nozgapopen_stats_dict, fuel_dicts, dfs, nozgap_event_durations, current_datetime):
    print("Writing statistics...")
    try:
        # Create directories if they do not exist
        if not os.path.exists(f'{cwd}/results/{sn}/{current_datetime}'):
            os.makedirs(f'{cwd}/results/{sn}/{current_datetime}')
        # Write statistics to a text file
        with open(f'{cwd}/results/{sn}/{current_datetime}/statistics.txt', 'w') as f:
            f.write(f'{sn}\n\n')
            f.write(f'Total Fuel Consumed (L): {total_fuel_consumed}\n\n')
            f.write(f'Number of Sweeping Files: {num_of_files}\n\n')
            f.write(f'Nozzle Open Statistics:\n')
            for k, v in nozgapopen_stats_dict.items():
                f.write(f'{k}: {v}\n')
            for k, v in fuel_dicts.items():
                f.write(f'\n{k}:\n')
                for k1, v1 in v.items():
                    f.write(f'{k1}: {v1}\n')
    except Exception as e:
        print('Error writing statistics:', e)
