import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set backend for matplotlib to 'Agg' to support non-interactive environments
plt.switch_backend('Agg')

# Plot the distribution of NozGapOpen event durations
def plot_nozgapopen_durations_dist(cwd, sn, nozgap_event_durations):
    plt.figure(figsize=(12, 6))
    plt.hist(nozgap_event_durations, bins=30, alpha=0.7)
    plt.xticks(np.arange(0, max(nozgap_event_durations), step=100))
    plt.xlim(0, max(nozgap_event_durations))  # Limit x-axis range
    plt.title('Distribution of NozGapOpen Events Duration')
    plt.xlabel('Duration (seconds)')
    plt.ylabel('Frequency')
    plt.savefig(f'{cwd}/app/static/graphs/{sn}/nozgapopen_durations_dist_plot.png')  # Save plot
    plt.close()

# Plot the correlation matrix for selected columns
def plot_corr_matrix(cwd, sn, df):
    plt.figure(figsize=(12, 6))
    correlation_matrix = df[['EngineSpeed', 'FanSpeed', 'EngineFuelRateTMSCS', 'NozGapOpen']].corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')  # Create heatmap
    plt.title('Correlation Matrix')
    plt.savefig(f'{cwd}/app/static/graphs/{sn}/correlation_matrix.png')  # Save plot
    plt.close()

# Plot the total NozGapOpen duration per bin
def plot_total_nozgapopen_duration_per_bin(cwd, sn, nozgap_event_durations):
    nozgap_event_durations = np.array(nozgap_event_durations)  # Convert to NumPy array

    # Create histogram to get bin edges
    counts, bin_edges = np.histogram(nozgap_event_durations, bins=30)

    # Calculate total duration for each bin
    total_durations = np.zeros_like(counts, dtype=float)
    for i in range(len(bin_edges) - 1):
        bin_mask = (nozgap_event_durations >= bin_edges[i]) & (nozgap_event_durations < bin_edges[i+1])
        total_durations[i] = nozgap_event_durations[bin_mask].sum() / 3600  # Convert to hours

    # Plotting
    plt.figure(figsize=(12, 6))
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

    # Convert bin centers from seconds to minutes
    bin_centers_minutes = bin_centers / 60

    plt.bar(bin_centers_minutes, total_durations, width=(bin_edges[1] - bin_edges[0]) / 60, alpha=0.7)
    plt.xlim(0, 20)
    plt.xticks(np.arange(0, 20, step=1))
    plt.title('Total Duration of NozGapOpen Events per Bin')
    plt.xlabel('Duration (minutes)')
    plt.ylabel('Total Duration (hours)')
    plt.savefig(f'{cwd}/app/static/graphs/{sn}/total_nozgapopen_durations_plot.png')  # Save plot
    plt.close()

# Plot the distribution of fuel rate
def plot_fuel_rate_dist(cwd, sn, dfs):
    plt.figure(figsize=(12, 6))
    for key in dfs.keys():
        plt.hist(dfs[key]['EngineFuelRateTMSCS'], bins=50, alpha=0.7, label=key)
    plt.title('Distribution of Fuel Rate')
    plt.xlabel('Fuel Rate (L/h)')
    plt.ylabel('Frequency')
    plt.legend()
    plt.yticks([])  # Hide y-axis numbers
    plt.xticks(np.arange(0, 25, step=1))
    plt.savefig(f'{cwd}/app/static/graphs/{sn}/fuel_rate_dist_plot.png')  # Save plot
    plt.close()

# Plot the distribution of fan speed
def plot_fan_speed_dist(cwd, sn, dfs):
    plt.figure(figsize=(12, 6))
    for key in dfs.keys():
        plt.hist(dfs[key]['FanSpeed'], bins=30, alpha=0.7, label=key)
    plt.yticks([])  # Hide y-axis numbers
    plt.xticks(np.arange(0, 3600, step=200))
    plt.title('Distribution of Fan Speed')
    plt.xlabel('Fan Speed (rpm)')
    plt.ylabel('Frequency')
    plt.legend()
    plt.savefig(f'{cwd}/app/static/graphs/{sn}/fan_speed_dist_plot.png')  # Save plot
    plt.close()

# Plot the distribution of engine speed
def plot_engine_speed_dist(cwd, sn, dfs):
    plt.figure(figsize=(12, 6))
    for key in dfs.keys():
        plt.hist(dfs[key]['EngineSpeed'], bins=30, alpha=0.7, label=key)
    plt.yticks([])  # Hide y-axis numbers
    plt.xticks(np.arange(800, 2200, step=100))
    plt.title('Distribution of Engine Speed')
    plt.xlabel('Engine Speed (rpm)')
    plt.ylabel('Frequency')
    plt.legend()
    plt.savefig(f'{cwd}/app/static/graphs/{sn}/engine_speed_dist_plot.png')  # Save plot
    plt.close()

# Generate all plots
def draw_plots(cwd, sn, dfs, nozgap_event_durations):
    print("Drawing plots...")
    plot_nozgapopen_durations_dist(cwd, sn, nozgap_event_durations)
    plot_total_nozgapopen_duration_per_bin(cwd, sn, nozgap_event_durations)
    plot_fuel_rate_dist(cwd, sn, dfs)
    plot_engine_speed_dist(cwd, sn, dfs)
    plot_fan_speed_dist(cwd, sn, dfs)
    plot_corr_matrix(cwd, sn, dfs['All Data'])
