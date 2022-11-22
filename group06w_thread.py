import threading
import time
import numpy as np


def thread_function(name, seed, cycles):
    rng = np.random.default_rng(seed)
    val = 0
    for i in range(cycles):
        rand_num = rng.integers(low=0, high=10, size=1)
        val = val + 0.1*rand_num[0]
        print("Thread %1d: %1.2f" % (name, val))
        time.sleep(2)


if __name__ == "__main__":
    x = threading.Thread(target=thread_function, args=(1, 1, 10))
    y = threading.Thread(target=thread_function, args=(2, 2, 10))
    z = threading.Thread(target=thread_function, args=(3, 3, 10))
    x.start()
    y.start()
    z.start()
    # x.join()
