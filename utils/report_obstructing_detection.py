import math
import statistics

import numpy as np
import matplotlib as mpl
from matplotlib.ticker import PercentFormatter

from solve_obstructing import *
from standby_or_dispatcher import distance_point_to_line
from obstructing_detecting import rotate_vector

mpl.rcParams['font.family'] = 'Times New Roman'


def get_shape_info(file_path, ptcld_folder, shape, ratio):
    boundary = get_boundary(ptcld_folder, f"{shape}.txt", ratio)

    standby_file = f"{shape}_standby.txt"

    standbys = read_coordinates(f"{file_path}/points/{standby_file}", ' ', 1)
    standbys = standbys[:, 0:3]

    dispatcher = []
    dispatcher.append([boundary[0][0], boundary[0][1], 0])
    dispatcher.append([boundary[1][0], boundary[0][1], 0])

    return standbys, boundary, dispatcher


def get_boundary(ptcld_folder, ptcld_file, ratio):
    points = read_coordinates(f"{ptcld_folder}/{ptcld_file}", ' ')

    points = np.array(points)
    points = points * ratio

    point_boundary = [
        [min(points[:, 0]), min(points[:, 1]), min(points[:, 2])],
        [max(points[:, 0]), max(points[:, 1]), max(points[:, 2])]
    ]

    return point_boundary


def get_recover_distance_move_back(standbys, shape, k, ptcld_folder, ratio, obstructing_list, moved_standbys):
    group_file = f"{shape}_G{k}.xlsx"

    groups = read_cliques_xlsx(f"{ptcld_folder}/{group_file}", ratio)

    dists = []

    for i, group in enumerate(groups):

        if obstructing_list[i]:
            distances = [get_distance(moved_standbys[i], coord) for coord in group]
            dists.extend(distances)

        else:
            distances = [get_distance(standbys[i], coord) for coord in group]
            dists.extend(distances)

            if not (moved_standbys[i] == standbys[i]).all():
                a=1

    return dists

def get_recover_distance_move_back2(standbys, shape, k, ptcld_folder, ratio, obstructing_list, moved_standbys):
    group_file = f"{shape}_G{k}.xlsx"

    groups = read_cliques_xlsx(f"{ptcld_folder}/{group_file}", ratio)

    dists = []

    for i, group in enumerate(groups):

        distances = [get_distance(moved_standbys[i], coord) for coord in group]
        dists.extend(distances)

    return dists

def get_recover_distance(standbys, shape, k, ptcld_folder, ratio, obstructing_list, dispatcher):
    group_file = f"{shape}_G{k}.xlsx"

    groups = read_cliques_xlsx(f"{ptcld_folder}/{group_file}", ratio)

    dists = []

    for i, group in enumerate(groups):

        if obstructing_list[i]:
            distances = [distance_point_to_line(coord, dispatcher) for coord in group]
            dists.extend(distances)

        else:
            distances = [get_distance(standbys[i], coord) for coord in group]
            dists.extend(distances)

    return dists


def read_bools_from_file(file_path):
    with open(file_path, 'r') as file:
        # Read each line, strip whitespace, convert to int, and add to list
        bool_list = [int(line.strip()) for line in file]
    return bool_list


def draw_change_plot(path, type, name, all_info):
    removed_lists, standby_nums, mtids_change_percentages, avg_dists_traveled = [], [], [], []

    for info in all_info:
        removed_lists.append(info[0])
        standby_nums.append(info[1])
        mtids_change_percentages.append(info[2])
        avg_dists_traveled.append(info[3])

    draw_dissolved_percentage(granularity, removed_lists, standby_nums, name,
                             f"{path}/{type}/{shape}_K{k}_GR{granularity}_dissolved_percentage.png")
    draw_MTID_change_percentage(granularity, mtids_change_percentages,
                             f"{path}/{type}/{shape}_K{k}_GR{granularity}_MTID_percentage.png")
    draw_avg_dist_traveled(granularity, avg_dists_traveled,
                             f"{path}/{type}/{shape}_K{k}_GR{granularity}_dist_traveled.png")


def draw_changed_standby(granularity, restored_list, removed_list, activating_list, save_path):
    degrees = [i * granularity for i in range(0, math.floor(360 / granularity) + 1)]

    fig = plt.figure(figsize=(5, 3), layout='constrained')
    restored_line, = plt.plot(degrees, restored_list, marker='o', markersize=4, label=f'Restored Standby FLSs')

    removed_line, = plt.plot(degrees, removed_list, marker='s', markersize=4, label=f'Removed Standby FLSs')

    activating_line, = plt.plot(degrees, activating_list, marker='x', markersize=4, label=f'Activated Standby FLSs')

    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax.set_title('Number of Standby FLSs', loc='left')
    ax.set_xlabel("User's View Angle ($^\circ$)", loc='right', fontsize="large")
    ax.set_xlim(left=0, right=365)
    plt.xticks(np.arange(0, 360 + granularity, step=max(granularity, 20)))
    # ax.set_ylim(0, 40)

    # plt.text(6, 48, 'With Priority Queue', color=pri_line.get_color(), fontweight='bold', zorder=3)
    #
    # plt.text(6, 54, 'No Priority Queue', color=nopri_line.get_color(), fontweight='bold', zorder=3)

    # Add legend
    ax.legend()
    # plt.show(dpi=500)
    plt.savefig(save_path, dpi=500)
    plt.close()


def draw_avg_dist_traveled(granularity, dists_lists, save_path):
    degrees = [i * granularity for i in range(0, math.floor(360 / granularity) + 1)]

    fig = plt.figure(figsize=(5, 3), layout='constrained')

    plt.plot(degrees, dists_lists[0], marker='s', markersize=4, label=f'Q=1')
    plt.plot(degrees, dists_lists[1], marker='x', markersize=4, label=f'Q=5')
    plt.plot(degrees, dists_lists[2], marker='o', markersize=4, label=f'Q=10')

    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax.set_title('Avg Distance Traveled (Display Cells)', loc='left')
    ax.set_xlabel("Degree of Movement ($^\circ$)", loc='right', fontsize="large")
    ax.set_xlim(left=0, right=365)
    plt.xticks(np.arange(0, 360 + granularity, step=max(granularity, 20)))
    ax.set_ylim(0)

    # yticks = list(plt.yticks()[0])
    # yticks = yticks + [max(max(dists_lists))]
    # plt.yticks(sorted(yticks))

    # Add legend
    ax.legend(loc=(0.8, 0.47))
    # plt.show(dpi=500)
    plt.savefig(save_path, dpi=500)
    plt.close()


def draw_MTID_change_percentage(granularity, change_lists, save_path):
    degrees = [i * granularity for i in range(0, math.floor(360 / granularity) + 1)]

    fig = plt.figure(figsize=(5, 3), layout='constrained')

    plt.plot(degrees, change_lists[0], marker='s', markersize=4, label=f'Q=1')
    plt.plot(degrees, change_lists[1], marker='x', markersize=4, label=f'Q=5')
    plt.plot(degrees, change_lists[2], marker='o', markersize=4, label=f'Q=10')

    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_major_formatter(PercentFormatter(1))

    ax.set_title('Percentage Increase in MTID', loc='left')
    ax.set_xlabel("Degree of Movement ($^\circ$)", loc='right', fontsize="large")

    if np.max(np.array(change_lists)) < 0:
        ax.set_ylim(np.min(np.array(change_lists)) * 1.05, 0)
    else:
        ax.set_ylim(0, np.max(np.array(change_lists)) * 1.05)
    ax.set_xlim(left=0, right=365)
    plt.xticks(np.arange(0, 360 + granularity, step=max(granularity, 20)))


    # Add legend
    ax.legend()
    # plt.show(dpi=500)
    plt.savefig(save_path, dpi=500)
    plt.close()


def draw_dissolved_percentage(granularity, removed_lists, total_groups, type, save_path):
    degrees = [i * granularity for i in range(0, math.floor(360 / granularity) + 1)]

    fig = plt.figure(figsize=(5, 3), layout='constrained')

    dissolved_list = [dissolved/total_groups[0] for dissolved in removed_lists[0]]
    plt.plot(degrees, dissolved_list, marker='s', markersize=4, label=f'Q=1')


    dissolved_list = [dissolved/total_groups[1] for dissolved in removed_lists[1]]
    plt.plot(degrees, dissolved_list, marker='x', markersize=4, label=f'Q=5')


    dissolved_list = [dissolved/total_groups[2] for dissolved in removed_lists[2]]
    plt.plot(degrees, dissolved_list, marker='o', markersize=4, label=f'Q=10')

    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_major_formatter(PercentFormatter(1))

    ax.set_title(f'Percentage of {type} Reliability Groups', loc='left')
    ax.set_xlabel("Degree of Movement ($^\circ$)", loc='right', fontsize="large")
    ax.set_ylim(0, 1.05)
    ax.set_xlim(left=0, right=365)
    plt.xticks(np.arange(0, 360 + granularity, step=max(granularity, 20)))
    # ax.set_ylim(0, 40)

    # Add legend
    ax.legend()
    # plt.show(dpi=500)
    plt.savefig(save_path, dpi=500)
    plt.close()


def draw_changed_standby_permanent(granularity, removed_list, activating_list, save_path):
    degrees = [i * granularity for i in range(0, math.floor(360 / granularity) + 1)]

    fig = plt.figure(figsize=(5, 3), layout='constrained')

    removed_line, = plt.plot(degrees, removed_list, marker='s', markersize=4, label=f'Removed Standby FLSs')
    activating_line, = plt.plot(degrees, activating_list, marker='x', markersize=4, label=f'Activated Standby FLSs')

    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax.set_title('Number of Standby FLSs', loc='left')
    ax.set_xlabel("User's View Angle ($^\circ$)", loc='right', fontsize="large")
    ax.set_xlim(left=0, right=365)
    plt.xticks(np.arange(0, 360 + granularity, step=max(granularity, 20)))
    # ax.set_ylim(0, 40)

    # plt.text(6, 48, 'With Priority Queue', color=pri_line.get_color(), fontweight='bold', zorder=3)
    #
    # plt.text(6, 54, 'No Priority Queue', color=nopri_line.get_color(), fontweight='bold', zorder=3)

    # Add legend
    ax.legend()
    # plt.show(dpi=500)
    plt.savefig(save_path, dpi=500)
    plt.close()


def dissolve(figure_path, file_path, ptcld_folder, granularity, shape, speed, ratio):

    max_speed = max_acceleration = max_deceleration = speed

    standbys, boundary, dispatcher = get_shape_info(file_path, ptcld_folder, shape, ratio)

    obstructing_list = read_bools_from_file(
        f'{file_path}/points/{shape}_{granularity}_{math.floor(360 / granularity) - 1}.txt')

    standby_list = [False for _ in obstructing_list]

    removed_list = []
    activating_list = []
    cumulative_removed_list = []
    cumulative_removed = 0

    mtids_change_percentage = []

    dists = get_recover_distance(standbys, shape, k, ptcld_folder, ratio, standby_list, dispatcher)
    mtids = [calculate_travel_time(max_speed, max_acceleration, max_deceleration, d) for d in dists]
    ori_mtid = statistics.mean(mtids)

    avg_dist_traveled = []

    for i in range(0, math.floor(360 / granularity) + 1):
        index = i % math.floor(360 / granularity)
        obstructing_list = read_bools_from_file(f'{file_path}/points/{shape}_{granularity}_{index}.txt')

        dist_traveled = []
        removed = activating = 0

        for j in range(0, len(obstructing_list)):
            if obstructing_list[j] and not standby_list[j]:
                removed += 1
                standby_list[j] = True
                cumulative_removed += 1
                dist_traveled.append(distance_point_to_line(standbys[j], dispatcher))
            elif not obstructing_list[j] and not standby_list[j]:
                activating += 1

        removed_list.append(removed)
        activating_list.append(activating)
        cumulative_removed_list.append(cumulative_removed)

        avg_dist_traveled.append(statistics.mean(dist_traveled) if len(dist_traveled) > 0 else 0)

        dists = get_recover_distance(standbys, shape, k, ptcld_folder, ratio, standby_list, dispatcher)
        mtids = [calculate_travel_time(max_speed, max_acceleration, max_deceleration, d) for d in dists]

        mtids_change_percentage.append((statistics.mean(mtids) - ori_mtid)/ori_mtid)

    draw_changed_standby_permanent(granularity, removed_list, activating_list,
                                   f"{figure_path}/Dissolve/{shape}_R{ratio}_K{k}_GR{granularity}.png")
    print(f"Shape:{shape}, R:{ratio}, G:{file_path[-1]}, Dissolved Percentage:{sum(removed_list)/len(standby_list) * 100}")

    return cumulative_removed_list, len(standby_list), mtids_change_percentage, avg_dist_traveled


def suspend(figure_path, file_path, ptcld_folder, granularity, shape, speed, ratio):
    max_speed = max_acceleration = max_deceleration = speed

    standbys, boundary, dispatcher = get_shape_info(file_path, ptcld_folder, shape, ratio)

    obstructing_list = read_bools_from_file(
        f'{file_path}/points/{shape}_{granularity}_{math.floor(360 / granularity) - 1}.txt')

    standby_list = [False for _ in obstructing_list]

    restored_list = []
    removed_list = []
    activating_list = []
    mtids_change_percentage = []

    dists = get_recover_distance(standbys, shape, k, ptcld_folder, ratio, standby_list, dispatcher)
    mtids = [calculate_travel_time(max_speed, max_acceleration, max_deceleration, d) for d in dists]
    ori_mtid = statistics.mean(mtids)

    avg_dist_traveled = []

    for i in range(0, math.floor(360 / granularity) + 1):
        index = i % math.floor(360 / granularity)
        obstructing_list = read_bools_from_file(f'{file_path}/points/{shape}_{granularity}_{index}.txt')

        dist_traveled = []

        restored = removed = activating = 0

        for j in range(0, len(obstructing_list)):
            if obstructing_list[j] and not standby_list[j]:
                removed += 1
                dist_traveled.append(distance_point_to_line(standbys[j], dispatcher))
            elif not obstructing_list[j] and standby_list[j]:
                restored += 1
                activating += 1
                dist_traveled.append(distance_point_to_line(standbys[j], dispatcher))
            elif not obstructing_list[j]:  # and not standby_list[j]:
                activating += 1

        restored_list.append(restored)
        removed_list.append(removed)
        activating_list.append(activating)
        standby_list = obstructing_list

        avg_dist_traveled.append(statistics.mean(dist_traveled))

        dists = get_recover_distance(standbys, shape, k, ptcld_folder, ratio, standby_list, dispatcher)
        mtids = [calculate_travel_time(max_speed, max_acceleration, max_deceleration, d) for d in dists]

        mtids_change_percentage.append((statistics.mean(mtids) - ori_mtid)/ori_mtid)

    draw_changed_standby(granularity, restored_list, removed_list, activating_list,
                         f"{figure_path}/Suspend/{shape}_R{ratio}_K{k}_GR{granularity}.png")

    return removed_list, len(standby_list), mtids_change_percentage, avg_dist_traveled



def suspend_move_back(file_path, ptcld_folder, granularity, shape, speed, ratio):
    max_speed = max_acceleration = max_deceleration = speed

    standbys, boundary, dispatcher = get_shape_info(file_path, ptcld_folder, shape, ratio)

    obstructing_list = read_bools_from_file(
        f'{file_path}/points/{shape}_{granularity}_{math.floor(360 / granularity) - 1}.txt')

    standby_list = [False for _ in obstructing_list]

    restored_list = []
    removed_list = []
    activating_list = []
    mtids_change_percentage = []

    dists = get_recover_distance_move_back(standbys, shape, k, ptcld_folder, ratio, standby_list, standbys)
    mtids = [calculate_travel_time(max_speed, max_acceleration, max_deceleration, d) for d in dists]
    ori_mtid = statistics.mean(mtids)

    avg_dist_traveled = []

    user_shifting = 100
    user_pos = [boundary[0][0] / 2 + boundary[1][0] / 2, boundary[0][1] - user_shifting,
                boundary[0][2] / 2 + boundary[1][2] / 2]
    shape_center = [boundary[0][0] / 2 + boundary[1][0] / 2, boundary[0][1] / 2 + boundary[1][1] / 2,
                    boundary[0][2] / 2 + boundary[1][2] / 2]
    vector = np.array(user_pos) - np.array(shape_center)

    for i in range(0, math.floor(360 / granularity) + 1):
        index = i % math.floor(360 / granularity)
        obstructing_list = read_bools_from_file(f'{file_path}/points/{shape}_{granularity}_{index}.txt')

        angle = i * granularity
        user_pos = shape_center + rotate_vector(vector, angle)
        solve_single_view(shape, k, ratio, f"{granularity}_{index}", "", user_pos, ptcld_folder, file_path, test=False, file_surfix="moved_standby")

        dist_traveled = []

        none_obstruct_stanby = read_coordinates(f"{file_path}/points/{shape}_{granularity}_{index}_moved_standby.txt", ' ', 1)
        none_obstruct_stanby = none_obstruct_stanby[:, 0:3]

        restored = removed = activating = 0

        for j in range(0, len(obstructing_list)):
            if obstructing_list[j] and not standby_list[j]:
                removed += 1
                dist_traveled.append(get_distance(standbys[j], none_obstruct_stanby[j]))
            elif not obstructing_list[j] and standby_list[j]:
                restored += 1
                activating += 1
                dist_traveled.append(get_distance(standbys[j], none_obstruct_stanby[j]))
            elif not obstructing_list[j]:
                activating += 1

        restored_list.append(restored)
        removed_list.append(removed)
        activating_list.append(activating)
        standby_list = obstructing_list

        avg_dist_traveled.append(statistics.mean(dist_traveled))

        dists = get_recover_distance_move_back(standbys, shape, k, ptcld_folder, ratio, standby_list, none_obstruct_stanby)

        dists2 = get_recover_distance_move_back2(standbys, shape, k, ptcld_folder, ratio, standby_list, none_obstruct_stanby)

        mtids = [calculate_travel_time(max_speed, max_acceleration, max_deceleration, d) for d in dists]

        mtids_change_percentage.append((statistics.mean(mtids) - ori_mtid)/ori_mtid)

    # draw_changed_standby(granularity, restored_list, removed_list, activating_list,
    #                      f"/Users/shuqinzhu/Desktop/obstructing_detection/temporary/{shape}_R{ratio}_K{k}_GR{granularity}.png")

    return removed_list, len(standby_list), mtids_change_percentage, avg_dist_traveled



if __name__ == "__main__":

    # ptcld_folder = "/Users/shuqinzhu/Desktop/pointcloud"
    # meta_dir = "/Users/shuqinzhu/Desktop"
    figure_path = "/Users/shuqinzhu/Desktop/obstructing_detection"

    ptcld_folder = "../assets/pointcloud"
    meta_dir = "../assets"

    speed = 6.11

    for granularity in [10]:
        p_list = []
        for shape in ["skateboard"]:
                # txt_file = f"{shape}.txt"
                # standby_file = f"{shape}_standby.txt"

            for k in [3]:

                temp_info, perm_info, move_back_info = [], [], []
                for ratio in [1, 5, 10]:
                    file_path = f"{meta_dir}/obstructing/R{ratio}/K{k}"
                    # temp_info.append(suspend(figure_path, file_path, ptcld_folder, granularity, shape, speed, ratio))
                    # perm_info.append(dissolve(figure_path, file_path, ptcld_folder, granularity, shape, speed, ratio))
                    move_back_info.append(suspend_move_back(file_path, ptcld_folder, granularity, shape, speed, ratio))



                # draw_change_plot(figure_path, 'Suspend', 'Suspend', temp_info)
                # draw_change_plot(figure_path, 'Dissolve', 'Dissolve', perm_info)

                draw_change_plot(figure_path, 'Moveback', 'Moved Back', move_back_info)
