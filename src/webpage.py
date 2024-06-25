import os
from combine_stats import past_results_check, get_past_results
import webbrowser

def create_webpage(cwd):
    # Generate HTML content
    html_content = """
    <html>
    <head>
        <title>Sweep Data Analysis</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            h1, h2, h3 {
                color: #333;
            }
            h1 {
                border-bottom: 2px solid #ddd;
                padding-bottom: 10px;
            }
            .section {
                margin-bottom: 40px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }
            table, th, td {
                border: 1px solid #ddd;
            }
            th, td {
                padding: 10px;
                text-align: left;
            }
            th {
                background-color: #f4f4f4;
            }
            img {
                max-width: 100%;
                height: auto;
                cursor: pointer;
                transition: transform 0.2s;
            }
            img:hover {
                transform: scale(1.05);
            }
            .img-container {
                margin-bottom: 20px;
            }
            .table-container {
                overflow-x: auto;
            }
        </style>
        <script>
            function openImageInNewWindow(src) {
                var newWindow = window.open("", "_blank", "width=1920,height=1080");
                newWindow.document.write("<html><head><title>Graph</title></head><body style='margin:0'><img src='" + src + "' style='width:100%; height:auto;'></body></html>");
            }

            function displaySNData(sn) {
                var sections = document.getElementsByClassName('section');
                for (var i = 0; i < sections.length; i++) {
                    sections[i].style.display = 'none';
                }
                document.getElementById(sn).style.display = 'block';
            }

            function handleFileSelect(event) {
                const file = event.target.files[0];
                if (file) {
                    processVideoFile(file);
                }
            }

            async function processVideoFile(file) {
                const formData = new FormData();
                formData.append('video', file);
                
                try {
                    const response = await fetch('http://127.0.0.1:5000/process_video', {
                        method: 'POST',
                        body: formData
                    });
                    const result = await response.json();
                    alert(result.message);
                } catch (error) {
                    console.error('Error:', error);
                }
            }
        </script>
    </head>
    <body>
    <div class="container">
    <h1>Sweep Data Analysis</h1>
    <div class="form-group">
        <label for="snDropdown">Select SN:</label>
        <select class="form-control" id="snDropdown" onchange="displaySNData(this.value)">
            <option value="">-- Select SN --</option>
    """

    sn_data_dict = {}
    for sn in os.listdir(os.path.join(cwd, 'results')):
        most_recent_results = os.path.join(cwd, 'results', sn, past_results_check(cwd, sn))
        sn_data = get_past_results(cwd, sn, most_recent_results)
        sn_data_dict[sn] = sn_data
        
        html_content += f'<option value="{sn}">{sn}</option>'

    html_content += """
        </select>
    </div>
    """

    for sn, sn_data in sn_data_dict.items():
        html_content += f"""
        <div id="{sn}" class="section" style="display:none;">
            <h2>{sn}</h2>
            <p><strong>Total Fuel Consumed:</strong> {sn_data['total_fuel_consumed']}</p>
            <p><strong>Number of Files Processed:</strong> {sn_data['num_of_files']}</p>
            
            <h3>Nozzle Statistics:</h3>
            <div class="table-container">
            <table class="table">
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
        """
        for key, value in sn_data['nozgapopen_stats_dict'].items():
            html_content += f"""
                    <tr>
                        <td>{key}</td>
                        <td>{value}</td>
                    </tr>
            """
        
        html_content += """
                </tbody>
            </table>
            </div>
        """

        # Combined Table
        html_content += """
            <h3>Statistics</h3>
            <div class="table-container">
            <table class="table">
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>All Data</th>
                        <th>Nozzle Open</th>
                        <th>Nozzle Closed</th>
                    </tr>
                </thead>
                <tbody>
        """

        combined_data = {
            "Total Time (hrs)": [sn_data['fuel_dicts']['All Data']['Total Time (hrs)'],
                                 sn_data['fuel_dicts']['Nozzle Open']['Total Time (hrs)'],
                                 sn_data['fuel_dicts']['Nozzle Closed']['Total Time (hrs)']],
            "Total Fuel Consumed (L)": [sn_data['fuel_dicts']['All Data']['Total Fuel Consumed (L)'],
                                        sn_data['fuel_dicts']['Nozzle Open']['Total Fuel Consumed (L)'],
                                        sn_data['fuel_dicts']['Nozzle Closed']['Total Fuel Consumed (L)']],
            "Mean Fuel Rate (L/hr)": [sn_data['fuel_dicts']['All Data']['Mean Fuel Rate (L/hr)'],
                                      sn_data['fuel_dicts']['Nozzle Open']['Mean Fuel Rate (L/hr)'],
                                      sn_data['fuel_dicts']['Nozzle Closed']['Mean Fuel Rate (L/hr)']],
            "Median Fuel Rate (L/hr)": [sn_data['fuel_dicts']['All Data']['Median Fuel Rate (L/hr)'],
                                        sn_data['fuel_dicts']['Nozzle Open']['Median Fuel Rate (L/hr)'],
                                        sn_data['fuel_dicts']['Nozzle Closed']['Median Fuel Rate (L/hr)']],
            "Stdev Fuel Rate (L/hr)": [sn_data['fuel_dicts']['All Data']['Stdev Fuel Rate (L/hr)'],
                                       sn_data['fuel_dicts']['Nozzle Open']['Stdev Fuel Rate (L/hr)'],
                                       sn_data['fuel_dicts']['Nozzle Closed']['Stdev Fuel Rate (L/hr)']],
            "Max Fuel Rate (L/hr)": [sn_data['fuel_dicts']['All Data']['Max Fuel Rate (L/hr)'],
                                     sn_data['fuel_dicts']['Nozzle Open']['Max Fuel Rate (L/hr)'],
                                     sn_data['fuel_dicts']['Nozzle Closed']['Max Fuel Rate (L/hr)']],
            "Min Fuel Rate (L/hr)": [sn_data['fuel_dicts']['All Data']['Min Fuel Rate (L/hr)'],
                                     sn_data['fuel_dicts']['Nozzle Open']['Min Fuel Rate (L/hr)'],
                                     sn_data['fuel_dicts']['Nozzle Closed']['Min Fuel Rate (L/hr)']],
            "Mean Engine Speed (rpm)": [sn_data['fuel_dicts']['All Data']['Mean Engine Speed (rpm)'],
                                        sn_data['fuel_dicts']['Nozzle Open']['Mean Engine Speed (rpm)'],
                                        sn_data['fuel_dicts']['Nozzle Closed']['Mean Engine Speed (rpm)']],
            "Median Engine Speed (rpm)": [sn_data['fuel_dicts']['All Data']['Median Engine Speed (rpm)'],
                                          sn_data['fuel_dicts']['Nozzle Open']['Median Engine Speed (rpm)'],
                                          sn_data['fuel_dicts']['Nozzle Closed']['Median Engine Speed (rpm)']],
            "Stdev Engine Speed (rpm)": [sn_data['fuel_dicts']['All Data']['Stdev Engine Speed (rpm)'],
                                         sn_data['fuel_dicts']['Nozzle Open']['Stdev Engine Speed (rpm)'],
                                         sn_data['fuel_dicts']['Nozzle Closed']['Stdev Engine Speed (rpm)']],
            "Max Engine Speed (rpm)": [sn_data['fuel_dicts']['All Data']['Max Engine Speed (rpm)'],
                                       sn_data['fuel_dicts']['Nozzle Open']['Max Engine Speed (rpm)'],
                                       sn_data['fuel_dicts']['Nozzle Closed']['Max Engine Speed (rpm)']],
            "Min Engine Speed (rpm)": [sn_data['fuel_dicts']['All Data']['Min Engine Speed (rpm)'],
                                       sn_data['fuel_dicts']['Nozzle Open']['Min Engine Speed (rpm)'],
                                       sn_data['fuel_dicts']['Nozzle Closed']['Min Engine Speed (rpm)']],
            "Mean Fan Speed (rpm)": [sn_data['fuel_dicts']['All Data']['Mean Fan Speed (rpm)'],
                                     sn_data['fuel_dicts']['Nozzle Open']['Mean Fan Speed (rpm)'],
                                     sn_data['fuel_dicts']['Nozzle Closed']['Mean Fan Speed (rpm)']],
            "Median Fan Speed (rpm)": [sn_data['fuel_dicts']['All Data']['Median Fan Speed (rpm)'],
                                       sn_data['fuel_dicts']['Nozzle Open']['Median Fan Speed (rpm)'],
                                       sn_data['fuel_dicts']['Nozzle Closed']['Median Fan Speed (rpm)']],
            "Stdev Fan Speed (rpm)": [sn_data['fuel_dicts']['All Data']['Stdev Fan Speed (rpm)'],
                                      sn_data['fuel_dicts']['Nozzle Open']['Stdev Fan Speed (rpm)'],
                                      sn_data['fuel_dicts']['Nozzle Closed']['Stdev Fan Speed (rpm)']],
            "Max Fan Speed (rpm)": [sn_data['fuel_dicts']['All Data']['Max Fan Speed (rpm)'],
                                    sn_data['fuel_dicts']['Nozzle Open']['Max Fan Speed (rpm)'],
                                    sn_data['fuel_dicts']['Nozzle Closed']['Max Fan Speed (rpm)']],
            "Min Fan Speed (rpm)": [sn_data['fuel_dicts']['All Data']['Min Fan Speed (rpm)'],
                                    sn_data['fuel_dicts']['Nozzle Open']['Min Fan Speed (rpm)'],
                                    sn_data['fuel_dicts']['Nozzle Closed']['Min Fan Speed (rpm)']],
        }

        for metric, values in combined_data.items():
            html_content += f"""
                <tr>
                    <td>{metric}</td>
                    <td>{values[0]}</td>
                    <td>{values[1]}</td>
                    <td>{values[2]}</td>
                </tr>
            """
        
        html_content += """
                </tbody>
            </table>
            </div>
        """

        html_content += """
            <h3>Graphs:</h3>
            <div class="row">
        """
        most_recent_results = os.path.join(cwd, 'results', sn, past_results_check(cwd, sn))
        for graph_file in os.listdir(most_recent_results):
            if graph_file.endswith('.png'):
                graph_path = os.path.join(most_recent_results, graph_file).replace('\\', '/')
                html_content += f"""
                <div class="col-md-4 img-container">
                    <img src="{graph_path}" alt="{graph_file}" class="img-fluid" onclick="openImageInNewWindow('{graph_path}')">
                </div>
                """
        
        html_content += """
            </div>
        </div>
        """

    html_content += """
    <div class="form-group">
        <label for="videoInput">Select Video:</label>
        <input type="file" class="form-control-file" id="videoInput" accept="video/*" onchange="handleFileSelect(event)">
    </div>
    </div>
    </body>
    </html>
    """

    # Write HTML content to a file
    os.makedirs("webpages", exist_ok=True)
    with open("webpages/sweep_analysis.html", "w") as f:
        f.write(html_content)

    webbrowser.open("webpages/sweep_analysis.html")

