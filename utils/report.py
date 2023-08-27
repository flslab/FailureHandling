import json
from itertools import chain

import pandas as pd
import os
import csv


def get_report_metrics(dir_meta, time_range, group_num):
    json_file_path = os.path.join(dir_meta, 'charts.json')
    csv_path_flss = os.path.join(dir_meta, 'flss.csv')
    csv_path_points = os.path.join(dir_meta, 'illuminating.csv')

    try:
        # Read the JSON file
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)

        metrics = []

        for metric_name in ['dispatched', 'failed', 'mid_flight', 'illuminating']:
            if data[metric_name]['t'][-1] < time_range[1]:
                metrics.append(data[metric_name]['y'][-1])
            else:
                for i in range(len(data[metric_name]['t']) - 1, -1, -1):
                    if data[metric_name]['t'][i] <= time_range[1]:
                        metrics.append(data[metric_name]['y'][i])
                        break

        # for metric_name in ['mid_flight', 'illuminating']:
        #     avg_value = 0
        #     counter = 0
        #     for i in range(len(data[metric_name]['t'])):
        #         if time_range[0] <= data[metric_name]['t'][i] <= time_range[1]:
        #             avg_value += data[metric_name]['y'][i]
        #             counter += 1
        #     try:
        #         metrics.append(avg_value / counter)
        #     except Exception as e:
        #         print(f"An error occurred: {e}")
        #         metrics.append(0)

        metrics.extend(get_dist_metrics(csv_path_flss))
        metrics.extend(get_mttr_by_group(csv_path_points, group_num))

    except Exception as e:
        print(f"An error occurred: {e}")

    return metrics


def read_sanity_metrics(dir_meta, time_range):
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
                if time_range[0] <= data[metric_name]['t'][i] <= time_range[1]:
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


def get_dist_metrics(csv_path):
    dists = []
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                if eval(row['26_dist_traveled']) >= 0:
                    dists.append(eval(row['26_dist_traveled']))
            except ValueError:
                # Skip rows where the value is not a number
                continue

    if not dists:
        return [0, 0, 0, 0]
    dists.sort()

    mid = len(dists) // 2
    median = (dists[mid] + dists[~mid]) / 2

    return [sum(dists) / len(dists), dists[0], dists[-1], median]


def get_mttr_by_group(csv_path, group_num):
    mttr = [[] for i in range(group_num)]
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                group_id = int(row['group_id'])

                if row['hub wait times'] != "[]":
                    mttr[group_id].extend(eval(row['hub wait times']))

                if row['standby wait times'] != "[]":
                    mttr[group_id].extend(eval(row['standby wait times']))

            except ValueError:
                # Skip rows where the value is not a number
                continue

    if not mttr:
        return [0, 0, 0, 0]

    mttr_all = (list(chain.from_iterable(mttr)))
    mttr_all.sort()
    mid = len(mttr_all) // 2
    median = (mttr_all[mid] + mttr_all[~mid]) / 2

    return [sum(mttr_all) / len(mttr_all), mttr_all[0], mttr_all[-1], median]


def get_mttr(csv_path):
    mttr = []
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                if row['hub wait times'] != "[]":
                    mttr.extend(eval(row['hub wait times']))

                if row['standby wait times'] != "[]":
                    mttr.extend(eval(row['standby wait times']))

            except ValueError:
                # Skip rows where the value is not a number
                continue

    if not mttr:
        return [0, 0, 0, 0]

    mttr_all = (list(chain.from_iterable(mttr)))
    mttr_all.sort()
    mid = len(mttr_all) // 2
    median = (mttr_all[mid] + mttr_all[~mid]) / 2

    return [sum(mttr_all) / len(mttr_all), mttr_all[0], mttr_all[-1], median]


def get_report_metrics_no_group(dir_meta, time_range):
    json_file_path = os.path.join(dir_meta, 'charts.json')
    csv_path_flss = os.path.join(dir_meta, 'flss.csv')
    csv_path_points = os.path.join(dir_meta, 'illuminating.csv')

    try:
        # Read the JSON file
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)

        metrics = []

        for metric_name in ['dispatched', 'failed', 'mid_flight', 'illuminating']:
            if data[metric_name]['t'][-1] < time_range[1]:
                metrics.append(data[metric_name]['y'][-1])
            else:
                for i in range(len(data[metric_name]['t']) - 1, -1, -1):
                    if data[metric_name]['t'][i] <= time_range[1]:
                        metrics.append(data[metric_name]['y'][i])
                        break

        # for metric_name in ['mid_flight', 'illuminating']:
        #     avg_value = 0
        #     counter = 0
        #     for i in range(len(data[metric_name]['t'])):
        #         if time_range[0] <= data[metric_name]['t'][i] <= time_range[1]:
        #             avg_value += data[metric_name]['y'][i]
        #             counter += 1
        #     try:
        #         metrics.append(avg_value / counter)
        #     except Exception as e:
        #         print(f"An error occurred: {e}")
        #         metrics.append(0)

        metrics.extend(get_dist_metrics(csv_path_flss))
        metrics.extend(get_mttr_by_group(csv_path_points, 1))

    except Exception as e:
        print(f"An error occurred: {e}")

    return metrics
