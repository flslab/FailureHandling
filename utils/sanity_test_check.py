import json
import pandas as pd
import os
import csv


def read_metrics(dir_meta, time_range):
    json_file_path = os.path.join(dir_meta, 'charts.json')
    csv_path_mttf = os.path.join(dir_meta, 'flss.csv')
    csv_path_mttr = os.path.join(dir_meta, 'illuminating.csv')
    try:
        # Read the JSON file
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)

        metrics = []

        if data['failed']['t'][-1] < time_range[1]:
            metrics.append(data['failed']['y'][-1])
        else:
            for i in range(len(data['failed']['t']) - 1, -1, -1):
                if data['failed']['t'][i] <= time_range[1]:
                    metrics.append(data['failed']['y'][i])
                    break

        for metric_name in ['mid_flight', 'illuminating']:
            avg_value = 0
            counter = 0
            for i in range(len(data[metric_name]['t'])):
                if time_range[0] <= data[metric_name]['t'][i] <= time_range[1] :
                    avg_value += data[metric_name]['y'][i]
                    counter += 1
            try:
                metrics.append(avg_value / counter)
            except Exception as e:
                print(f"An error occurred: {e}")
                metrics.append(0)

        metrics.append(calculate_mean(csv_path_mttf, "27_time_to_fail"))
        metrics.append(calculate_mttr(csv_path_mttr))

    except Exception as e:
        print(f"An error occurred: {e}")

    return metrics


def calculate_mttr(csv_path):
    wait_list = []

    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                if row['hub wait times'] != "[]":
                    wait_list.extend(row['hub wait times'][1:-1].split(', '))
                if row['standby wait times'] != "[]":
                    wait_list.extend(row['standby wait times'][1:-1].split(', '))
            except ValueError:
                # Skip rows where the value is not a number
                continue

    if not wait_list:
        return -1

    float_list = [float(s) for s in wait_list]
    return sum(float_list) / len(float_list)


def calculate_mean(csv_path, column_heading):
    values = []

    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                value = float(row[column_heading])
                if value > 0:
                    values.append(value)
            except ValueError:
                # Skip rows where the value is not a number
                continue

    if not values:
        return None

    return sum(values) / len(values)
