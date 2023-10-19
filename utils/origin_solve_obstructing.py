import numpy as np
import os
import statistics
import pandas as pd
import csv

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

def distance_between(point1, point2):
    return np.linalg.norm(np.array(point1) - np.array(point2))


# Function to check if a point is inside a cube
def is_inside_cube(point, cube_center, distance):
    return all(abs(p - c) <= distance for p, c in zip(point, cube_center))


def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


# Function to find visible cubes
def visible_cubes(camera, cubes):
    # Calculate distances from the camera to each cube
    distances = [distance_between(camera, cube[:3]) for cube in cubes]

    # Sort cubes by distance
    sorted_indices = np.argsort(distances)

    index = 0
    distance_stb = 0
    distance_ill = 0
    standby_block = []

    dist_between = []
    visible_list = []

    while index < len(sorted_indices):

        i = sorted_indices[index]
        obstruct_list = []
        is_visible = True

        # Check if the line of sight to the cube is obstructed
        for j in sorted_indices:
            if j == i:
                break

            # Check if any point on the line segment is inside the obstructing cube
            t_values = np.linspace(0, 1, 100)  # Adjust the number of points as needed
            line_points = np.outer((1 - t_values), camera) + np.outer(t_values, cubes[i][:3])
            if any(is_inside_cube(point, cubes[j][0:3], 0.5) for point in line_points):
                if cubes[i][3] != 1 and any(is_inside_cube(point, cubes[j][0:3], 0.5) for point in line_points):
                    # if cubes[j][3] != 1:
                    #     obstruct_list = []
                    #     break

                    if cubes[j][3] == 1 and j in visible_list and j not in obstruct_list:
                        obstruct_list.append(j)

                is_visible = False

        if is_visible:
            visible_list.append(i)


        move_back_times = 0
        for index_ob, j in enumerate(obstruct_list):

            if index_ob == 0:
               dist_between.append(np.linalg.norm(cubes[i][0:3] - cubes[j][0:3]))

            distance_stb = distance_stb + np.linalg.norm(cubes[i][0:3] - cubes[j][0:3])

            # print(f"D_stb: {np.linalg.norm(cubes[i][0:3] - cubes[j][0:3])}")

            cubes[j] = cubes[i]

            V = cubes[i][0:3] - camera
            V = normalize(V)

            new_pos = V + cubes[i][0:3]

            while not all([not is_inside_cube(new_pos, cube, 1) for cube in cubes[:, 0:3]]):
                new_pos = new_pos + V * 1/2
                move_back_times += 1

                # print(f"D_ill in step: {np.linalg.norm(cubes[i][0:3] - new_pos)}")

            # print(f"D_ill: {np.linalg.norm(cubes[i][0:3] - new_pos)}")
            distance_ill = distance_ill + np.linalg.norm(cubes[i][0:3] - new_pos)

            cubes[i][0:3] = V + cubes[i][0:3]
            cubes[i][3] = 1

        distances = [distance_between(camera, cube[:3]) for cube in cubes]

        sorted_indices = np.argsort(distances)


        if len(obstruct_list) > 0:
            standby_block.append(len(obstruct_list))

            index -= len(obstruct_list) + 1
            print(f"Illum: {i}, Standby:{obstruct_list}")
            # print(f"move_back_times: {move_back_times}")
            # print(f"    - block: {len(obstruct_list)}")

        index += 1

    return distance_ill, distance_stb, dist_between, standby_block, cubes


def check_blocking_nums(shape):
    input_file = f"{shape}_G{K}.xlsx"

    txt_file = f"{shape}.txt"

    illums = read_coordinates(f"{file_folder}/pointcloud/{txt_file}")

    illums = np.array(illums)
    illums = np.c_[illums, np.zeros(illums.shape[0])]

    point_boundary = [
        [min(illums[:, 0]), min(illums[:, 1]), min(illums[:, 2])],
        [max(illums[:, 0]), max(illums[:, 1]), max(illums[:, 2])]
    ]

    standbys = read_coordinates(f"{file_folder}/pointcloud/{txt_file}")

    standbys = np.array(standbys)
    standbys = np.c_[standbys, np.zeros(standbys.shape[0])]

    points = np.concatenate((illums, standbys), axis=0)

    return points, point_boundary


if __name__ == "__main__":

    # shape = "skateboard"

    file_folder = "/Users/shuqinzhu/Desktop"

    result = [["Shape", "View", "D_Illum", "D_Stb", "Min D_between", "Max D_between", "Avg D_between",
              "Occur Times", "Min Stb Block", "Max Stb Block", "Avg Stb Block"]]

    for K in [20, 3]:

        output_path = f"/Users/shuqinzhu/Desktop/obstructing/R{1}/K{K}"

        for shape in ["skateboard", "hat", "dragon"]:
            points, boundary = check_blocking_nums(shape)

            cam_positions = [
                # top
                [boundary[0][0] / 2 + boundary[1][0] / 2, boundary[0][1] / 2 + boundary[1][1] / 2, boundary[1][2] + 100],
                # down
                [boundary[0][0] / 2 + boundary[1][0] / 2, boundary[0][1] / 2 + boundary[1][1] / 2, boundary[0][2] - 100],
                # left
                [boundary[0][0] - 100, boundary[0][1] / 2 + boundary[1][1] / 2, boundary[0][0] / 2 + boundary[1][0] / 2],
                # right
                [boundary[1][0] + 100, boundary[0][1] / 2 + boundary[1][1] / 2, boundary[0][0] / 2 + boundary[1][0] / 2],
                # front
                [boundary[0][0] / 2 + boundary[1][0] / 2, boundary[0][1] - 100, boundary[0][0] / 2 + boundary[1][0] / 2],
                # back
                [boundary[0][0] / 2 + boundary[1][0] / 2, boundary[1][1] + 100, boundary[0][0] / 2 + boundary[1][0] / 2]
            ]

            views = ["top", "bottom", "left", "right", "front", "back"]

            for i, in views:

                camera = cam_positions[i]

                distance_ill, distance_stb, dist_between, standby_block, adjusted_points = visible_cubes(camera, points)

                illum = []
                standby = []
                for coord in adjusted_points:
                    if coord[3] == 0:
                        illum.append(coord[:3])
                    else:
                        standby.append(coord[:3])

                illum = np.array(illum)
                standby = np.array(standby)

                np.savetxt(f'{output_path}/points/{shape}_origin_adj_{views[i]}_ill.txt', illum, fmt='%d', delimiter='\t')
                np.savetxt(f'{output_path}/points/{shape}_origin_adj_{views[i]}_stb.txt', standby, fmt='%d', delimiter='\t')


                print(f"{shape}, {views[i]} view: D_Illum: {distance_ill}, D_Stb: {distance_stb}, "
                      f"D_between: {min(dist_between) if len(dist_between) > 0 else 0, max(dist_between) if len(dist_between) > 0 else 0, statistics.mean(dist_between) if len(dist_between) > 0 else 0}, "
                      f"Obstruction Times: {len(standby_block) if len(standby_block) > 0 else 0}, standby_block: {min(standby_block) if len(standby_block) > 0 else 0, max(standby_block) if len(standby_block) > 0 else 0,  statistics.mean(standby_block) if len(standby_block) > 0 else 0}")

                result.append([shape, views[i], distance_ill, distance_stb, min(dist_between) if len(dist_between) > 0 else 0, max(dist_between) if len(dist_between) > 0 else 0, statistics.mean(dist_between) if len(dist_between) > 0 else 0,
                               len(standby_block), min(standby_block) if len(standby_block) > 0 else 0, max(standby_block) if len(standby_block) > 0 else 0, statistics.mean(standby_block) if len(standby_block) > 0 else 0])
                csv_file_name = f"/Users/shuqinzhu/Desktop/obstructing/K{K}_result_origin.csv"

                # Open the CSV file in write mode and create a CSV writer
                with open(csv_file_name, mode='w', newline='') as file:
                    writer = csv.writer(file)

                    # Write the data from the list to the CSV file
                    for row in result:
                        writer.writerow(row)
