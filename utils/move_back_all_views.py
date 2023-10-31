import csv

from solve_obstructing import solve_single_view, get_points
from obstructing_FLSs import calculate_single_view
import multiprocessing as mp


def solve_all_views(group_file, meta_direc, ratio, k, shape):

    result_find = [
        ["Shape", "K", "Ratio", "View", "Visible_Illum", "Obstructing FLS"]]

    result_solve = [[
        "Shape", "K", "Ratio", "View",
        "Min Dist Illum", "Max Dist Illum", "Avg Dist Illum",
        "Min Dist Standby", "Max Dist Standby", "Avg Dist Standby",
        "Moved Illuminating FLSs",
        "Min Dist Between", "Max Dist Between", "Avg Dist Between",
        "Min Obstructing FLSs", "Max Obstructing FLSs", "Avg Obstructing FLSs",
        "Min Ori Dist To Center", "Max Ori Dist To Center", "Avg Ori Dist To Center", "Origin MTID",
        "Min Dist To Center", "Max Dist To Center", "Avg Dist To Center", "MTID",
        "Dist To Center Change", "MTID Change", "Obstructing Nums"]]

    report_path = f"{meta_direc}/obstructing/R{ratio}"

    output_path = f"{meta_direc}/obstructing/R{ratio}/K{k}"

    txt_file = f"{shape}.txt"
    standby_file = f"{shape}_standby.txt"
    points, boundary, standbys = get_points(ratio, group_file, output_path, txt_file, standby_file)

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

    views = ["top", "bottom", "left", "right", "front", "back", "top"]
    # views = ["top"]

    for i in range(len(views)):

        view = views[i]
        camera = cam_positions[i]

        txt_file = f"{shape}.txt"
        standby_file = f"{shape}_{views[i-1]}_standby.txt" if i > 1 else f"{shape}_standby.txt"
        points, boundary, standbys = get_points(ratio, group_file, output_path, txt_file, standby_file)

        metrics_find = calculate_single_view(shape, k, ratio, view, points, camera, output_path)
        result_find.append(metrics_find)

        metrics_solve = solve_single_view(shape, k, ratio, view, views[i - 1] if i > 1 else "origin", camera,
                                          group_file, output_path)

        result_solve.append(metrics_solve)

    view = views[0]
    camera = cam_positions[0]

    txt_file = f"{shape}.txt"
    standby_file = f"{shape}_{views[-1]}_standby.txt"
    points, boundary, standbys = get_points(ratio, group_file, output_path, txt_file, standby_file)

    metrics_find = calculate_single_view(shape, k, ratio, view, points, camera, output_path)
    result_find.append(metrics_find)

    with open(f'{report_path}/report_find_R{ratio}_K{k}_{shape}.csv', mode='w', newline='') as file:
        writer = csv.writer(file)

        # Write the data from the list to the CSV file
        for row in result_find:
            writer.writerow(row)

    with open(f'{report_path}/report_solve_R{ratio}_K{k}_{shape}.csv', mode='w', newline='') as file:
        writer = csv.writer(file)

        # Write the data from the list to the CSV file
        for row in result_solve:
            writer.writerow(row)



if __name__ == "__main__":

    # file_folder = "/Users/shuqinzhu/Desktop/pointcloud"
    # meta_dir = "/Users/shuqinzhu/Desktop"

    file_folder = "/users/Shuqin/pointcloud"
    meta_dir = "/users/Shuqin"

    p_list = []
    for illum_to_disp_ratio in [1, 3, 5, 10]:

        for k in [3, 20]:

            for shape in ["skateboard", "dragon", "hat"]:
                # solve_all_views(file_folder, meta_dir, illum_to_disp_ratio, k, shape)
                p_list.append(mp.Process(target=solve_all_views, args=(file_folder, meta_dir, illum_to_disp_ratio, k, shape)))

    for p in p_list:
        print(p)
        p.start()
