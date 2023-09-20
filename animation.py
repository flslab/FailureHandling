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

start_time = 0
duration = 180
fps = 30
frame_rate = 1 / fps
total_points = 11888

# t30_d1_g0	t30_d1_g20	t30_d5_g0	t30_d5_g20	t600_d1_g0	t600_d1_g20	t600_d5_g0	t600_d5_g20
output_name = "testd"
input_path = f"/Users/hamed/Desktop/{output_name}/timeline.json"


def set_axis(ax, length, width, height):
    ax.axes.set_xlim3d(left=0, right=length)
    ax.axes.set_ylim3d(bottom=0, top=width)
    ax.axes.set_zlim3d(bottom=0, top=height)
    ax.set_aspect('equal')
    ax.grid(False)
    ax.set_xticks(range(0, length + 1, ticks_gap))
    ax.set_yticks(range(0, width + 1, ticks_gap))
    ax.set_zticks(range(0, height + 1, ticks_gap))


def set_text(tx, t, missing_flss):
    tx.set(text=f"Elapsed time: {int(t)} seconds\nNumber of missing FLSs: {missing_flss}")


def draw_figure():
    px = 1 / plt.rcParams['figure.dpi']
    fig_width = 1280 * px
    fig_height = 720 * px
    fig = plt.figure(figsize=(fig_width, fig_height))
    ax = fig.add_subplot(projection='3d')
    tx = fig.text(0.1, 0.8, s="", fontsize=16)
    line1 = ax.scatter([], [], [])
    return fig, ax, tx


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


def init(ax):
    ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax.zaxis.set_pane_color((0, 0, 0, 0.025))
    ax.view_init(elev=14, azim=136, roll=0)
    # return line1,


def update(frame):
    t = start_time + frame * frame_rate
    while len(filtered_events):
        # print(t)
        event_time = filtered_events[0][0]
        if event_time <= t:
            event = filtered_events.pop(0)
            event_type = event[1]
            fls_id = event[-1]
            if event_type == TimelineEvents.ILLUMINATE or event_type == TimelineEvents.ILLUMINATE_STANDBY:
                points[fls_id] = event[2]
            else:
                points.pop(fls_id)
        else:
            t += frame_rate
            break
    coords = points.values()
    ax.clear()
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    zs = [c[2] for c in coords]
    ln = ax.scatter(xs, ys, zs, c='blue', s=2, alpha=1)
    set_axis(ax, length, width, height)
    set_text(tx, t, total_points - len(coords))
    return ln,


def show_last_frame(events, t=30):
    final_points = dict()
    for event in events:
        event_time = event[0]
        if event_time > t:
            break
        event_type = event[1]
        fls_id = event[-1]
        if event_type == TimelineEvents.ILLUMINATE or event_type == TimelineEvents.ILLUMINATE_STANDBY:
            final_points[fls_id] = event[2]
        else:
            try:
                final_points.pop(fls_id)
            except Exception as e:
                continue

    coords = final_points.values()
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    zs = [c[2] for c in coords]

    return xs, ys, zs


def draw_last_frame(result_path, fig_name, end_time):
    input_path = result_path + "/timeline.json"
    filtered_events, length, width, height = read_point_cloud(input_path)
    fig, ax, _ = draw_figure()
    init(ax)
    xs, ys, zs = show_last_frame(filtered_events, t=end_time)
    ax.scatter(xs, ys, zs, c='blue', s=2, alpha=1)
    set_axis(ax, length, width, height)
    plt.savefig(f"{result_path}/{fig_name}.png")
    plt.close()


def trim_png(image_path, output_path, trim_values):
    try:
        # Open the image file
        with Image.open(image_path) as img:
            # Get the dimensions of the image
            width, height = img.size

            # Calculate the new dimensions
            left = trim_values[0]
            top = trim_values[1]
            right = width - trim_values[2]
            bottom = height - trim_values[3]

            # Check if the trim values are valid
            if left >= right or top >= bottom:
                raise ValueError("Invalid trim values, resulting in non-positive width or height.")

            # Crop the image
            img_cropped = img.crop((left, top, right, bottom))

            # Save the cropped image
            img_cropped.save(output_path)

            print(f"The image has been trimmed and saved to {output_path}")
    except FileNotFoundError:
        print(f"The file at path {image_path} does not exist.")
    except ValueError as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



if __name__ == '__main__':
    # mpl.use('macosx')
    #
    # filtered_events, length, width, height = read_point_cloud(input_path)
    # fig, ax, tx = draw_figure()
    # points = dict()
    # ani = FuncAnimation(
    #     fig, partial(update,),
    #     frames=30 * duration,
    #     init_func=partial(init, ax))
    # #
    # # plt.show()
    # writer = FFMpegWriter(fps=fps)
    # ani.save(f"results/{output_name}.mp4", writer=writer)
    # exit()
    configs = [
        {
            "keys": ["K"],
            "values": ["0", "3"]
        },
        {
            "keys": ["D"],
            "values": ["5"]
        },
        {
            "keys": ["R"],
            "values": ["1", "inf"]
        },
        {
            "keys": ["T"],
            "values": ["30", "120"]
        }
    ]

    # props_values = [p["values"] for p in configs]
    # combinations = list(itertools.product(*props_values))
    # # print(combinations)
    #
    # exp_dir = "/Users/hamed/Desktop/chess_30_min"
    #
    # for c in combinations:
    #     exp_name = f"chess_K{c[0]}_D{c[1]}_R{c[2]}_T{c[3]}"
    #     print(exp_name)
    #     input_path = f"{exp_dir}/{exp_name}/timeline.json"
    #     filtered_events, length, width, height = read_point_cloud(input_path)
    #     fig, ax, _ = draw_figure()
    #     init(ax)
    #     xs, ys, zs = show_last_frame(filtered_events, t=1799)
    #     ax.scatter(xs, ys, zs, c='blue', s=2, alpha=1)
    #     set_axis(ax, length, width, height)
    #     plt.show()
    #     # plt.savefig(f"{exp_dir}/{exp_name}.png")
    #     plt.close()
    #     # break
    # exit()
    # for c in combinations:
    #     exp_name = f"chess_K{c[0]}_D{c[1]}_R{c[2]}_T{c[3]}"
    #     input_path = f"{exp_dir}/{exp_name}/timeline.json"
    #     filtered_events, length, width, height = read_point_cloud(input_path)
    #     fig, ax, tx = draw_figure()
    #     points = dict()
    #     ani = FuncAnimation(
    #         fig, partial(update,),
    #         frames=30 * duration,
    #         init_func=partial(init, ax))
    #     #
    #     # plt.show()
    #     writer = FFMpegWriter(fps=fps)
    #     ani.save(f"{exp_dir}/{exp_name}.mp4", writer=writer)




    for folder in ["K3", "K5", "K10", "K20"]:
        for filename in ["real", "match", 'child']:
            input_path = f"/Users/shuqinzhu/Desktop/racecar_R350_pri/{folder}/racecar_D1_R350_T30_S6_N{filename}_pri/timeline.json"
            # input_path = f"/Users/shuqinzhu/Desktop/timeline.json"
            filtered_events, length, width, height = read_point_cloud(input_path)
            fig, ax, _ = draw_figure()
            init(ax)
            xs, ys, zs = show_last_frame(filtered_events, t=800)
            ax.scatter(xs, ys, zs, c='blue', s=2, alpha=1)
            set_axis(ax, length, width, height)
            # ax.view_init(elev=90, azim=-90)
            # plt.show()
            # plt.savefig(f"/Users/shuqinzhu/Desktop/K3_toy_inf.png")
            # image_path = "/Users/shuqinzhu/Desktop/K3_toy_inf.png"
            # output_path = "/Users/shuqinzhu/Desktop/K3_toy_inf.png"
            # trim_values = [375, 200, 300, 120]  # Replace with the number of pixels to trim from each side (left, top, right, bottom)
            # trim_png(image_path, output_path, trim_values)
            #
            plt.savefig(f"/Users/shuqinzhu/Desktop/exp_figure/racecar_pri/{folder}_{filename}_pri.png")
            image_path = f"/Users/shuqinzhu/Desktop/exp_figure/racecar_pri/{folder}_{filename}_pri.png"  # Replace with the path to your PNG file
            output_path = f"/Users/shuqinzhu/Desktop/exp_figure/racecar_pri/{folder}_{filename}_pri.png"  # Replace with the path to save the trimmed image
            trim_values = [360, 232, 306, 155]  # Replace with the number of pixels to trim from each side (left, top, right, bottom)
            trim_png(image_path, output_path, trim_values)
