import numpy as np
import os

import pandas as pd
from matplotlib import pyplot as plt

file_folder = "/Users/shuqinzhu/Desktop/Experiments_Results.nosync/group_formation"
K = 3


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


def get_standby_coords(groups):
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


def distance(point1, point2):
    return np.linalg.norm(np.array(point1) - np.array(point2))


# Function to check if a point is inside a cube
def is_inside_cube(point, cube_center, distance):
    return all(abs(p - c) <= distance for p, c in zip(point, cube_center))


# Function to find visible cubes
def visible_cubes(camera, cubes):
    # Calculate distances from the camera to each cube
    distances = [distance(camera, cube[:3]) for cube in cubes]

    # Sort cubes by distance
    sorted_indices = np.argsort(distances)

    visible = []
    blocking = []
    visible_index = []
    blocking_index = []
    blocked_by = []
    for i in sorted_indices:
        cube = cubes[i]
        is_visible = True

        # Check if the line of sight to the cube is obstructed
        for j in sorted_indices:
            if j == i:
                break

            # Check if any point on the line segment is inside the obstructing cube
            t_values = np.linspace(0, 1, 100)  # Adjust the number of points as needed
            line_points = np.outer((1 - t_values), camera) + np.outer(t_values, cube[:3])
            if any(is_inside_cube(point, cubes[j][0:3], 0.5) for point in line_points):
                if cubes[j][3] == 1 and cube[3] != 1 and any(is_inside_cube(point, cubes[j][0:3], 0.5) for point in line_points):
                    if j in visible_index and j not in blocking_index:
                        blocking.append(cubes[j][0:3])
                        blocked_by.append(cube[0:3])
                        blocking_index.append(j)

                is_visible = False
                break

        if is_visible:
            visible_index.append(i)
            visible.append(cube)

    return visible, blocking, blocked_by, blocking_index


def check_blocking_nums(shape):
    input_file = f"{shape}_G{K}.xlsx"

    txt_file = f"{shape}.txt"

    groups, a = read_cliques_xlsx(os.path.join(file_folder, input_file))

    group_standby_coord = get_standby_coords(groups)

    points = read_coordinates(f"{file_folder}/pointcloud/{txt_file}")

    points = np.array(points)


    point_boundary = [
        [min(points[:, 0]), min(points[:, 1]), min(points[:, 2])],
        [max(points[:, 0]), max(points[:, 1]), max(points[:, 2])]
    ]

    for coord in group_standby_coord:

        coords = points[:, :3]

        coords = coords.tolist()

        if coord in coords:
            directions = []
            for x in [-1, 0, 1]:
                for y in [-1, 0, 1]:
                    for z in [-1, 0, 1]:
                        directions.append([x, y, z])

            directions = np.array(directions)

            overlap = True

            while overlap:
                for dirc in directions:
                    new_coord = coord + dirc
                    if new_coord.tolist() not in coords:
                        overlap = False
                        break

                if overlap:
                    print(f"None Stopping")
                break
        coord.append(1)
        points = np.concatenate((points, [coord]), axis=0)
    return points, point_boundary


if __name__ == "__main__":

    # shape = "skateboard"

    for shape in [ "hat", "dragon"]:
        points, boundary = check_blocking_nums(shape)

        cam_positions = [
            #top
            [boundary[0][0] + boundary[1][0]/2, boundary[0][1] + boundary[1][1]/2, boundary[1][2] + 100],
            #down
            [boundary[0][0] + boundary[1][0]/2, boundary[0][1] + boundary[1][1]/2, boundary[0][2] - 100],
            #left
            [boundary[1][0] + 100, boundary[0][1] + boundary[1][1]/2, boundary[0][0] + boundary[1][0]/2],
            #right
            [boundary[0][0] - 100, boundary[0][1] + boundary[1][1] / 2, boundary[0][0] + boundary[1][0]/2],
            #front
            [boundary[0][0] + boundary[1][0]/2, boundary[0][1] - 100, boundary[0][0] + boundary[1][0] / 2],
            #back
            [boundary[0][0] + boundary[1][0]/2, boundary[1][1] + 100, boundary[0][0] + boundary[1][0] / 2]

            ]

        views = ["top", "bottom", "left", "right", "front", "back"]
        elevations = [90, -90, 0, 0, 0, 0]
        azimuths = [0, 0, -90, 90, 180,  0]

        # Create a 3D scatter plot
        fig = plt.figure(figsize=(18, 12))

        illum = []
        standby = []
        for coord in points:
            if coord[3] == 0:
                illum.append(coord[:3])
            else:
                standby.append(coord[:3])

        illum = np.array(illum)
        standby = np.array(standby)

        for i, view in enumerate(views):
            ax = fig.add_subplot(projection='3d')
            ax.scatter(illum[:, 0], illum[:, 1], illum[:, 2], c='blue', marker='+', alpha=1)
            ax.scatter(standby[:, 0], standby[:, 1], standby[:, 2], c='red', marker='x', alpha=1)
            # ax.set_xlabel('X Label')
            # ax.set_ylabel('Y Label')
            # ax.set_zlabel('Z Label')
            ax.view_init(elev=elevations[i], azim=azimuths[i])
            # ax.set_title(view.capitalize() + ' View')
            ax.set_aspect('equal')
            plt.savefig(f'/Users/shuqinzhu/Desktop/exp_figure/view_standby/{shape}_K{K}_{view}.png', dpi=500)

        for i, camera in enumerate(cam_positions):
            visible, blocking, blocked_by, blocking_index = visible_cubes(camera, points)
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
            

            ax = fig.add_subplot(projection='3d')
            ax.scatter(illum[:, 0], illum[:, 1], illum[:, 2], c='blue', marker='+', alpha=1)
            ax.scatter(standby[:, 0], standby[:, 1], standby[:, 2], c='red', marker='x', alpha=1)
            # ax.set_xlabel('X Label')
            # ax.set_ylabel('Y Label')
            # ax.set_zlabel('Z Label')
            ax.view_init(elev=elevations[i], azim=azimuths[i])
            # ax.set_title(view.capitalize() + ' View')
            ax.set_aspect('equal')
            plt.savefig(f'/Users/shuqinzhu/Desktop/exp_figure/view_standby/{shape}_K{K}_{views[i]}.png', dpi=500)

            ax = fig.add_subplot(projection='3d')
            ax.scatter(visible_illum[:, 0], visible_illum[:, 1], visible_illum[:, 2], c='blue', marker='+', alpha=1)
            ax.scatter(visible_standby[:, 0], visible_standby[:, 1], visible_standby[:, 2], c='red', marker='x', alpha=1)
            ax.view_init(elev=elevations[i], azim=azimuths[i])
            # ax.set_title(view.capitalize() + ' View')
            ax.set_aspect('equal')
            plt.savefig(f'/Users/shuqinzhu/Desktop/exp_figure/view_standby/{shape}_K{K}_{views[i]}_visible.png')

            ax = fig.add_subplot(projection='3d')
            ax.scatter(blocking[:, 0], blocking[:, 1], blocking[:, 2], c='red', marker='x', alpha=1)
            ax.scatter(blocked_by[:, 0], blocked_by[:, 1], blocked_by[:, 2], c='blue', marker='+', alpha=1)
            ax.view_init(elev=elevations[i], azim=azimuths[i])
            # ax.set_title(view.capitalize() + ' View')
            ax.set_aspect('equal')
            plt.savefig(f'/Users/shuqinzhu/Desktop/exp_figure/view_standby/{shape}_K{K}_{views[i]}_overlap.png')


            ax = fig.add_subplot(projection='3d')
            ax.scatter(blocking[:, 0], blocking[:, 1], blocking[:, 2], c='red', marker='x', alpha=1)
            ax.view_init(elev=elevations[i], azim=azimuths[i])
            # ax.set_title(view.capitalize() + ' View')
            ax.set_aspect('equal')
            plt.savefig(f'/Users/shuqinzhu/Desktop/exp_figure/view_standby/{shape}_K{K}_{views[i]}_obstructing.png')

            ax = fig.add_subplot(projection='3d')
            ax.scatter(blocked_by[:, 0], blocked_by[:, 1], blocked_by[:, 2], c='blue', marker='+', alpha=1)
            ax.view_init(elev=elevations[i], azim=azimuths[i])
            # ax.set_title(view.capitalize() + ' View')
            ax.set_aspect('equal')
            plt.savefig(f'/Users/shuqinzhu/Desktop/exp_figure/view_standby/{shape}_K{K}_{views[i]}_blocked.png')


            print(f"{shape}, {views[i]} view: Number of Illuminating FLS: {len(visible_illum)}, Number of Obstructing FLS: {len(visible_standby)}, Standby Blocking: {len(visible_standby)}, Acutal Number: {len(blocking_index)}")

            # print(f"{shape}, {views[i]} view: Standby Blocking: {blocking}")

            # print(f"{shape}, {views[i]} view: Number of Illuminating FLS: {count_0}, Number of Obstructing FLS: {count_1}, Standby Blocking: {blocking}")
