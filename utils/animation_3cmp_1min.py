import itertools
import json
import math
from functools import partial

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import matplotlib as mpl
from worker.metrics import TimelineEvents
from PIL import Image

ticks_gap = 20

start_time = 900
duration = 60
fps = 30
frame_rate = 1 / fps
total_points = 760

# t30_d1_g0	t30_d1_g20	t30_d5_g0	t30_d5_g20	t600_d1_g0	t600_d1_g20	t600_d5_g0	t600_d5_g20
output_name = "testd"
input_path = f"/Users/hamed/Desktop/{output_name}/timeline.json"


def set_axis(ax, length, width, height, title=""):
    ax.axes.set_xlim3d(left=0, right=length)
    ax.axes.set_ylim3d(bottom=0, top=width)
    ax.axes.set_zlim3d(bottom=0, top=height)
    ax.set_aspect('equal')
    ax.grid(False)
    ax.set_xticks(range(0, length + 1, ticks_gap))
    ax.set_yticks(range(0, width + 1, ticks_gap))
    ax.set_zticks(range(0, height + 1, ticks_gap))
    ax.set_title(title, y=.9)


def set_axis_2d(ax, length, width, title):
    ax.axes.set_xlim(0, length)
    ax.axes.set_ylim(0, width)
    ax.set_aspect('equal')
    ax.grid(False)
    ax.axis('off')
    ax.set_title(title)


def update_title(ax, title, missing_flss):
    ax.set_title(f"{title}\nNumber of missing FLSs: {missing_flss}", y=.9)


def set_text_left(tx, t, missing_flss):
    tx.set(text=f"Number of missing FLSs: {missing_flss}")


def set_text_right(tx, t, missing_flss):
    tx.set(text=f"Number of missing FLSs: {missing_flss}")


def set_text_time(tx, t):
    tx.set(text=f"Elapsed time: {int(t)} seconds")


def draw_figure():
    px = 1 / plt.rcParams['figure.dpi']
    fig_width = 1920 * px
    fig_height = 1080 * px
    fig = plt.figure(figsize=(fig_width, fig_height))
    spec = fig.add_gridspec(2, 9, left=0.04, right=0.96, top=0.92, bottom=0.08)
    ax = fig.add_subplot(spec[0:2, 0:3], projection='3d', proj_type='ortho')
    ax1 = fig.add_subplot(spec[0:2, 3:6], projection='3d', proj_type='ortho')
    ax2 = fig.add_subplot(spec[0:2, 6:9], projection='3d', proj_type='ortho')

    tx_left = fig.text(0.15, 0.88, s="", fontsize=16)
    tx_right = fig.text(0.05, 0.88, s="", fontsize=16)

    tx_time = fig.text(0.43, 0.88, s="", fontsize=16)
    return fig, ax, ax1, ax2, tx_left, tx_right, tx_time


def read_point_cloud(input_path):
    with open(input_path) as f:
        events = json.load(f)

    height = 0
    width = 0
    length = 0
    filtered_events = []
    for e in events:
        if e[1] == TimelineEvents.FAIL and e[2] is False:
            filtered_events.append(e)
        elif e[1] == TimelineEvents.ILLUMINATE or e[1] == TimelineEvents.ILLUMINATE_STANDBY:
            filtered_events.append(e)
            length = max(int(e[2][0]), length)
            width = max(int(e[2][1]), width)
            height = max(int(e[2][2]), height)
    length = math.ceil(length / ticks_gap) * ticks_gap
    width = math.ceil(width / ticks_gap) * ticks_gap
    height = math.ceil(height / ticks_gap) * ticks_gap

    return filtered_events, length, width, height


def init(ax, ax1, ax2):
    ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax.zaxis.set_pane_color((0, 0, 0, 0.025))
    ax.view_init(elev=14, azim=-136, roll=0)

    ax1.xaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax1.yaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax1.zaxis.set_pane_color((0, 0, 0, 0.025))
    ax1.view_init(elev=14, azim=-136, roll=0)

    ax2.xaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax2.yaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax2.zaxis.set_pane_color((0, 0, 0, 0.025))
    ax2.view_init(elev=14, azim=-136, roll=0)
    # return line1,


def update(frame, names):
    t_left = start_time + frame * frame_rate
    t_center = start_time + frame * frame_rate
    t_right = start_time + frame * frame_rate
    while len(filtered_events_left):
        # print(t)
        event_time = filtered_events_left[0][0]
        if event_time <= t_left:
            event = filtered_events_left.pop(0)
            event_type = event[1]
            fls_id = event[-1]
            if event_type == TimelineEvents.ILLUMINATE or event_type == TimelineEvents.ILLUMINATE_STANDBY:
                points_left[fls_id] = event[2]
            else:
                if fls_id in points_left:
                    points_left.pop(fls_id)
        else:
            t_left += frame_rate
            break
    coords_left = points_left.values()
    ax.clear()
    xs = [c[0] for c in coords_left]
    ys = [c[1] for c in coords_left]
    zs = [c[2] for c in coords_left]

    ax.clear()
    ln = ax.scatter(xs, ys, zs, c='purple', s=2, alpha=1)
    set_axis(ax, length, width, height)

    update_title(ax, names[0], total_points - len(coords_left))
    # set_text_left(tx_left, t, total_points - len(coords_left))
    while len(filtered_events_center):
        # print(t)
        event_time = filtered_events_center[0][0]
        if event_time <= t_center:
            event = filtered_events_center.pop(0)
            event_type = event[1]
            fls_id = event[-1]
            if event_type == TimelineEvents.ILLUMINATE or event_type == TimelineEvents.ILLUMINATE_STANDBY:
                points_center[fls_id] = event[2]
            else:
                if fls_id in points_center:
                    points_center.pop(fls_id)
        else:
            t_center += frame_rate
            break
    coords_center = points_center.values()
    ax1.clear()
    xs = [c[0] for c in coords_center]
    ys = [c[1] for c in coords_center]
    zs = [c[2] for c in coords_center]

    ax1.clear()
    ln1 = ax1.scatter(xs, ys, zs, c='purple', s=2, alpha=1)
    set_axis(ax1, length, width, height)
    update_title(ax1, names[1], total_points - len(coords_center))

    set_text_time(tx_time, t_left)

    while len(filtered_events_right):
        # print(t)
        event_time = filtered_events_right[0][0]
        if event_time <= t_right:
            event = filtered_events_right.pop(0)
            event_type = event[1]
            fls_id = event[-1]
            if event_type == TimelineEvents.ILLUMINATE or event_type == TimelineEvents.ILLUMINATE_STANDBY:
                points_right[fls_id] = event[2]
            else:
                if fls_id in points_right:
                    points_right.pop(fls_id)
        else:
            t_right += frame_rate
            break
    coords_right = points_right.values()
    ax2.clear()
    xs = [c[0] for c in coords_right]
    ys = [c[1] for c in coords_right]
    zs = [c[2] for c in coords_right]

    ax2.clear()
    ln2 = ax2.scatter(xs, ys, zs, c='purple', s=2, alpha=1)
    set_axis(ax2, length, width, height)
    update_title(ax2, names[2], total_points - len(coords_right))
    # set_text_right(tx_right, t, total_points - len(coords_right))

    set_text_time(tx_time, t_left)

    return [ln, ln1, ln2]


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


if __name__ == '__main__':
    titles = ["No Standby", "G=3", "G=20"]
    shape = "skateboard"
    start_time = 1800
    file_names = ["skateboard_G0_R3000_T900_S66", "skateboard_G3_R3000_T900_S66", "skateboard_G20_R3000_T900_S66"]
    video_name = "skateboard_G{0,3,20}_R3000_T900_S66"

    txt_file_path = f"/Users/shuqinzhu/Desktop/video/pointclouds/{shape}.txt"
    gtl = read_coordinates(txt_file_path)
    print(f"Number of Points: {len(gtl)}")

    total_points = len(gtl)

    input_path_left = f"/Users/shuqinzhu/Desktop/video/timelines/{file_names[0]}.json"
    filtered_events_left, length, width, height = read_point_cloud(input_path_left)

    input_path_center = f"/Users/shuqinzhu/Desktop/video/timelines/{file_names[1]}.json"
    filtered_events_center, length, width, height = read_point_cloud(input_path_center)

    input_path_right = f"/Users/shuqinzhu/Desktop/video/timelines/{file_names[2]}.json"
    filtered_events_right, length, width, height = read_point_cloud(input_path_right)
    fig, ax, ax1, ax2, tx_left, tx_right, tx_time = draw_figure()
    points_left = dict()
    points_center = dict()
    points_right = dict()

    ani = FuncAnimation(
        fig, partial(update, names=titles),
        frames=fps * duration,
        init_func=partial(init, ax, ax1, ax2))
    #
    # plt.show()
    writer = FFMpegWriter(fps=fps)
    # ani.save(f"{exp_dir}/{exp_name}.mp4", writer=writer)
    ani.save(f"/Users/shuqinzhu/Desktop/video/videos/{video_name}.mp4", writer=writer)
