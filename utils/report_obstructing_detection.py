import math
import numpy as np
import matplotlib as mpl
from solve_obstructing import *

mpl.rcParams['font.family'] = 'Times New Roman'


def read_bools_from_file(file_path):
    with open(file_path, 'r') as file:
        # Read each line, strip whitespace, convert to int, and add to list
        bool_list = [int(line.strip()) for line in file]
    return bool_list


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


def permanent_send_back(file_path, granularity, shape):
    # standbys = readz_coordinates(f"{file_path}/points/{standby_file}", ' ', 1)
    # dist_to_center = get_dist_to_centroid(standbys[:, 0:3], shape, k, ptcld_folder, ratio)

    obstructing_list = read_bools_from_file(
        f'{file_path}/points/{shape}_{granularity}_{math.floor(360 / granularity) - 1}.txt')

    standby_list = [False for _ in obstructing_list]

    restored_list = []
    removed_list = []
    activating_list = []

    for i in range(0, math.floor(360 / granularity) + 1):
        index = i % math.floor(360 / granularity)
        obstructing_list = read_bools_from_file(f'{file_path}/points/{shape}_{granularity}_{index}.txt')

        removed = activating = 0

        for j in range(0, len(obstructing_list)):
            if obstructing_list[j] and not standby_list[j]:
                removed += 1
                standby_list[j] = True
            elif not obstructing_list[j] and not standby_list[j]:
                activating += 1

        removed_list.append(removed)
        activating_list.append(activating)

    draw_changed_standby_permanent(granularity, removed_list, activating_list,
                                   f"/Users/shuqinzhu/Desktop/obstructing_detection/permanent/{shape}_R{ratio}_K{k}_GR{granularity}.png")


def temporary_send_back(file_path, granularity, shape):
    # standbys = read_coordinates(f"{file_path}/points/{standby_file}", ' ', 1)
    # dist_to_center = get_dist_to_centroid(standbys[:, 0:3], shape, k, ptcld_folder, ratio)

    obstructing_list = read_bools_from_file(
        f'{file_path}/points/{shape}_{granularity}_{math.floor(360 / granularity) - 1}.txt')

    standby_list = [False for _ in obstructing_list]

    restored_list = []
    removed_list = []
    activating_list = []

    for i in range(0, math.floor(360 / granularity) + 1):
        index = i % math.floor(360 / granularity)
        obstructing_list = read_bools_from_file(f'{file_path}/points/{shape}_{granularity}_{index}.txt')

        restored = removed = activating = 0

        for j in range(0, len(obstructing_list)):
            if obstructing_list[j] and not standby_list[j]:
                removed += 1
            elif not obstructing_list[j] and standby_list[j]:
                restored += 1
                activating += 1
            elif not obstructing_list[j]:  # and not standby_list[j]:
                activating += 1

        restored_list.append(restored)
        removed_list.append(removed)
        activating_list.append(activating)
        standby_list = obstructing_list

    draw_changed_standby(granularity, restored_list, removed_list, activating_list,
                         f"/Users/shuqinzhu/Desktop/obstructing_detection/temporary/{shape}_R{ratio}_K{k}_GR{granularity}.png")


if __name__ == "__main__":

    ptcld_folder = "/Users/shuqinzhu/Desktop/pointcloud"
    meta_dir = "/Users/shuqinzhu/Desktop"

    for granularity in [10, 45]:
        p_list = []
        for shape in ["skateboard", "dragon", "hat"]:
            for ratio in [1, 3, 5, 10]:
                # txt_file = f"{shape}.txt"
                # standby_file = f"{shape}_standby.txt"

                for k in [3, 20]:
                    file_path = f"{meta_dir}/obstructing/R{ratio}/K{k}"
                    temporary_send_back(file_path, granularity, shape)
                    permanent_send_back(file_path, granularity, shape)
