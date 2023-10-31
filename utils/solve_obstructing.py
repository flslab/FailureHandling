import csv
import math
from collections import Counter
from threading import Thread

import numpy as np
import os
import pandas as pd
from matplotlib import pyplot as plt
from tqdm import tqdm
import statistics
import multiprocessing as mp


def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def calculate_travel_time(max_speed, max_acceleration, max_deceleration, distance):
    # Step 1 and 2: Calculate time and distance during acceleration
    t_accel = max_speed / max_acceleration
    d_accel = 0.5 * max_acceleration * t_accel ** 2

    # Step 3 and 4: Calculate time and distance during deceleration
    t_decel = max_speed / max_deceleration
    d_decel = 0.5 * max_deceleration * t_decel ** 2

    # Step 5: Check if the vehicle reaches max speed
    if d_accel + d_decel > distance:
        # If not, find the time using a different approach (not covered here)
        d_accel = d_decel = distance / 2
        t_accel = math.sqrt(d_accel * 2 / max_acceleration)
        t_decel = math.sqrt(d_decel * 2 / max_deceleration)
        return t_accel + t_decel

    # Step 6 and 7: Calculate distance and time at max speed
    d_cruise = distance - (d_accel + d_decel)
    t_cruise = d_cruise / max_speed

    # Step 8: Calculate total time
    t_total = t_accel + t_cruise + t_decel

    return t_total


def get_dist_to_centroid(standbys, shape, k, file_folder, ratio):
    input_file = f"{shape}_G{k}.xlsx"

    groups, a = read_cliques_xlsx(f"{file_folder}/{input_file}", ratio)

    avg_dists = []

    for i, group in enumerate(groups):
        distances = [get_distance(standbys[i], coord) for coord in group]

        avg_dists.append(statistics.mean(distances))

    return avg_dists


def angle_between(origin, point):
    vector = np.array(point) - np.array(origin)
    angle = np.arctan2(vector[1], vector[0])
    return np.degrees(angle)


def read_cliques_xlsx(path, ratio):
    df = pd.read_excel(path, sheet_name='cliques')
    group_list = []

    for c in df["7 coordinates"]:
        coord_list = np.array(eval(c))
        coord_list = coord_list * ratio
        group_list.append(coord_list)

    return group_list, [max(eval(d)) + 1 if eval(d) != [] else 1 for d in df["6 dist between each pair"]]


def read_coordinates(file_path, delimiter):
    coordinates = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Split the line by spaces and convert each part to a float
                coord = [float(x) for x in line.strip().split(delimiter)]
                if len(coord) == 3:  # Ensure that there are exactly 3 coordinates
                    coord.append(0)
                    coordinates.append(coord)
                else:
                    print(f"Invalid coordinate data on line: {line.strip()}")
        return coordinates
    except FileNotFoundError:
        print(f"The file at path {file_path} does not exist.")
        return None
    except Exception as e:
        print(f"An error occurred 5: {e}")
        return None


def get_standby_coords(groups, K):
    group_standby_coord = []

    for i in range(len(groups)):

        group = groups[i]

        if K:
            member_count = group.shape[0]
            sum_x = np.sum(group[:, 0])
            sum_y = np.sum(group[:, 1])
            sum_z = np.sum(group[:, 2])
            stand_by_coord = [
                float(round(sum_x / member_count)),
                float(round(sum_y / member_count)),
                float(round(sum_z / member_count)),
            ]
            group_standby_coord.append(stand_by_coord)

    return group_standby_coord


def get_distance(point1, point2):
    return np.linalg.norm(np.array(point1) - np.array(point2))


# Function to check if a point is inside a cube
def is_inside_cube(point, cube_center, length):
    return all(abs(p - c) < length + 0.00000000001 for p, c in zip(point, cube_center))


def is_disp_cell_overlapping(coord1, coord2):
    return is_inside_cube(coord1, coord2, 1)


def get_points(ratio, pointcloud_folder, output_path, txt_file, standby_file):

    group_standby_coord = read_coordinates(f"{output_path}/points/{standby_file}", ' ')

    points = read_coordinates(f"{pointcloud_folder}/{txt_file}", ' ')

    points = np.array(points)
    points = points * ratio

    point_boundary = [
        [min(points[:, 0]), min(points[:, 1]), min(points[:, 2])],
        [max(points[:, 0]), max(points[:, 1]), max(points[:, 2])]
    ]

    for coord in group_standby_coord:
        coord[3] = 1
        points = np.concatenate((points, [coord]), axis=0)

    return points, point_boundary, np.array(group_standby_coord)[:, 0:3]


def solve_single_view(shape, k, ratio, view, lastview, camera, group_file, output_path):
    tag = f"Solving: {shape}, K: {k}, Ratio: {ratio} ,{view}"
    print(tag)

    txt_file = f"{shape}.txt"
    standby_file = f"{shape}{lastview}_standby.txt"
    points, boundary, standbys = get_points(ratio, group_file, output_path, txt_file, standby_file)
    ori_dists_center = get_dist_to_centroid(standbys, shape, k, group_file, ratio)
    dist_illum = {}
    dist_standby = {}
    dist_between = []

    obstructing = read_coordinates(f"{output_path}/points/{shape}_{view}_blocking.txt", ' ')
    blocked_by = read_coordinates(f"{output_path}/points/{shape}_{view}_blocked.txt", ' ')

    if len(obstructing) == 0:
        metrics = [shape, k, ratio, view, 0, 0, 0,
                   0, 0, 0,
                   0, 0, 0,
                   0, 0, 0,
                   0, 0, 0,
                   0, 0
                   ]

        print(metrics)

    obstructing = np.array(obstructing)[:, 0:3]
    blocked_by = np.array(blocked_by)[:, 0:3]

    obs_list = []
    for coord in obstructing:
        # find_flag = False

        point_ids = np.where(np.all(points[:, 0:3] == coord, axis=1))[0]
        if len(point_ids) == 0:
            print(f"Obstructing Not Found: {coord}, " + tag)
        else:
            obs_list.append(point_ids[0])
        # for index, row in enumerate(points[:, 0:3]):
        # if get_distance(row, coord) < 0.3:
        #     obs_list.append(index)
        #     find_flag = True
        #     break
        # if not find_flag:
        #     print(f"Obstructing Not Found: {coord}, " + tag)

    standby_list = []
    for coord in obstructing:
        point_ids = np.where(np.all(standbys[:, 0:3] == coord, axis=1))[0][0]
        # if len(point_ids) == 0:
        #     print(f"Standby Not Found: {coord}, " + tag)
        # else:
        standby_list.append(point_ids)

    blocked_list = []
    multiple_blocking = {}
    for blocked_index, coord in enumerate(blocked_by):

        point_ids = np.where(np.all(points[:, 0:3] == coord, axis=1))[0][0]
        # if len(point_ids) == 0:
        #     print(f"Blocked Not Found: {coord}, " + tag)
        # else:
        blocked_list.append(point_ids)
        if point_ids in multiple_blocking.keys():
            if standby_list[blocked_index] not in multiple_blocking[point_ids]:
                multiple_blocking[point_ids].append(standby_list[blocked_index])
                # if len(multiple_blocking[point_ids]) == 4:
                #     for pid in multiple_blocking[point_ids]:
                #         print(standbys[pid][0:3])
        else:
            multiple_blocking[point_ids] = [standby_list[blocked_index]]

    obstruct_pairs = dict()

    # Match obstructing FLSs with only one illuminating FLS, they just needs to move once
    for uni_index in set(standby_list):
        blocked_list_indexes = np.where(standby_list == uni_index)[0]
        pair_index = None
        min_dist = float('inf')
        blocked_index_list = []
        for blocked_list_index in blocked_list_indexes:
            blocked_index_list.append(blocked_list[blocked_list_index])

        for blocked_index in set(blocked_index_list):
            dist_between.append(get_distance(standbys[uni_index][0:3], points[blocked_index][0:3]))
            dist = get_distance(camera, points[blocked_index][0:3])
            if dist < min_dist:
                min_dist = dist
                pair_index = blocked_index
            obstruct_pairs[blocked_list_indexes[0]] = pair_index

    multi_obst = []
    for blocking_list in list(multiple_blocking.values()):
        multi_obst.append(len(blocking_list))

    step_length = 0.5

    for key in obstruct_pairs.keys():
        dist_standby[standby_list[key]] = 0
        dist_illum[obstruct_pairs[key]] = 0

    for key in obstruct_pairs.keys():
        obstructing_index = key
        standby_index = standby_list[obstructing_index]
        illum_index = obstruct_pairs[key]

        illum_coord = points[illum_index][0:3]

        gaze_vec = normalize(np.array(illum_coord) - camera)
        new_pos = illum_coord + gaze_vec

        check_times = 1
        while not all([not is_disp_cell_overlapping(new_pos, p) for p in points]):
            new_pos += gaze_vec * step_length
            check_times += 1

        dist_standby[standby_index] += get_distance(illum_coord, obstructing[obstructing_index])
        dist_illum[illum_index] += get_distance(illum_coord, new_pos)

        points[obs_list[obstructing_index], 0:3] = new_pos
        standbys[standby_list[obstructing_index]] = new_pos

    np.savetxt(f'{output_path}/points/{shape}_{view}_standby.txt', standbys, fmt='%f', delimiter=' ')

    dists_center = get_dist_to_centroid(standbys, shape, k, group_file, ratio)

    max_speed = max_acceleration = max_deceleration = 6.11

    dist_illum_list = list(dist_illum.values())
    dist_standby_list = list(dist_standby.values())

    metrics = [shape, k, ratio, view,
               min(dist_illum_list), max(dist_illum_list), statistics.mean(dist_illum_list),
               min(dist_standby_list), max(dist_standby_list), statistics.mean(dist_standby_list),
               len(obstruct_pairs.values()),
               min(dist_between), max(dist_between), statistics.mean(dist_between),
               min(multi_obst), max(multi_obst), statistics.mean(multi_obst),
               min(ori_dists_center), max(ori_dists_center), statistics.mean(ori_dists_center),
               calculate_travel_time(max_speed, max_acceleration, max_deceleration, statistics.mean(ori_dists_center)),
               min(dists_center), max(dists_center), statistics.mean(dists_center),
               calculate_travel_time(max_speed, max_acceleration, max_deceleration, statistics.mean(dists_center)),
               (statistics.mean(dists_center) / statistics.mean(ori_dists_center)) - 1,
               (calculate_travel_time(max_speed, max_acceleration, max_deceleration,
                                      statistics.mean(dists_center)) / calculate_travel_time(max_speed,
                                                                                             max_acceleration,
                                                                                             max_deceleration,
                                                                                             statistics.mean(
                                                                                                 ori_dists_center))) - 1,
               multi_obst
               ]

    return metrics


def solve_obstructing(group_file, meta_direc, ratio):
    title = [
        "Shape", "K", "Ratio", "View",
        "Min Dist Illum", "Max Dist Illum", "Avg Dist Illum",
        "Min Dist Standby", "Max Dist Standby", "Avg Dist Standby",
        "Moved Illuminating FLSs",
        "Min Dist Between", "Max Dist Between", "Avg Dist Between",
        "Min Obstructing FLSs", "Max Obstructing FLSs", "Avg Obstructing FLSs",
        "Min Ori Dist To Center", "Max Ori Dist To Center", "Avg Ori Dist To Center", "Origin MTID",
        "Min Dist To Center", "Max Dist To Center", "Avg Dist To Center", "MTID",
        "Dist To Center Change", "MTID Change", "Obstructing Nums"]
    result = [title]

    for k in [3, 20]:
        report_path = f"{meta_direc}/obstructing/R{ratio}"

        output_path = f"{meta_direc}/obstructing/R{ratio}/K{k}"

        for shape in ["skateboard", "hat", "dragon"]:
            # for shape in ["skateboard", "dragon"]:

            txt_file = f"{shape}.txt"
            standby_file = f"{shape}_standby.txt"
            points, boundary, standbys = get_points(ratio, group_file, output_path, txt_file, standby_file)

            ori_dists_center = get_dist_to_centroid(standbys, shape, k, group_file, ratio)
            # print(ori_dists_center)

            cam_positions = [
                # top
                [boundary[0][0] / 2 + boundary[1][0] / 2, boundary[0][1] / 2 + boundary[1][1] / 2,
                 boundary[1][2] + 100],
                # down
                [boundary[0][0] / 2 + boundary[1][0] / 2, boundary[0][1] / 2 + boundary[1][1] / 2,
                 boundary[0][2] - 100],
                # left
                [boundary[0][0] - 100, boundary[0][1] / 2 + boundary[1][1] / 2,
                 boundary[0][0] / 2 + boundary[1][0] / 2],
                # right
                [boundary[1][0] + 100, boundary[0][1] / 2 + boundary[1][1] / 2,
                 boundary[0][0] / 2 + boundary[1][0] / 2],
                # front
                [boundary[0][0] / 2 + boundary[1][0] / 2, boundary[0][1] - 100,
                 boundary[0][0] / 2 + boundary[1][0] / 2],
                # back
                [boundary[0][0] / 2 + boundary[1][0] / 2, boundary[1][1] + 100,
                 boundary[0][0] / 2 + boundary[1][0] / 2]
            ]

            views = ["top", "bottom", "left", "right", "front", "back"]

            # np.savetxt(f'{output_path}/points/{shape}_standby_solve.txt', standbys, fmt='%f', delimiter=' ')

            for i in range(len(views)):
                # if i != 3:
                #     continue

                tag = f"Solving: {shape}, K: {k}, Ratio: {ratio} ,{views[i]}"
                print(tag)

                dist_illum = {}
                dist_standby = {}
                dist_between = []

                camera = np.array(cam_positions[i])

                obstructing = read_coordinates(f"{output_path}/points/{shape}_{views[i]}_blocking.txt", ' ')
                blocked_by = read_coordinates(f"{output_path}/points/{shape}_{views[i]}_blocked.txt", ' ')

                if len(obstructing) == 0:
                    metrics = [shape, k, ratio, views[i], 0, 0, 0,
                               0, 0, 0,
                               0, 0, 0,
                               0, 0, 0,
                               0, 0, 0,
                               0, 0
                               ]

                    result.append(metrics)
                    print(metrics)
                    continue

                obstructing = np.array(obstructing)[:, 0:3]
                blocked_by = np.array(blocked_by)[:, 0:3]

                obs_list = []
                for coord in obstructing:
                    # find_flag = False

                    point_ids = np.where(np.all(points[:, 0:3] == coord, axis=1))[0]
                    if len(point_ids) == 0:
                        print(f"Obstructing Not Found: {coord}, " + tag)
                    else:
                        obs_list.append(point_ids[0])
                    # for index, row in enumerate(points[:, 0:3]):
                    # if get_distance(row, coord) < 0.3:
                    #     obs_list.append(index)
                    #     find_flag = True
                    #     break
                    # if not find_flag:
                    #     print(f"Obstructing Not Found: {coord}, " + tag)

                standby_list = []
                for coord in obstructing:
                    point_ids = np.where(np.all(standbys[:, 0:3] == coord, axis=1))[0][0]
                    # if len(point_ids) == 0:
                    #     print(f"Standby Not Found: {coord}, " + tag)
                    # else:
                    standby_list.append(point_ids)

                blocked_list = []
                multiple_blocking = {}
                for blocked_index, coord in enumerate(blocked_by):

                    point_ids = np.where(np.all(points[:, 0:3] == coord, axis=1))[0][0]
                    # if len(point_ids) == 0:
                    #     print(f"Blocked Not Found: {coord}, " + tag)
                    # else:
                    blocked_list.append(point_ids)
                    if point_ids in multiple_blocking.keys():
                        if standby_list[blocked_index] not in multiple_blocking[point_ids]:
                            multiple_blocking[point_ids].append(standby_list[blocked_index])
                            # if len(multiple_blocking[point_ids]) == 4:
                            #     for pid in multiple_blocking[point_ids]:
                            #         print(standbys[pid][0:3])
                    else:
                        multiple_blocking[point_ids] = [standby_list[blocked_index]]

                obstruct_pairs = dict()

                # Match obstructing FLSs with only one illuminating FLS, they just needs to move once
                for uni_index in set(standby_list):
                    blocked_list_indexes = np.where(standby_list == uni_index)[0]
                    pair_index = None
                    min_dist = float('inf')
                    blocked_index_list = []
                    for blocked_list_index in blocked_list_indexes:
                        blocked_index_list.append(blocked_list[blocked_list_index])

                    for blocked_index in set(blocked_index_list):
                        dist_between.append(get_distance(standbys[uni_index][0:3], points[blocked_index][0:3]))
                        dist = get_distance(camera, points[blocked_index][0:3])
                        if dist < min_dist:
                            min_dist = dist
                            pair_index = blocked_index
                        obstruct_pairs[blocked_list_indexes[0]] = pair_index

                multi_obst = []
                for blocking_list in list(multiple_blocking.values()):
                    multi_obst.append(len(blocking_list))

                step_length = 0.5

                for key in obstruct_pairs.keys():
                    dist_standby[standby_list[key]] = 0
                    dist_illum[obstruct_pairs[key]] = 0

                for key in obstruct_pairs.keys():
                    obstructing_index = key
                    standby_index = standby_list[obstructing_index]
                    illum_index = obstruct_pairs[key]

                    illum_coord = points[illum_index][0:3]

                    gaze_vec = normalize(np.array(illum_coord) - camera)
                    new_pos = illum_coord + gaze_vec

                    check_times = 1
                    while not all([not is_disp_cell_overlapping(new_pos, p) for p in points]):
                        new_pos += gaze_vec * step_length
                        check_times += 1

                    dist_standby[standby_index] += get_distance(illum_coord, obstructing[obstructing_index])
                    dist_illum[illum_index] += get_distance(illum_coord, new_pos)

                    points[obs_list[obstructing_index], 0:3] = new_pos
                    standbys[standby_list[obstructing_index]] = new_pos

                dists_center = get_dist_to_centroid(standbys, shape, k, group_file, ratio)

                max_speed = max_acceleration = max_deceleration = 6.11

                dist_illum_list = list(dist_illum.values())
                dist_standby_list = list(dist_standby.values())

                metrics = [shape, k, ratio, views[i],
                           min(dist_illum_list), max(dist_illum_list), statistics.mean(dist_illum_list),
                           min(dist_standby_list), max(dist_standby_list), statistics.mean(dist_standby_list),
                           len(obstruct_pairs.values()),
                           min(dist_between), max(dist_between), statistics.mean(dist_between),
                           min(multi_obst), max(multi_obst), statistics.mean(multi_obst),
                           min(ori_dists_center), max(ori_dists_center), statistics.mean(ori_dists_center),
                           calculate_travel_time(max_speed, max_acceleration, max_deceleration,
                                                 statistics.mean(ori_dists_center)),
                           min(dists_center), max(dists_center), statistics.mean(dists_center),
                           calculate_travel_time(max_speed, max_acceleration, max_deceleration,
                                                 statistics.mean(dists_center)),
                           (statistics.mean(dists_center) / statistics.mean(ori_dists_center)) - 1,
                           (calculate_travel_time(max_speed, max_acceleration, max_deceleration,
                                                  statistics.mean(dists_center)) / calculate_travel_time(max_speed,
                                                                                                         max_acceleration,
                                                                                                         max_deceleration,
                                                                                                         statistics.mean(
                                                                                                             ori_dists_center))) - 1,
                           multi_obst
                           ]

                result.append(metrics)
                print(list(zip(title, metrics)))
    with open(f'{report_path}/solve_R{ratio}.csv', mode='w', newline='') as file:
        writer = csv.writer(file)

        # Write the data from the list to the CSV file
        for row in result:
            writer.writerow(row)


if __name__ == "__main__":

    # file_folder = "C:/Users/zhusq/Desktop"
    # meta_dir = "C:/Users/zhusq/Desktop"
    file_folder = "/Users/shuqinzhu/Desktop/pointcloud"
    meta_dir = "/Users/shuqinzhu/Desktop"

    # file_folder = "/users/Shuqin/pointcloud"
    # meta_dir = "/users/Shuqin"

    p_list = []
    for illum_to_disp_ratio in [1, 3, 5, 10]:
        solve_obstructing(file_folder, meta_dir, illum_to_disp_ratio)
    #     p_list.append(mp.Process(target=calculate_obstructing, args=(file_folder, meta_dir, illum_to_disp_ratio)))
    #
    # for p in p_list:
    #     # print(t)
    #     p.start()
