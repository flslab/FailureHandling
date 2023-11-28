from functools import partial

from find_obstructing_raybox import *
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
import matplotlib as mpl
from worker.metrics import TimelineEvents
from PIL import Image
from mpl_toolkits.mplot3d import Axes3D


def generate_animation(ptcld_folder, meta_direc, ratio, k, shape, granularity):
    output_path = f"{meta_direc}/obstructing/R{ratio}/K{k}"

    txt_file = f"{shape}.txt"
    standby_file = f"{shape}_standby.txt"
    standby_points = read_coordinates(f"{output_path}/points/{standby_file}", ' ', 1)

    illum_points = read_coordinates(f"{ptcld_folder}/{txt_file}", ' ')

    draw_shape(illum_points, standby_points, ratio)


def creat_figure():

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')



    user, = ax.plot([1], [1], [1], 'ro', alpha=0)

    return fig, ax, user


def draw_shape(fig, ax, illum_points, standby_points, Q):

    x_data = [point[0] for point in standby_points]
    y_data = [point[1] for point in standby_points]
    z_data = [point[2] for point in standby_points]

    ax.scatter(x_data, y_data, z_data, c="#929591", s=1, alpha=1)

    x_data = [point[0] * Q for point in illum_points]
    y_data = [point[1] * Q for point in illum_points]
    z_data = [point[2] * Q for point in illum_points]

    ax.scatter(x_data, y_data, z_data, c='blue', s=Q, alpha=1)

    # ax.view_init(elev=90, azim=-90)
    # ax.grid(False)
    #
    # ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    # ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    # ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    # ax.set_xticks([])
    # ax.set_yticks([])
    # ax.set_zticks([])
    # ax.xaxis.line.set_visible(False)
    # ax.yaxis.line.set_visible(False)
    # ax.zaxis.line.set_visible(False)
    # plt.show()


def init(ax):
    ax.view_init(elev=90, azim=-90)
    ax.grid(False)
    ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    ax.xaxis.line.set_visible(False)
    ax.yaxis.line.set_visible(False)
    ax.zaxis.line.set_visible(False)

def update(frame, ax, dot, fov):

    pass


def generate_video(fig, ax, user, fov, fps, duration):
    ani = FuncAnimation(
        fig, partial(update, ax, user, fov),
        frames=fps * duration,
        init_func=partial(init, ax))


if __name__ == "__main__":
    ptcld_folder = "/Users/shuqinzhu/Desktop/pointcloud"
    meta_dir = "/Users/shuqinzhu/Desktop"

    for ratio in [5]:
        for k in [3]:
            for shape in ["dragon"]:
                generate_animation(ptcld_folder, meta_dir, ratio, k, shape, 10)
