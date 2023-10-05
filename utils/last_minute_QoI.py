import json
import numpy as np

# Replace with the actual file path
file_path = 'data.json'

# Read the JSON file
with open(file_path, 'r') as file:
    data = json.load(file)

# Extract the 'illuminating' data
illuminating_data = data.get('illuminating', {})
timestamps = illuminating_data.get('t', [])
values = illuminating_data.get('y', [])

# Filter the data based on the time stamps
filtered_values = [value for timestamp, value in zip(timestamps, values) if 1740 <= timestamp <= 1800]

# Calculate the average value per second
# Assuming the timestamps are in seconds and are integers
averages_per_second = []
for second in range(1740, 1801):
    values_in_second = [value for timestamp, value in zip(timestamps, values) if (timestamp >= second and timestamp< second + 1)]
    if values_in_second:
        averages_per_second.append(np.mean(values_in_second))

# Calculate the overall average of the averages per second
overall_average = np.mean(averages_per_second) if averages_per_second else None

print(f"Overall average: {overall_average}")
