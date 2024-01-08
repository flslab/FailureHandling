import pandas as pd
import numpy as np
from collections import Counter


def kmeans(points, k, max_iterations=1000):
    centroids = points[np.random.choice(points.shape[0], k, replace=False)]
    iterations = {}
    for i in range(k):
        iterations[i] = -1

    for ite in range(max_iterations):
        # Assign each point to the nearest centroid
        distances = np.sqrt(((points - centroids[:, np.newaxis]) ** 2).sum(axis=2))
        group_id = np.argmin(distances, axis=0)

        # Compute new centroids from the mean of the points in the group
        new_centroids = np.array([points[group_id == i].mean(axis=0) for i in range(k)])
        
        exit_flag = True
        for i in range(len(new_centroids)):
            if iterations[i] < 0 and all(centroids[i] == new_centroids[i]):
                iterations[i] = ite
            elif iterations[i] < 0:
                exit_flag = False
        if exit_flag:
            return group_id, list(iterations.values())

        centroids = new_centroids

    return group_id, list(iterations.values())


def check_if_exhaust(file_path, k, max_iterations=1000):
    iterations = {}
    for i in range(k):
        iterations[i] = -1

    points, centroids = read_group_formation(file_path)

    for ite in range(max_iterations):
        # Assign each point to the nearest centroid
        distances = np.sqrt(((points - centroids[:, np.newaxis]) ** 2).sum(axis=2))
        closest_centroids = np.argmin(distances, axis=0)

        new_centroids = np.array([points[closest_centroids == i].mean(axis=0) for i in range(k)])

        exit_flag = True
        for i in range(len(new_centroids)):
            if iterations[i] < 0 and all(centroids[i] == new_centroids[i]):
                iterations[i] = ite
            elif iterations[i] < 0:
                exit_flag = False
        if exit_flag:
            return list(iterations.values())

    return list(iterations.values())


def read_group_formation(file_path):
    df = pd.read_excel(file_path)

    centers = []
    points = []
    for index, row in df.iterrows():
        coordinates = eval(row['7 coordinates'])

        coordinates_array = np.array(coordinates)

        center = np.mean(coordinates_array, axis=0)
        centers.append(center)
        points.extend(coordinates_array)

    return np.array(points), np.array(centers)


if __name__ == "__main__":
    # k = 253

    group_info = [["skateboard_G3", 576], ["skateboard_G20", 86], ["dragon_G3", 253], ["dragon_G20", 38], ["hat_G3", 521], ["hat_G20", 78]]

    for info in group_info:
        k = info[1]
        file_path = f"../assets/pointcloud/{info[0]}.xlsx"
        points, _ = read_group_formation(file_path)
        _, iterations = kmeans(points, k)

        # iterations = check_if_exhaust(file_path, k)
        print(info[0], max(iterations))

    # points = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9],
    #                    [5.49, 7.15, 6.03], [5.49, 7.15, 6.03], [5.45, 4.24, 6.46], [5.45, 4.24, 6.46], [4.38, 8.92, 9.64],
    #                    [4.38, 8.92, 9.64],
    #                    [3.83, 7.92, 5.29], [3.83, 7.92, 5.29], [5.68, 9.26, 0.71], [5.68, 9.26, 0.71], [0.87, 0.20, 8.33],
    #                    [0.87, 0.20, 8.33],
    #                    [7.78, 8.70, 9.79], [7.78, 8.70, 9.79], [7.99, 4.61, 7.81], [7.99, 4.61, 7.81], [1.18, 6.40, 1.43],
    #                    [1.18, 6.40, 1.43],
    #                    [9.45, 5.22, 4.15], [9.45, 5.22, 4.15]])
    # k = 3  # Number of clusters
    # centroids, assignments = kmeans(points, k)
    #
    # print("Centroids:", centroids)
    # print("Assignments:", assignments)
