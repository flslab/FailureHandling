from moviepy.editor import VideoFileClip
import numpy as np

# Load the video file
clip = VideoFileClip("/Users/shuqinzhu/Desktop/video/videos/hat_G{0,3}_R3000_T900_S66.mp4")

# Get the size of the video
width, height = clip.size


def add_vertical_line(frame):
    frame = np.copy(frame)
    x = width // 2
    y1 = 0
    y2 = int(height * 0.9)

    # Draw the line on the frame
    frame[y1:y2, x - 1:x + 1] = [255, 255, 255]  # RGB white color

    return frame


new_clip = clip.fl_image(add_vertical_line)

new_clip.write_videofile("/Users/shuqinzhu/Desktop/video/hat_G{0,3}_R3000_T900_S66_line.mp4", codec='libx264')
