import random

import numpy as np
import matplotlib.pyplot as plt


def left_half_exponential(n):
    if n <= 0:
        raise ValueError("Input n must be a positive float")

    # Generate a random number from the exponential distribution
    lambda_param = 1.0 / n
    x = np.random.exponential(scale=1 / lambda_param)

    # Ensure the generated number is within the range [0, n]
    while x > n:
        x = np.random.exponential(scale=1 / lambda_param)

    # Get the left half of the distribution
    return n - x


if __name__ == '__main__':
    data = []
    alpha, beta = 5, 1
    for i in range(1000000):
        r = random.betavariate(alpha, beta)
        # while x > 60:
        #     x = np.random.exponential(scale=1 / lambda_param)

        data.append(r*60)
    count, bins, ignored = plt.hist(data, bins=1000, density=False)
    plt.show()
