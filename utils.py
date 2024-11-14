# utils.py

import time


def measure_time(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            print(f"{func.__name__} tomó {(end_time - start_time) * 1000:.2f} ms")
            return result
        return wrapper