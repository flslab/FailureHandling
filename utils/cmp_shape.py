import os

import pandas as pd
from itertools import combinations
from ast import literal_eval
import numpy as np
import time
import random
from statistics import median
from openpyxl import load_workbook
import math
import csv
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from collections import Counter

mpl.rcParams['font.family'] = 'Times New Roman'


def calculate_euclidean_distance(point1, point2):
    return sum((a - b) ** 2 for a, b in zip(point1, point2)) ** 0.5


def calculate_distances_to_center(points, center):
    return [calculate_euclidean_distance(point, center) for point in points]


def calculate_centroid(points):
    return [sum(coord) / len(coord) for coord in zip(*points)]


def calculate_center(coords):
    return [sum(coord) / len(coord) for coord in zip(*coords)]


def process_excel(file_path):
    try:
        # Read the 'cliques' sheet
        df = pd.read_excel(file_path, sheet_name='cliques', engine='openpyxl')

        # Extract all distance values
        all_distances = []
        for distances_list in df['8 distance to center']:
            # Convert string representation of list to actual list (if necessary)
            if isinstance(distances_list, str):
                distances_list = eval(distances_list)
            all_distances.extend(distances_list)

        # Calculate and print statistics
        for i, dist in enumerate(all_distances):
            if dist < 1:
                all_distances[i] = 1

        else:
            print("No distances found.")
    except FileNotFoundError:
        print(f"The file at path {file_path} does not exist.")
    except Exception as e:
        print(f"An error occurred 1: {e}")

    return all_distances


def get_avg_dist_to_centroid(file_path):
    try:
        # Read the 'cliques' sheet
        df = pd.read_excel(file_path, sheet_name='cliques', engine='openpyxl')

        # Extract all distance values
        avg_dists_to_centroid = []
        for distances_list in df['8 distance to center']:
            # Convert string representation of list to actual list (if necessary)
            if isinstance(distances_list, str):
                distances_list = eval(distances_list)

            for i, dist in enumerate(distances_list):
                if dist < 1:
                    distances_list[i] = 1

            avg_dists_to_centroid.append(sum(distances_list) / len(distances_list))

        else:
            print("No distances found.")
    except FileNotFoundError:
        print(f"The file at path {file_path} does not exist.")
    except Exception as e:
        print(f"An error occurred 1: {e}")

    return avg_dists_to_centroid


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


def get_dispatcher_to_centroid(file_path):
    try:
        # Read the Excel file and access the 'cliques' sheet
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df = pd.read_excel(file_path, sheet_name='cliques', engine='openpyxl')

            # Convert string representation of lists to actual lists
            group_formation = df['7 coordinates'].apply(eval)

            # Calculate the center and distances to center for each row
            dispatcher_to_center = []

            dispatcher_coord = [0, 0, 0]
            for coords in group_formation:
                center = calculate_centroid(coords)
                dispatcher_to_center.append(calculate_euclidean_distance(center, dispatcher_coord))

        print("File processed successfully.")
    except FileNotFoundError:
        print(f"The file at path {file_path} does not exist.")
    except Exception as e:
        print(f"An error occurred 2: {e}")

    return dispatcher_to_center


def add_distance_to_center_column(file_path):
    try:
        # Read the Excel file and access the 'cliques' sheet
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df = pd.read_excel(file_path, sheet_name='cliques', engine='openpyxl')

            # Convert string representation of lists to actual lists
            group_formation = df['7 coordinates'].apply(eval)

            # Calculate the center and distances to center for each row
            df['8 distance to center'] = group_formation.apply(
                lambda coords: calculate_distances_to_center(coords, calculate_centroid(coords))
            )

            # Write the modified DataFrame back to the 'cliques' sheet
            for sheet in writer.book.sheetnames:
                if sheet != 'cliques':
                    writer.sheets[sheet] = writer.book[sheet]
            df.to_excel(writer, sheet_name='cliques', index=False)

        print("File processed successfully.")
    except FileNotFoundError:
        print(f"The file at path {file_path} does not exist.")
    except Exception as e:
        print(f"An error occurred 2: {e}")


def write_list_to_csv(file_path, input_list):
    try:
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(input_list)
        print("Data written successfully to", file_path)
    except Exception as e:
        print(f"An error occurred 3: {e}")


def get_groupsize_list(file_path):
    try:
        # Step 1: Read the Excel file and access the 'cliques' sheet
        df = pd.read_excel(file_path, sheet_name='cliques', engine='openpyxl')

        # Step 2: Read the '7 coordinates' column
        coordinates_column = df['7 coordinates']

        # Step 3: For each row, calculate the number of coordinates
        number_of_coordinates_per_row = [len(eval(row)) for row in coordinates_column]

        return number_of_coordinates_per_row
    except FileNotFoundError:
        print(f"The file at path {file_path} does not exist.")
        return None
    except Exception as e:
        print(f"An error occurred 4: {e}")
        return None


def read_coordinates(file_path):
    coordinates = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Split the line by spaces and convert each part to a float
                coord = [float(x) for x in line.strip().split(' ')]
                if len(coord) == 3:  # Ensure that there are exactly 3 coordinates
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


def draw_histogram(group_sizes, save_path):
    try:
        group_counts = Counter(group_sizes)

        # Get the unique group sizes and their respective counts
        sizes = list(group_counts.keys())
        counts = list(group_counts.values())

        # Create a bar graph
        plt.bar(sizes, counts)
        plt.xlabel('Size of the Group')
        plt.ylabel('Number of Groups of this Size')
        plt.title('Histogram of Group Sizes')

        ax = plt.gca()
        ax.get_xaxis().set_major_locator(plt.MaxNLocator(integer=True))
        ax.get_yaxis().set_major_locator(plt.MaxNLocator(integer=True))

        plt.savefig(f'/Users/shuqinzhu/Desktop/figures/{save_path}')
        # plt.show()
        plt.close()
        print(f"Histogram saved successfully to {save_path}")
    except Exception as e:
        print(f"An error occurred 6: {e}")


def calculate_overall_average(file_path, column_name):
    try:
        # Read the 'cliques' sheet from the Excel file
        df = pd.read_excel(file_path, sheet_name='cliques')

        # Convert string representation of lists to actual lists (if necessary)
        df[column_name] = df[column_name].apply(eval)

        # Get all distances as a single list
        all_distances = [dist for sublist in df[column_name] for dist in sublist]

        print(f"{column_name}: {sum(all_distances)}, {len(all_distances)}, {sum(all_distances) / len(all_distances)}")

        # Calculate the overall average distance

        return all_distances
    except FileNotFoundError:
        print(f"The file at path {file_path} does not exist.")
        return None
    except Exception as e:
        print(f"An error occurred 7: {e}")
        return None


# def compare_columns(file_path, column_name1, column_name2):
#     try:
#         # Read the Excel file
#         df = pd.read_excel(file_path)

#         # Convert string representation of lists to actual lists (if necessary)
#         df[column_name1] = df[column_name1].apply(eval)
#         df[column_name2] = df[column_name2].apply(eval)

#         # Iterate over the rows and compare the sum of distances in the two columns
#         for index, row in df.iterrows():
#             if sum(row[column_name1]) < sum(row[column_name2]):
#                 print(f"{column_name1} smaller {column_name2}: {sum(row[column_name1])} < {sum(row[column_name2])}")
#     except FileNotFoundError:
#         print(f"The file at path {file_path} does not exist.")
#     except Exception as e:
#         print(f"An error occurred 8: {e}")

def mttr_groupsize_plot(mttrs, group_sizes, name):
    # Assuming data_2d_list is your 2D list with MTTR data

    # Create a box plot
    plt.boxplot(mttrs, labels=group_sizes)

    # Set the x-axis label
    plt.xlabel('Group Size (G)')

    # Set the y-axis label
    plt.ylabel('MTTR')

    # Set the title
    plt.title('Box Plot of MTTR by Group Size')

    # Display the plot
    plt.savefig(f"/Users/shuqinzhu/Desktop/figures/MTTR/{name}")
    plt.close()


def mtdi_groupsize_plot(mtdis, group_sizes, name):
    # Assuming data_2d_list is your 2D list with MTTR data

    # Create a box plot
    plt.boxplot(mtdis, labels=group_sizes)

    # Set the x-axis label
    plt.xlabel('Group Size (G)')

    # Set the y-axis label
    plt.ylabel('MTDI')

    # Set the title
    plt.title('Box Plot of MTDI by Group Size')

    # Display the plot
    plt.savefig(f"/Users/shuqinzhu/Desktop/figures/MTDI/{name}")
    plt.close()


def dispatcher_to_centroid_box_plot(data, group_sizes, name):
    # Assuming data_2d_list is your 2D list with MTTR data

    # Create a box plot
    plt.boxplot(data, labels=group_sizes)

    # Set the x-axis label
    plt.xlabel('Group Size (G)')

    # Set the y-axis label
    plt.ylabel('Distance from Dispatcher to Group Centroids')

    # Display the plot
    plt.savefig(f"/Users/shuqinzhu/Desktop/figures/dispatcher_to_centroid/{name}")
    plt.close()


def distance_centroid_to_point_plot(data_sets, group_sizes, name):
    # Create a box plot
    fig = plt.figure(figsize=(5, 3), layout='constrained')
    ax = fig.add_subplot()
    plt.boxplot(data_sets, labels=group_sizes)

    # print(f"Group centroid to points:{data_sets}")
    # Set the x-axis label
    plt.xlabel('Group Size (G)')

    # Set the title
    # plt.title('Distance from Group Centroid To Points in Group by Group Size')

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.set_title('Group Centroid To Points Distance', loc='left')

    # ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=False))
    # ax.get_xaxis().set_major_locator(plt.MaxNLocator(integer=True))
    # plt.ylim(bottom=min(min(data_sets)) - 1, top=max(max(data_sets)) + 1)
    # Display the plot
    # plt.tight_layout()
    plt.savefig(f"/Users/shuqinzhu/Desktop/figures/centroid_to_point/{name}", dpi=500)
    plt.close()


def time_centroid_to_point_plot(data_sets, group_sizes, speed_models, name):
    # Step 2: Plot the data
    fig = plt.figure(figsize=(5, 3), layout='constrained')
    ax = fig.add_subplot()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    for i, data_set in enumerate(data_sets):
        plt.plot(group_sizes, data_set, label=f'Speed Model: {speed_models[i]}')

    # Configure the chart
    plt.xlabel('Group Size')

    ax.set_title('Avg Time To Travel from Group Centroid to Points in Group', loc='left', zorder=4)
    # plt.ylabel('Avg Time To Travel from Group Centroid to Points in Group')
    # plt.title('Avg Time To Travel by Group Size')
    plt.legend(bbox_to_anchor=(0.9, 0.9),loc='upper right')
    plt.xticks(group_sizes)

    # Display the plot
    plt.savefig(f"/Users/shuqinzhu/Desktop/figures/time_centroid_to_point/{name}", dpi=500)
    plt.close()


def dispatcher_to_centroid_plot(data, group_sizes, name):
    # Step 2: Plot the data
    plt.figure()

    plt.plot(group_sizes, data)

    # Configure the chart
    plt.xlabel('Group Size')
    plt.ylabel('Avg Distance from Dispatcher to Group Centroid')
    plt.title('Avg Distance from Dispatcher to Group Centroid by Group Size')
    plt.legend()
    plt.xticks(group_sizes)

    # Display the plot
    plt.savefig(f"/Users/shuqinzhu/Desktop/figures/dispatcher_to_centroid/{name}")
    plt.close()


def compare_dispatcher_to_centroid_plot(datasets, group_sizes, name):
    # Step 2: Plot the data
    plt.figure()
    group_formation_name = ["CANF", "K-Means"]

    for i, data in enumerate(datasets):
        plt.plot(group_sizes, data, label=f'{group_formation_name[i]}')

    # Configure the chart
    plt.xlabel('Group Size')
    plt.ylabel('Avg Distance from Dispatcher to Group Centroid')
    plt.title('Avg Distance from Dispatcher to Group Centroid by Group Size')
    plt.legend()
    plt.xticks(group_sizes)

    # Display the plot
    plt.savefig(f"/Users/shuqinzhu/Desktop/figures/dispatcher_to_centroid/{name}")
    plt.close()


if __name__ == '__main__':

    mpl.rcParams['font.family'] = 'Times New Roman'
    max_speed = max_acceleration = max_deceleration = 6.11

    disp_cell_size = 0.05

    report_file_path = 'mttr_report.csv'
    group_names = ["CANF", "KMeans"]

    # shapes = ["chess", "dragon", "skateboard", "racecar"]
    shapes = ["skateboard"]

    reports = [["Shape", "Method", "Group Size", "Avg Pairwise Distance", "Avg Centroid Distance", "Min GroupSize",
                "Median GroupSize", "Max GroupSize", "Avg MTTR", "Min MTTR", "Median MTTR", "Max MTTR", "Min MTDI",
                "Median MTDI", "Max MTDI", "Avg Dist To Centroid", "Min Dist To Centroid", "Median  Dist To Centroid",
                "Max Dist To Centroid"]]

    dispatcher_to_center_compare = []

    for shape in shapes:

        file_path = '/Users/shuqinzhu/Desktop/skateboard_files/pointcloud/' + shape + '.txt'
        unique_coordinates = read_coordinates(file_path)

        F = len(unique_coordinates)


        for i, group_type in enumerate(["K", "G"]):

            group_name = group_names[i]
            mttr_list = []

            mtdi_list = []

            avg_dispatcher_to_center_list = []
            dispatcher_to_center_list = []

            centroid_dist_list = []

            time_to_travel_center_list = [[], [], [], []]

            for i, K in enumerate([3, 5, 10, 20]):

                file_path = shape + "_" + group_type + str(K) + ".xlsx"
                print(file_path)

                file_path = "/Users/shuqinzhu/Desktop/skateboard_files/" + file_path
                add_distance_to_center_column(file_path)

                dispatcher_to_center = get_dispatcher_to_centroid(file_path)
                avg_dispatcher_to_center = sum(dispatcher_to_center) / len(dispatcher_to_center)
                avg_dispatcher_to_center_list.append(avg_dispatcher_to_center)

                dispatcher_to_center_list.append(dispatcher_to_center)

                pairwise_dist = calculate_overall_average(file_path, '6 dist between each pair')
                centroid_dist = calculate_overall_average(file_path, '8 distance to center')

                avg_pairwise_dist = sum(pairwise_dist) / len(pairwise_dist)
                avg_centroid_dist = sum(centroid_dist) / len(centroid_dist)
                centroid_dist_list.append(centroid_dist)

                for i, speed_model in enumerate([3, 10, 30, 60]):
                    time_to_travel_center_list[i].append(
                        calculate_travel_time(speed_model, speed_model, speed_model, avg_centroid_dist))

                dists = process_excel(file_path)

                mttr = [calculate_travel_time(max_speed, max_acceleration, max_deceleration,
                                              dist * disp_cell_size if dist > 0 else disp_cell_size) for dist in dists]

                print(f"Lenth: {len(mttr)}")

                mttr_list.append(mttr)

                avg_mttr = calculate_travel_time(max_speed, max_acceleration, max_deceleration,
                                                 dists[0] * disp_cell_size if dists[0] > 0 else disp_cell_size)
                report = [shape, group_name, str(K), avg_pairwise_dist, avg_centroid_dist]

                group_sizes = get_groupsize_list(file_path)
                group_sizes.sort()

                print(group_sizes)
                median_index = len(group_sizes) // 2
                median_size = (group_sizes[median_index] + group_sizes[~median_index]) / 2

                report.append(str(group_sizes[0]))
                report.append(str(median_size))
                report.append(str(group_sizes[-1]))

                report_mttr = [sum(mttr) / len(mttr), min(mttr), median(mttr), max(mttr)]

                report.extend(report_mttr)

                mttf = 30 / 2

                group_dist_to_centroid = get_avg_dist_to_centroid(file_path)

                mtdis = []

                print(
                    f"Size of group_size: {len(group_sizes)}, Size of group_dist_to_centroid: {len(group_dist_to_centroid)}")

                mtdis = [(size * (mttf / (size + 1)) / (avg_mttr / (mttf / (size + 1)))) / F for size in group_sizes]

                mtdis.sort()
                mtdi_list.append(mtdis)
                max_mtdi = mtdis[-1]
                min_mtdi = mtdis[0]
                median_index = len(mtdis) // 2

                median_mtdi = (mtdis[median_index] + mtdis[~median_index]) / 2

                report.append(str(min_mtdi))
                report.append(str(median_mtdi))
                report.append(str(max_mtdi))

                report.append(str(sum(dists) / len(dists)))
                report.append(str(min(dists)))
                report.append(str(max(dists)))
                report.append(str(median(dists)))

                reports.append(report)

                # print(group_sizes)

                draw_histogram(group_sizes, shape + "_" + group_name + str(K) + "_groupsizehist.png")

            # print(f"Length of List: {len(mttr_list)}")
            mttr_groupsize_plot(mttr_list, [3, 5, 10, 20], f"{shape}_{group_name}_MTTR.png")
            mtdi_groupsize_plot(mtdi_list, [3, 5, 10, 20], f"{shape}_{group_name}_MTDI.png")
            distance_centroid_to_point_plot(centroid_dist_list, [3, 5, 10, 20],
                                            f"{shape}_{group_name}_dist_to_centroid.png")
            dispatcher_to_centroid_plot(avg_dispatcher_to_center_list, [3, 5, 10, 20],
                                        f"{shape}_{group_name}_dist_to_centroid.png")

            dispatcher_to_centroid_box_plot(dispatcher_to_center_list, [3, 5, 10, 20],
                                            f"{shape}_{group_name}_dist_to_centroid_box.png")

            dispatcher_to_center_compare.append(avg_dispatcher_to_center_list)

            time_centroid_to_point_plot(time_to_travel_center_list, [3, 5, 10, 20], [3, 10, 30, 60],
                                        f"{shape}_{group_name}_time_to_travel.png")

        compare_dispatcher_to_centroid_plot(dispatcher_to_center_compare, [3, 5, 10, 20],
                                            f"{shape}_compare_dist_to_centroid.png")

    write_list_to_csv(report_file_path, reports)
