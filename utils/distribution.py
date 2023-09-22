import random

import numpy as np
import matplotlib.pyplot as plt


def left_half_exponential(n):
    alpha, beta = 10, 0.8
    return random.betavariate(alpha, beta) * n


if __name__ == '__main__':
    data = []
    alpha, beta = 10, 0.8
    for i in range(1000000):
        r = random.betavariate(alpha, beta)
        # while x > 60:
        #     x = np.random.exponential(scale=1 / lambda_param)

        data.append(r * 60)
    count, bins, ignored = plt.hist(data, bins=100, density=False)
    print(np.mean(data))
    plt.show()
