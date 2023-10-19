import csv
from threading import Thread

import numpy as np
import os
import pandas as pd
from matplotlib import pyplot as plt
from tqdm import tqdm
import statistics
import multiprocessing as mp


def angle_between(origin, point):
    vector = np.array(point) - np.array(origin)
    angle = np.arctan2(vector[1], vector[0])
    return np.degrees(angle)


def read_cliques_xlsx(path):
    df = pd.read_excel(path, sheet_name='cliques')
    group_list = []

    for c in df["7 coordinates"]:
        coord_list = np.array(eval(c))
        # coord_list[:, 2] += 100
        group_list.append(coord_list)

    return group_list, [max(eval(d)) + 1 if eval(d) != [] else 1 for d in df["6 dist between each pair"]]


def read_coordinates(file_path):
    coordinates = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Split the line by spaces and convert each part to a float
                coord = [float(x) for x in line.strip().split(' ')]
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


# Function to find visible cubes
def visible_cubes(camera, cubes, ratio):
    # Calculate distances from the camera to each cube
    distances = [get_distance(camera, cube[:3]) for cube in cubes]

    max_dist = max(distances)

    # Sort cubes by distance
    sorted_indices = np.argsort(distances)

    visible = []
    blocking = []
    visible_index = []
    blocking_index = []
    blocked_by = []

    for index_i in tqdm(range(0, len(sorted_indices))):
        i = sorted_indices[index_i]

        cube = cubes[i]

        is_visible = True

        t_values = np.linspace(0, 1,
                               round(get_distance(camera, cube[:3]) / 0.1))  # Adjust the number of points as needed
        line_points = np.outer((1 - t_values), camera) + np.outer(t_values, cube[:3])

        # Check if the line of sight to the cube is obstructed
        for index_j, j in enumerate(sorted_indices):
            if index_j >= index_i:
                break

            if cubes[j][3] != 1 and any(
                    is_in_illum_cell(p, cubes[j][0:3], ratio) for p in line_points):
                is_visible = False
                break

        if is_visible:
            visible_index.append(i)
            visible.append(cube)

        if cube[3] == 1 and is_visible:

            V = cube[:3] - camera
            V = V / np.linalg.norm(V)

            t_values = np.linspace(0, max_dist - get_distance(camera, cube[:3]),
                                   round((max_dist - get_distance(camera, cube[:3])) / 0.1))

            line_points = []

            for t in t_values:
                line_points.append(V * t + cube[:3])

            line_points = np.array(line_points)

            for index_j, j in enumerate(sorted_indices):
                if index_j <= index_i or cubes[j][3] == 1:
                    continue

                if any(is_in_illum_cell(p, cubes[j][0:3], ratio) for p in line_points):

                    blocked_by.append(cubes[j][0:3])

                    if i not in blocking_index:
                        blocking.append(cube[0:3])
                        blocking_index.append(i)
                    break

    return visible, blocking, blocked_by, blocking_index


def check_blocking_nums(shape, K, file_fopointclder):
    input_file = f"{shape}_G{K}.xlsx"

    txt_file = f"{shape}.txt"

    groups, a = read_cliques_xlsx(f"{file_folder}/pointcloud/{input_file}")

    group_standby_coord = get_standby_coords(groups, K)

    points = read_coordinates(f"{file_folder}/pointcloud/{txt_file}")

    points = np.array(points)

    point_boundary = [
        [min(points[:, 0]), min(points[:, 1]), min(points[:, 2])],
        [max(points[:, 0]), max(points[:, 1]), max(points[:, 2])]
    ]

    center = np.array([
        (min(points[:, 0]) + max(points[:, 0])) / 2,
        (min(points[:, 1]) + max(points[:, 1])) / 2,
        (min(points[:, 2]) + max(points[:, 2])) / 2
    ])

    check_times = []

    for coord in group_standby_coord:

        coords = points[:, :3]

        coords = coords.tolist()

        check = 0
        a = [not is_in_disp_cell(coord, c) for c in coords]
        if not all(a):

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
        check_times.append(check)

        coord.append(1)
        points = np.concatenate((points, [coord]), axis=0)
    return points, point_boundary, check_times


def calculate_obstructing(group_file, meta_direc, ratio, K):
    result = [
        ["Shape", "K", "Ratio", "View", "Visible_Illum", "Obstructing FLS", "Min Times Checked", "Mean Times Checked",
         "Max Times Checked"]]
    report_path = f"{meta_direc}/obstructing/R{ratio}"

    output_path = f"{meta_direc}/obstructing/R{ratio}/K{K}"

    for shape in ["skateboard", "hat", "dragon"]:
        # for shape in ["skateboard", "dragon"]:
        points, boundary, check_times = check_blocking_nums(shape, K, group_file)

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

        illum = []
        standby = []
        for coord in points:
            if coord[3] == 0:
                illum.append(coord[:3])
            else:
                standby.append(coord[:3])

        illum = np.array(illum)
        standby = np.array(standby)

        np.savetxt(f'{output_path}/points/{shape}_illum.txt', illum, fmt='%d', delimiter='\t')
        np.savetxt(f'{output_path}/points/{shape}_standby.txt', standby, fmt='%d', delimiter='\t')

        for i in range(len(views)):

            print(f"{shape}, K: {K}, Ration: {ratio} ,{views[i]}")

            camera = cam_positions[i]

            visible, blocking, blocked_by, blocking_index = visible_cubes(camera, points, ratio)
            # count_0 = visible[:, 3].count(0)
            # count_1 = visible[:, 3].count(1)

            visible_illum = []
            visible_standby = []
            for point in visible:
                if point[3] == 1:
                    visible_standby.append(point[0:3])
                else:
                    visible_illum.append(point[0:3])

            visible_illum = np.array(visible_illum)
            np.unique(visible_illum, axis=0)

            visible_standby = np.array(visible_standby)
            np.unique(visible_standby, axis=0)

            blocking = np.array(blocking)
            np.unique(blocking, axis=0)

            blocked_by = np.array(blocked_by)
            np.unique(blocked_by, axis=0)

            np.savetxt(f'{output_path}/points/{shape}_{views[i]}_visible_illum.txt', visible_illum, fmt='%d',
                       delimiter='\t')
            np.savetxt(f'{output_path}/points/{shape}_{views[i]}_visible_standby.txt', visible_standby,
                       fmt='%d',
                       delimiter='\t')
            np.savetxt(f'{output_path}/points/{shape}_{views[i]}_blocking_1.txt', blocking, fmt='%d',
                       delimiter='\t')
            np.savetxt(f'{output_path}/points/{shape}_{views[i]}_blocked_1.txt', blocked_by, fmt='%d',
                       delimiter='\t')

            print(
                f"{shape}, K: {K}, Ratio: {ratio} ,{views[i]} view: Number of Illuminating FLS: {len(visible_illum)}, Visible Standby FLS: {len(visible_standby)},  Obstructing Number: {len(blocking_index)}")

            result.append(
                [shape, K, ratio, views[i], len(visible_illum), len(blocking_index), min(check_times),
                 statistics.mean(check_times), max(check_times)])

    with open(f'{report_path}/report_R{ratio}_K{K}.csv', mode='w', newline='') as file:
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

        for k_value in [3, 20]:
            # calculate_obstructing(file_folder, meta_dir, illum_to_disp_ratio, K)
            p_list.append(mp.Process(target=calculate_obstructing, args=(file_folder, meta_dir, illum_to_disp_ratio, k_value)))
    #
    for p in p_list:
        # print(t)
        p.start()