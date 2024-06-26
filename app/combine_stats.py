import math
import os
import pickle

# Function to compute the weighted median of two datasets
def weighted_median(median1, count1, median2, count2):
    total_count = count1 + count2
    weight1 = count1 / total_count
    weight2 = count2 / total_count
    
    if median1 <= median2:
        return median1 + (median2 - median1) * weight2
    else:
        return median2 + (median1 - median2) * weight1

# Function to compute the combined mean of two datasets
def combined_mean(mean1, count1, mean2, count2):
    return (mean1*count1 + mean2*count2) / (count1 + count2)

# Function to compute the combined standard deviation of two datasets
def combined_stdev(stdev1, count1, mean1, stdev2, count2, mean2):
    comb_mean = combined_mean(mean1, count1, mean2, count2)
    combined_sumsq = (count1-1)*stdev1**2 + (count2-1)*stdev2**2 + count1*(mean1 - comb_mean)**2 + count2*(mean2 - comb_mean)**2
    combined_variance = combined_sumsq / (count1 + count2 - 1)
    return  math.sqrt(combined_variance)

# Function to compute the combined proportion of two datasets
def combined_proportion(total1, time1, total2, time2):
    return ((total1 + total2) / (time1 + time2))*100

# Function to combine nozzle gap open statistics from past and new data
def combine_nozgapopen_stats(past_noz, new_noz, past_fuel, new_fuel):
    print('Past NozGapOpen:', past_noz)
    print('New NozGapOpen:', new_noz)
    try:
        combined_noz = {
                'Total NozGapOpen Duration (hrs)': past_noz['Total NozGapOpen Duration (hrs)'] + new_noz['Total NozGapOpen Duration (hrs)'],
                'Mean NozGapOpen Duration (s)': combined_mean(past_noz['Mean NozGapOpen Duration (s)'], past_noz['NozGapOpen Event Count'], new_noz['Mean NozGapOpen Duration (s)'], new_noz['NozGapOpen Event Count']),
                'Median NozGapOpen Duration (s)': weighted_median(past_noz['Median NozGapOpen Duration (s)'], past_noz['NozGapOpen Event Count'], new_noz['Median NozGapOpen Duration (s)'], new_noz['NozGapOpen Event Count']),
                'Stdev NozGapOpen Duration (mins)': combined_stdev(past_noz['Stdev NozGapOpen Duration (mins)'], past_noz['NozGapOpen Event Count'], past_noz['Mean NozGapOpen Duration (s)'], new_noz['Stdev NozGapOpen Duration (mins)'], new_noz['NozGapOpen Event Count'], new_noz['Mean NozGapOpen Duration (s)']),
                'Max NozGapOpen Duration (mins)': max(past_noz['Max NozGapOpen Duration (mins)'], new_noz['Max NozGapOpen Duration (mins)']),
                'Min NozGapOpen Duration (s)': min(past_noz['Min NozGapOpen Duration (s)'], new_noz['Min NozGapOpen Duration (s)']),
                'NozGapOpen Event Count': past_noz['NozGapOpen Event Count'] + new_noz['NozGapOpen Event Count'],
                'Proportion NozGapOpen %': combined_proportion(past_noz['Total NozGapOpen Duration (hrs)'], past_fuel['All Data']['Total Time (hrs)'], new_noz['Total NozGapOpen Duration (hrs)'], new_fuel['All Data']['Total Time (hrs)'])
        }
        print('Combined NozGapOpen:', combined_noz)
        return combined_noz
    except Exception as e:
        print('Error combining nozgapopen stats:', e)
        return past_noz

# Function to combine fuel statistics from past and new data
def combine_fuel_stats(past_fuel, new_fuel):
    try:
        combined_fuel = {}

        print('Past Fuel:', past_fuel)
        print('New Fuel:', new_fuel)

        for data_category in past_fuel.keys():
            past_fuel_data = past_fuel[data_category]
            new_fuel_data = new_fuel[data_category]

            # Calculate counts based on total time and an assumed sampling rate of 0.1 seconds
            past_count = (past_fuel_data['Total Time (hrs)']*3600)/0.1
            new_count = (new_fuel_data['Total Time (hrs)']*3600)/0.1
            combined_fuel[data_category] = {
                    'Total Time (hrs)': past_fuel_data['Total Time (hrs)'] + new_fuel_data['Total Time (hrs)'],
                    'Total Fuel Consumed (L)': past_fuel_data['Total Fuel Consumed (L)'] + new_fuel_data['Total Fuel Consumed (L)'],

                    'Mean Fuel Rate (L/hr)': combined_mean(past_fuel_data['Mean Fuel Rate (L/hr)'], past_count, new_fuel_data['Mean Fuel Rate (L/hr)'], new_count),
                    'Median Fuel Rate (L/hr)': weighted_median(past_fuel_data['Median Fuel Rate (L/hr)'], past_count, new_fuel_data['Median Fuel Rate (L/hr)'], new_count),
                    'Stdev Fuel Rate (L/hr)': combined_stdev(past_fuel_data['Stdev Fuel Rate (L/hr)'], past_count, past_fuel_data['Mean Fuel Rate (L/hr)'], new_fuel_data['Stdev Fuel Rate (L/hr)'], new_count, new_fuel_data['Mean Fuel Rate (L/hr)']),
                    'Max Fuel Rate (L/hr)': max(past_fuel_data['Max Fuel Rate (L/hr)'], new_fuel_data['Max Fuel Rate (L/hr)']),
                    'Min Fuel Rate (L/hr)': min(past_fuel_data['Min Fuel Rate (L/hr)'], new_fuel_data['Min Fuel Rate (L/hr)']),

                    'Mean Engine Speed (rpm)': combined_mean(past_fuel_data['Mean Engine Speed (rpm)'], past_count, new_fuel_data['Mean Engine Speed (rpm)'], new_count),
                    'Median Engine Speed (rpm)': weighted_median(past_fuel_data['Median Engine Speed (rpm)'], past_count, new_fuel_data['Median Engine Speed (rpm)'], new_count),
                    'Stdev Engine Speed (rpm)': combined_stdev(past_fuel_data['Stdev Engine Speed (rpm)'], past_count, past_fuel_data['Mean Engine Speed (rpm)'], new_fuel_data['Stdev Engine Speed (rpm)'], new_count, new_fuel_data['Mean Engine Speed (rpm)']),
                    'Max Engine Speed (rpm)': max(past_fuel_data['Max Engine Speed (rpm)'], new_fuel_data['Max Engine Speed (rpm)']),
                    'Min Engine Speed (rpm)': min(past_fuel_data['Min Engine Speed (rpm)'], new_fuel_data['Min Engine Speed (rpm)']),

                    'Mean Fan Speed (rpm)': combined_mean(past_fuel_data['Mean Fan Speed (rpm)'], past_count, new_fuel_data['Mean Fan Speed (rpm)'], new_count),
                    'Median Fan Speed (rpm)': weighted_median(past_fuel_data['Median Fan Speed (rpm)'], past_count, new_fuel_data['Median Fan Speed (rpm)'], new_count),
                    'Stdev Fan Speed (rpm)': combined_stdev(past_fuel_data['Stdev Fan Speed (rpm)'], past_count, past_fuel_data['Mean Fan Speed (rpm)'], new_fuel_data['Stdev Fan Speed (rpm)'], new_count, new_fuel_data['Mean Fan Speed (rpm)']),
                    'Max Fan Speed (rpm)': max(past_fuel_data['Max Fan Speed (rpm)'], new_fuel_data['Max Fan Speed (rpm)']),
                    'Min Fan Speed (rpm)': min(past_fuel_data['Min Fan Speed (rpm)'], new_fuel_data['Min Fan Speed (rpm)'])
                }
            
        print('Combined Fuel:', combined_fuel)

        return combined_fuel
    except Exception as e:
        print('Error combining fuel stats:', e)
        return past_fuel

# Function to combine both nozzle gap open stats and fuel stats
def combine_results(past_nozgapopen_stats_dict, past_fuel_dicts, nozgapopen_stats_dict, fuel_dicts):
    return combine_nozgapopen_stats(past_nozgapopen_stats_dict, nozgapopen_stats_dict, past_fuel_dicts, fuel_dicts), combine_fuel_stats(past_fuel_dicts, fuel_dicts)

# Function to process past results and combine with new results
def process_past_results(cwd, sn, most_recent_results, nozgapopen_stats_dict, fuel_dicts, num_of_files, total_fuel_consumed):
    past_results = get_past_results(cwd, sn, most_recent_results)
    nozgapopen_stats_dict, fuel_dicts = combine_results(past_results['nozgapopen_stats_dict'], past_results['fuel_dicts'], nozgapopen_stats_dict, fuel_dicts)
    num_of_files += past_results['num_of_files']
    total_fuel_consumed += past_results['total_fuel_consumed']
    return nozgapopen_stats_dict, fuel_dicts, num_of_files, total_fuel_consumed

# Function to check if there are past results for a specific serial number
def past_results_check(cwd, sn):
    past_results = os.listdir(f'{cwd}/results/{sn}')
    if past_results != []:
        return max(past_results)
    else:
        return None

# Function to retrieve past results from a specified file
def get_past_results(cwd, sn, most_recent_results):
    with open(os.path.join(cwd, 'results', sn, most_recent_results, 'values.pkl'), 'rb') as f:
        past_results = pickle.load(f)
    return past_results
