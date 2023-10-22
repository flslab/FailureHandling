import csv
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


def get_dist_to_centroid(standbys, shape, k, file_folder, ratio):
    input_file = f"{shape}_G{k}.xlsx"

    groups, a = read_cliques_xlsx(f"{file_folder}/pointcloud/{input_file}", ratio)

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
        # coord_list[:, 2] += 100
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
def is_inside_cube(point, cube_center, distance):
    return all(abs(p - c) < distance + 0.00000000001 for p, c in zip(point, cube_center))


def is_in_disp_cell(coord1, coord2):
    return is_inside_cube(coord1, coord2, 1)


def is_in_illum_cell(coord1, coord2, ratio):
    return is_inside_cube(coord1, coord2, 1 * ratio)


def get_points(shape, K, file_folder, ratio):
    input_file = f"{shape}_G{K}.xlsx"

    txt_file = f"{shape}.txt"

    groups, a = read_cliques_xlsx(f"{file_folder}/pointcloud/{input_file}", ratio)

    group_standby_coord = get_standby_coords(groups, K)

    points = read_coordinates(f"{file_folder}/pointcloud/{txt_file}", ' ')

    points = np.array(points)
    points = points * ratio

    point_boundary = [
        [min(points[:, 0]), min(points[:, 1]), min(points[:, 2])],
        [max(points[:, 0]), max(points[:, 1]), max(points[:, 2])]
    ]

    center = np.array([
        (min(points[:, 0]) + max(points[:, 0])) / 2,
        (min(points[:, 1]) + max(points[:, 1])) / 2,
        (min(points[:, 2]) + max(points[:, 2])) / 2
    ])

    for group_id, coord in enumerate(group_standby_coord):
        coords = points[:, :3]

        coords = coords.tolist()

        check = 0

        if not all([not is_in_disp_cell(coord, c) for c in coords]):

            overlap = True
            rims_check = 1

            while overlap:
                directions = []
                for x in range(-rims_check, rims_check + 1, 1):
                    for y in range(-rims_check, rims_check + 1, 1):
                        for z in range(-rims_check, rims_check + 1, 1):
                            if x == 0 and y == 0 and z == 0:
                                continue
                            directions.append([x, y, z])

                directions = sorted(directions, key=lambda d: get_distance(d, center))
                directions = np.array(directions)

                for dirc in directions:
                    new_coord = coord + dirc * 0.5
                    check += 1
                    if all([not is_in_disp_cell(new_coord, c) for c in coords]):
                        overlap = False
                        coord = new_coord.tolist()
                        break

                if overlap:
                    if rims_check % 10 == 0:
                        print(f"Rim: {rims_check}")
                    rims_check += 1
                # break

        group_standby_coord[group_id] = coord[:]
        coord.append(1)
        points = np.concatenate((points, [coord]), axis=0)

    return points, point_boundary, np.array(group_standby_coord)


def calculate_obstructing(group_file, meta_direc, ratio):
    title = [
        "Shape", "K", "Ratio", "View", "Dist Illum", "Dist Standby", "Obstruction Times",
        "Min Dist Between", "Max Dist Between", "Mean Dist Between",
        "Min Obstructing FLSs", "Max Obstructing FLSs", "Mean Obstructing FLSs",
        "Min Ori Dist To Center", "Max Ori Dist To Center", "Mean Ori Dist To Center",
        "Min Dist To Center", "Max Dist To Center", "Mean Dist To Center",
        "Dist To Center Change", "Obstructing Nums"]
    result = [title]

    for k in [3, 20]:
        report_path = f"{meta_direc}/obstructing/R{ratio}"

        output_path = f"{meta_direc}/obstructing/R{ratio}/K{k}"

        for shape in ["skateboard", "hat", "dragon"]:
            # for shape in ["skateboard", "dragon"]:
            points, boundary, standbys = get_points(shape, k, group_file, ratio)

            ori_dists_center = get_dist_to_centroid(standbys, shape, k, group_file, ratio)

            cam_positions = [
                # top
                [boundary[0][0] / 2 + boundary[1][0] / 2, boundary[0][1] / 2 + boundary[1][1] / 2,
                 boundary[1][2] + 100 * ratio],
                # down
                [boundary[0][0] / 2 + boundary[1][0] / 2, boundary[0][1] / 2 + boundary[1][1] / 2,
                 boundary[0][2] - 100 * ratio],
                # left
                [boundary[0][0] - 100 * ratio, boundary[0][1] / 2 + boundary[1][1] / 2,
                 boundary[0][0] / 2 + boundary[1][0] / 2],
                # right
                [boundary[1][0] + 100 * ratio, boundary[0][1] / 2 + boundary[1][1] / 2,
                 boundary[0][0] / 2 + boundary[1][0] / 2],
                # front
                [boundary[0][0] / 2 + boundary[1][0] / 2, boundary[0][1] - 100 * ratio,
                 boundary[0][0] / 2 + boundary[1][0] / 2],
                # back
                [boundary[0][0] / 2 + boundary[1][0] / 2, boundary[1][1] + 100 * ratio,
                 boundary[0][0] / 2 + boundary[1][0] / 2]
            ]

            views = ["top", "bottom", "left", "right", "front", "back"]

            for i in range(len(views)):
                tag = f"Solving: {shape}, K: {k}, Ration: {ratio} ,{views[i]}"

                print(tag)

                dist_illum = 0
                dist_standby = 0
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
                    break

                obstructing = np.array(obstructing)[:, 0:3]
                blocked_by = np.array(blocked_by)[:, 0:3]

                obs_list = []
                for coord in obstructing:
                    find_flag = False
                    for index, row in enumerate(points[:, 0:3]):
                        if get_distance(row, coord) < 0.3:
                            obs_list.append(index)
                            find_flag = True
                            break
                    if not find_flag:
                        print(f"Obstructing Not Found: {coord}, " + tag)

                standby_list = []
                for coord in obstructing:
                    find_flag = False
                    for index, row in enumerate(standbys[:, 0:3]):
                        if get_distance(row, coord) < 0.1:
                            standby_list.append(index)
                            find_flag = True
                            break
                    if not find_flag:
                        print(f"Standby Not Found: {coord}, " + tag)

                blocked_list = []
                for coord in blocked_by:
                    find_flag = False
                    for index, row in enumerate(points[:, 0:3]):
                        if get_distance(row, coord) < 0.1:
                            blocked_list.append(index)
                            find_flag = True
                            break
                    if not find_flag:
                        print(f"Blocked Not Found: {coord}, " + tag)

                multi_obst = Counter(blocked_list)

                step_length = 0.5
                for index, coord in enumerate(blocked_by):
                    gaze_vec = normalize(np.array(coord) - camera)
                    new_pos = coord + gaze_vec

                    check_times = 1
                    while not all([not is_in_disp_cell(new_pos, p) for p in points]):
                        new_pos += gaze_vec * step_length
                        check_times += 1

                    dist_standby += get_distance(coord, obstructing[index])
                    dist_illum += get_distance(coord, new_pos)

                    dist_between.append(get_distance(coord, obstructing[index]))

                    points[obs_list[index], 0:3] = new_pos
                    standbys[standby_list[index]] = new_pos

                dists_center = get_dist_to_centroid(standbys, shape, k, group_file, ratio)

                metrics = [shape, k, ratio, views[i], dist_illum, dist_standby, len(multi_obst.keys()),
                           min(dist_between), max(dist_between), statistics.mean(dist_between),
                           min(multi_obst.values()), max(multi_obst.values()), statistics.mean(multi_obst.values()),
                           min(ori_dists_center), max(ori_dists_center), statistics.mean(ori_dists_center),
                           min(dists_center), max(dists_center), statistics.mean(dists_center),
                           (statistics.mean(dists_center) / statistics.mean(ori_dists_center)) - 1, multi_obst.items()
                           ]

                result.append(metrics)
                print(list(zip(title, metrics)))
    with open(f'{report_path}/solve_R{ratio}_K{k}.csv', mode='w', newline='') as file:
        writer = csv.writer(file)

        # Write the data from the list to the CSV file
        for row in result:
            writer.writerow(row)


if __name__ == "__main__":

    # file_folder = "C:/Users/zhusq/Desktop"
    # meta_dir = "C:/Users/zhusq/Desktop"
    # file_folder = "/Users/shuqinzhu/Desktop"
    # meta_dir = "/Users/shuqinzhu/Desktop"

    file_folder = "/users/Shuqin"
    meta_dir = "/users/Shuqin"

    p_list = []
    for illum_to_disp_ratio in [1, 3, 5, 10]:
        # calculate_obstructing(file_folder, meta_dir, illum_to_disp_ratio)
        p_list.append(mp.Process(target=calculate_obstructing, args=(file_folder, meta_dir, illum_to_disp_ratio)))

    for p in p_list:
        # print(t)
        p.start()
