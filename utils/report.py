import json
from itertools import chain
import pandas as pd
import os
import csv
import math

from config import Config
from worker.metrics import gen_point_metrics_no_group
from utils.file import write_csv


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
                if counter > 0:
                    metrics.append(avg_value / counter)
                else:
                    metrics.append(0)
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
        metrics.extend(get_dist_metrics(csv_path_flss))
        metrics.extend(get_mttr_by_group(csv_path_points, 1))

    except Exception as e:
        print(f"An error occurred: {e}")

    return metrics


def create_csv_from_timeline(directory):
    if not os.path.exists(directory):
        return

    with open(os.path.join(directory, 'timeline.json'), "r") as file:
        timeline = json.load(file)

    point_metrics, standby_metrics = gen_point_metrics_no_group(timeline, 0)
    write_csv(directory, point_metrics, 'illuminating')
    write_csv(directory, standby_metrics, 'standby')

    return timeline


def write_final_report(csv_file_path, target_file_path, name, group_num, time_range):
    # if os.path.exists(os.path.join(csv_file_path, name +'_final_report.csv')):
    #     return

    report_key = [
        "Total Dispatched",
        "Total Failed",
        "Mid-Flight",
        "Illuminating",
        "Avg Dist Traveled",
        "Min Dist Traveled",
        "Max Dist Traveled",
        "Median Dist Traveled",
        "Avg MTTR",
        "Min MTTR",
        "Max MTTR",
        "Median MTTR",
        "Deploy Rate",
        "Number of Groups",
    ]
    report_metrics = get_report_metrics_no_group(csv_file_path, time_range)
    report_metrics = [metric for metric in report_metrics]
    report_metrics.append(Config.DISPATCH_RATE)

    report_metrics.append(group_num)

    report = []

    for i in range(len(report_key)):
        report.append([report_key[i], report_metrics[i]])

    df = pd.read_csv(os.path.join(csv_file_path, 'flss.csv'))

    # 3. Split the dataframe based on the condition
    dist1 = df[df['timeline'].str.contains(' 1, ')]
    dist2 = df[~df['timeline'].str.contains(' 1, ')]

    dist3 = df[df['timeline'].str.contains(' 2, ')]
    dist3 = dist3[dist3['timeline'].str.contains(' 6, ')]
    dist_3_list = []
    for i in dist3.index:
        fls_timeline = eval(dist3['timeline'][i])
        for event in fls_timeline:
            if event[1] == 2:
                standby_coord = event[2]
            elif event[1] == 6:
                dist_3_list.append(distance_between(standby_coord, event[2]))
                break

    dist4 = df[df['timeline'].str.contains(' 6, ')]
    dist4 = dist4[~dist4['timeline'].str.contains(' 2, ')]

    dispatcher_coords = get_dispatcher_coords()

    dist_standby_hub_to_centroid = df[df['timeline'].str.contains(' 2, ')]
    dist_hub_to_centroid = []

    for i in dist_standby_hub_to_centroid.index:
        fls_timeline = eval(dist_standby_hub_to_centroid['timeline'][i])

        for event in fls_timeline:
            if event[1] == 2:
                standby_coord = event[2]
                dispatcher_coord = check_dispatcher(dispatcher_coords, standby_coord)
                dist_hub_to_centroid.append(distance_between(dispatcher_coord, standby_coord))
                break

    dist_standby_hub_to_fail_before_centroid = df[df['timeline'].str.contains(' 5, ')]
    dist_standby_hub_to_fail_before_centroid = dist_standby_hub_to_fail_before_centroid[
        ~dist_standby_hub_to_fail_before_centroid['timeline'].str.contains(' 4, ')]

    dist_standby_centroid_to_fail_before_recovered = df[df['timeline'].str.contains(' 2, ')]

    dist_standby_centroid_to_fail_before_recovered = dist_standby_centroid_to_fail_before_recovered[
        dist_standby_centroid_to_fail_before_recovered['timeline'].str.contains(' 4, ')]
    dist_standby_centroid_to_fail_before_recovered = dist_standby_centroid_to_fail_before_recovered[
        dist_standby_centroid_to_fail_before_recovered['timeline'].str.contains(' 5, ')]
    dist_standby_centroid_to_fail_before_recovered = dist_standby_centroid_to_fail_before_recovered[
        ~dist_standby_centroid_to_fail_before_recovered['timeline'].str.contains(' 6, ')]
    dist_centroid_to_fail = []
    for i in dist_standby_centroid_to_fail_before_recovered.index:
        fls_timeline = eval(dist_standby_centroid_to_fail_before_recovered['timeline'][i])
        for event in fls_timeline:
            if event[1] == 2:
                standby_coord = event[2]
                dispatcher_coord = check_dispatcher(dispatcher_coords, standby_coord)
                dist_centroid_to_fail.append(dist_standby_centroid_to_fail_before_recovered['26_dist_traveled'][i] -
                            distance_between(dispatcher_coord, standby_coord))
                break

    # Extract '26_dist_traveled' column values
    dist1_values = dist1['26_dist_traveled']
    dist2_values = dist2['26_dist_traveled']
    # dist3_values = dist3['26_dist_traveled']
    dist4_values = dist4['26_dist_traveled']
    # dist_standby_hub_to_centroid = dist_standby_hub_to_centroid['26_dist_traveled']
    dist_standby_hub_to_fail_before_centroid = dist_standby_hub_to_fail_before_centroid['26_dist_traveled']
    # dist_standby_centroid_to_fail_before_recovered = dist_standby_centroid_to_fail_before_recovered['26_dist_traveled']

    min_value = []
    max_value = []
    average_value = []
    median_value = []

    # 4. Calculate the required statistics for sheet1
    values = [dist1_values, dist2_values, dist_3_list, dist4_values,
              dist_hub_to_centroid,
              dist_standby_hub_to_fail_before_centroid,
              dist_centroid_to_fail]

    for value in values:
        if not isinstance(value, list):
            value = value.tolist()
        value.sort()

        mid = len(value) // 2
        median = (value[mid] + value[~mid]) / 2 if mid > 0 else 0

        min_value.append(value[0] if len(value) > 0 else 0)
        max_value.append(value[-1] if len(value) > 0 else 0)
        average_value.append(sum(value) / len(value) if len(value) > 0 else 0)
        median_value.append(median)

    titles_type = ['dist_arrived_illuminate', 'dist_failed_midflight_illuminate',
                   'dist_stationary_standby_recover_illuminate', 'dist_midflight_standby_recover_illuminate',
                   'dist_standby_hub_to_centroid',
                   'dist_standby_hub_to_fail_before_centroid', 'dist_standby_centroid_to_fail_before_recovered']

    for i, title in enumerate(titles_type):
        report.append(['Min_' + title, min_value[i]])
        report.append(['Max_' + title, max_value[i]])
        report.append(['Avg_' + title, average_value[i]])
        report.append(['Median_' + title, median_value[i]])

    df = pd.read_csv(os.path.join(csv_file_path, 'illuminating.csv'))
    recover_by_hub = df['recovered by hub']
    recover_by_standby = df['recovered by standby']

    report.append(['Illuminate Recovered_By_HUB', sum(recover_by_hub)])
    report.append(['Illuminate Recovered_By_Standby', sum(recover_by_standby)])

    df = pd.read_csv(os.path.join(csv_file_path, 'standby.csv'))
    standby_recover_by_hub = df['recovered by hub']

    report.append(['Standby Recovered_By_HUB', sum(standby_recover_by_hub)])

    df = pd.read_csv(os.path.join(csv_file_path, 'metrics.csv'))
    filtered_row = df[df['Metric'] == 'Queued FLSs']
    report.append(['Queued FLSs', filtered_row['Value'].iloc[0]])

    with open(os.path.join(csv_file_path, 'timeline.json'), 'r') as json_file:
        events = json.load(json_file)
        failed_standby = 0
        failed_illum = 0
        for event in events:
            if event[1] == 3:
                failed_illum += 1
            elif event[1] == 5:
                failed_standby += 1

    report.append(['Failed Illuminating FLS', failed_illum])
    report.append(['Failed Standby FLS', failed_standby])

    df = pd.DataFrame(data=None, columns=['', 'Value'])
    for row in report:
        # if len(df) >= 35:
        #     break
        df.loc[len(df)] = row

    try:
        name = name.replace("_test0", "")
        writer = pd.ExcelWriter(os.path.join(target_file_path, name + '_final_report.xlsx'), engine='openpyxl')

        df.to_excel(writer, sheet_name='Metrics')

        with open(os.path.join(csv_file_path, 'charts.json'), 'r') as json_file:
            function_of_time = json.load(json_file)

        metric_names = ['illuminating']
        for metric_name in metric_names:
            df = pd.DataFrame()
            df['Time'] = function_of_time[metric_name]['t']
            df['Value'] = function_of_time[metric_name]['y']
            df.to_excel(writer, sheet_name=metric_name)

        df = pd.read_csv(os.path.join(csv_file_path, 'config.csv'))
        df.to_excel(writer, sheet_name='Config')
        df = pd.read_csv(os.path.join(csv_file_path, 'dispatcher.csv'))
        df.to_excel(writer, sheet_name='Dispatcher')

        writer.close()
    except Exception as e:
        print(e)


def get_dispatcher_coords(center=None):
    l = 60
    w = 60
    dispatcher_coords = [0,0,0]

    if Config.SANITY_TEST == 1:
        height = min([2, math.sqrt(Config.SANITY_TEST_CONFIG[1][1])])
        radius = math.sqrt(Config.SANITY_TEST_CONFIG[1][1] ** 2 - height ** 2)
        center = [radius + 1, radius + 1, 0]

    elif Config.SANITY_TEST == 2:
        radius = Config.STANDBY_TEST_CONFIG[0][1]
        center = [radius + 1, radius + 1, 0]

    if Config.DISPATCHERS == 1:
        if Config.SANITY_TEST > 0:
            dispatcher_coords = [center]
        else:
            dispatcher_coords = [[l / 2, w / 2, 0]]
    elif Config.DISPATCHERS == 3:
        dispatcher_coords = [[l / 2, w / 2, 0], [l, w, 0], [0, 0, 0]]

    elif Config.DISPATCHERS == 5:
        dispatcher_coords = [[l / 2, w / 2, 0], [l, 0, 0], [0, w, 0], [l, w, 0], [0, 0, 0]]

    return dispatcher_coords


def distance_between(coord1, coord2):
    return ((coord2[0] - coord1[0]) ** 2 + (coord2[1] - coord1[1]) ** 2 + (coord2[2] - coord1[2]) ** 2) ** 0.5


def check_dispatcher(dispatcher_coords, coord):
    # Calculate distances from coord to each coordinate in dispatcher_coords
    distances = [distance_between(c, coord) for c in dispatcher_coords]

    # Find the index of the smallest distance
    min_index = distances.index(min(distances))

    # Return the coordinate from dispatcher_coords that corresponds to the smallest distance
    return dispatcher_coords[min_index]

