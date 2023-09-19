import random
import numpy as np

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


fail_time = []
for i in range(100000):
    fail_time.append(left_half_exponential(30))

print(sum(fail_time)/len(fail_time))

