import os
import json
import csv
import sys

import numpy as np

from config import Config
from test_config import TestConfig
import pandas as pd
import glob
import re
import utils
from utils import logger

from worker.metrics import merge_timelines, gen_charts, gen_point_metrics, trim_timeline, point_to_id, \
    gen_point_metrics_no_group


def write_json(fid, results, directory, is_clique):
    file_name = f"{fid:05}.c.json" if is_clique else f"{fid:05}.json"
    with open(os.path.join(directory, 'json', file_name), "w") as f:
        json.dump(results, f)


def write_csv(directory, rows, file_name):
    logger.debug(f"WRITE_CSV_FILE {file_name}")
    with open(os.path.join(directory, f'{file_name}.csv'), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)


def create_csv_from_json(config, init_num, directory, fig_dir, group_map):
    if not os.path.exists(directory):
        return

    headers_set = set()
    rows = []
    node_rows = []

    json_dir = os.path.join(directory, 'json')
    filenames = os.listdir(json_dir)
    filenames.sort()

    for filename in filenames:
        if filename.endswith('.json'):
            with open(os.path.join(json_dir, filename)) as f:
                try:
                    data = json.load(f)
                    headers_set = headers_set.union(set(list(data.keys())))
                except json.decoder.JSONDecodeError:
                    print(filename)

    headers = list(headers_set)
    headers.sort()
    rows.append(['fid'] + headers)
    node_rows.append(['fid'] + headers)

    weights = []
    min_dists = []
    avg_dists = []
    max_dists = []
    timelines = []
    for filename in filenames:
        if filename.endswith('.json'):
            with open(os.path.join(json_dir, filename)) as f:
                try:
                    data = json.load(f)
                    fid = filename.split('.')[0]
                    row = [fid] + [data[h] if h in data else 0 for h in headers]
                    node_rows.append(row)
                    timelines.append(data['timeline'])
                except json.decoder.JSONDecodeError:
                    print(filename)

    # with open(os.path.join(directory, 'cliques.csv'), 'w', newline='') as csvfile:
    #     writer = csv.writer(csvfile)
    #     writer.writerows(rows)

    with open(os.path.join(directory, 'flss.csv'), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(node_rows)

    merged_timeline = merge_timelines(timelines)

    num_metrics = [0, 0, 0, 0]
    start_time = 0

    trimed_timeline = merged_timeline
    if config.RESET_AFTER_INITIAL_DEPLOY:
        trimed_timeline, num_metrics, start_time = trim_timeline(merged_timeline, init_num)

    with open(os.path.join(directory, 'timeline.json'), "w") as f:
        json.dump(trimed_timeline, f)

    chart_data = gen_charts(trimed_timeline, start_time, num_metrics, fig_dir)
    with open(os.path.join(directory, 'charts.json'), "w") as f:
        json.dump(chart_data, f)

    point_metrics, standby_metrics = gen_point_metrics(merged_timeline, start_time, group_map)
    write_csv(directory, point_metrics, 'illuminating')
    write_csv(directory, standby_metrics, 'standby')


def write_hds_time(hds, directory, nid):
    if not os.path.exists(directory):
        return

    headers = ['timestamp(s)', 'relative_time(s)', 'hd']
    rows = [headers]

    for i in range(len(hds)):
        row = [hds[i][0], hds[i][0] - hds[0][0], hds[i][1]]
        rows.append(row)

    with open(os.path.join(directory, f'hd-n{nid}.csv'), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)


def write_hds_round(hds, rounds, directory, nid):
    if not os.path.exists(directory):
        return

    headers = ['round', 'time(s)', 'hd']
    rows = [headers]

    for i in range(len(hds)):
        row = [i + 1, rounds[i + 1] - rounds[0], hds[i][1]]
        rows.append(row)

    with open(os.path.join(directory, f'hd-n{nid}.csv'), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)


def write_swarms(swarms, rounds, directory, nid):
    headers = [
        'timestamp(s)',
        'relative times(s)',
        'num_swarms',
        'average_swarm_size',
        'largest_swarm',
        'smallest_swarm',
    ]

    rows = [headers]

    for i in range(len(swarms)):
        t = swarms[i][0] - rounds[0]
        num_swarms = len(swarms[i][1])
        sizes = swarms[i][1].values()

        row = [swarms[i][0], t, num_swarms, sum(sizes) / num_swarms, max(sizes), min(sizes)]
        rows.append(row)

    with open(os.path.join(directory, f'swarms-n{nid}.csv'), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)


def write_configs(directory, date_time):
    headers = ['config', 'value']
    rows = [headers]

    kargs = vars(Config).items()
    if TestConfig.ENABLED:
        kargs = vars(TestConfig).items()

    for k, v in kargs:
        if not k.startswith('__'):
            rows.append([k, v])
    rows.append(["datetime", date_time])

    with open(os.path.join(directory, 'config.csv'), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)


def combine_csvs(directory, xlsx_dir, file_name):
    csv_files = glob.glob(f"{directory}/*.csv")

    with pd.ExcelWriter(os.path.join(xlsx_dir, f'{file_name}.xlsx'), mode='w') as writer:
        for csv_file in csv_files:
            df = pd.read_csv(csv_file)
            sheet_name = csv_file.split('/')[-1][:-4]
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    # shutil.rmtree(os.path.join(directory))


def combine_xlsx(directory):
    xlsx_files = glob.glob(f"{directory}/*.xlsx")

    with pd.ExcelWriter(os.path.join(directory, 'summary.xlsx')) as writer:
        dfs = []
        for file in sorted(xlsx_files):
            print(file)
            df = pd.read_excel(file, sheet_name='metrics')
            m = re.search(r'K:(\d+)_R:(\d+)', file)
            k = m.group(1)
            r = m.group(2)

            df2 = pd.DataFrame([k, r])
            df3 = pd.concat([df2, df.value])
            dfs.append(df3)
        pd.concat([pd.concat([pd.DataFrame(['k', 'r']), df.metric])] + dfs, axis=1).to_excel(writer, index=False)


def read_cliques_xlsx(path):
    df = pd.read_excel(path, sheet_name='cliques')
    return [np.array(eval(c)) for c in df["7 coordinates"]], [max(eval(d)) + 1 for d in df["6 dist between each pair"]]


def get_group_mapping(path):
    group_id = []

    df = pd.read_excel(path, sheet_name='cliques')
    group_map = dict()
    for i, row in enumerate(df["7 coordinates"]):
        for coord in eval(row):
            pid = point_to_id(coord)
            group_map[pid] = i
            if i not in group_id:
                group_id.append(i)

    return group_map, group_id


def delete_previous_json_files(path):
    try:
        # Iterate over all files in the folder
        for root, dirs, files in os.walk(path):
            for file in files:
                path = os.path.join(root, file)
                # Delete the file
                os.remove(path)
        print("All files under the folder have been deleted.")
    except Exception as e:
        print(f"Error occurred: {e}")


def create_csv_from_json_no_group(config, init_num, directory, fig_dir):
    if not os.path.exists(directory):
        return

    headers_set = set()
    rows = []
    node_rows = []

    json_dir = os.path.join(directory, 'json')
    filenames = os.listdir(json_dir)
    filenames.sort()

    for filename in filenames:
        if filename.endswith('.json'):
            with open(os.path.join(json_dir, filename)) as f:
                try:
                    data = json.load(f)
                    headers_set = headers_set.union(set(list(data.keys())))
                except json.decoder.JSONDecodeError:
                    print(filename)

    headers = list(headers_set)
    headers.sort()
    rows.append(['fid'] + headers)
    node_rows.append(['fid'] + headers)

    weights = []
    min_dists = []
    avg_dists = []
    max_dists = []
    timelines = []
    for filename in filenames:
        if filename.endswith('.json'):
            with open(os.path.join(json_dir, filename)) as f:
                try:
                    data = json.load(f)
                    fid = filename.split('.')[0]
                    row = [fid] + [data[h] if h in data else 0 for h in headers]
                    node_rows.append(row)
                    timelines.append(data['timeline'])
                except json.decoder.JSONDecodeError:
                    print(filename)

    # with open(os.path.join(directory, 'cliques.csv'), 'w', newline='') as csvfile:
    #     writer = csv.writer(csvfile)
    #     writer.writerows(rows)

    with open(os.path.join(directory, 'flss.csv'), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(node_rows)

    merged_timeline = merge_timelines(timelines)

    num_metrics = [0, 0, 0, 0]
    start_time = -1

    trimed_timeline = merged_timeline
    if config.RESET_AFTER_INITIAL_DEPLOY:
        trimed_timeline, num_metrics, start_time = trim_timeline(merged_timeline, init_num)

    with open(os.path.join(directory, 'timeline.json'), "w") as f:
        json.dump(trimed_timeline, f)

    chart_data = gen_charts(trimed_timeline, start_time, num_metrics, fig_dir)
    with open(os.path.join(directory, 'charts.json'), "w") as f:
        json.dump(chart_data, f)

    point_metrics, standby_metrics = gen_point_metrics_no_group(merged_timeline, start_time)
    write_csv(directory, point_metrics, 'illuminating')
    write_csv(directory, standby_metrics, 'standby')


def create_csv_from_timeline(directory):
    if not os.path.exists(directory):
        return

    with open(os.path.join(directory, 'timeline.json'), "r") as file:
        timeline = json.load(file)

    point_metrics, standby_metrics = gen_point_metrics_no_group(timeline, 0)
    write_csv(directory, point_metrics, 'illuminating')
    write_csv(directory, standby_metrics, 'standby')


if __name__ == "__main__":
    if len(sys.argv) == 4:
        dir_in = sys.argv[1]
        dir_out = sys.argv[2]
        name = sys.argv[3]
    else:
        dir_in, dir_out, name = "../results/butterfly/H:2/1687746648", "../results/butterfly/H:2", "agg"
    create_csv_from_json(dir_in, 0)
    # combine_csvs(dir_in, dir_out, name)
    # print(f"usage: {sys.argv[0]} <input_dir> <output_dir> <xlsx_file_name>")
    # combine_xlsx("results/1/results/racecar/H:2/20-Jun-08_52_06")
    # combine_xlsx("/Users/hamed/Desktop/165-point_64-core/H:rs_ETA_STR:K-1")
    # combine_xlsx("/Users/hamed/Desktop/165-point_64-core/H:rs_ETA_STR:K")
    # combine_xlsx("/Users/hamed/Desktop/165-point_64-core/H:rs_ETA_STR:1.5K")
