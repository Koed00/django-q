import time

# simple countdown
def count(n):
    start_time = time.time()
    while n > 0:
        n -= 1
    stop_time = time.time()
    return stop_time - start_time
