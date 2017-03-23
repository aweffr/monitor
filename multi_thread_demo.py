import time, threading
from collections import deque


def loop():
    print("thread %s start running ..." % threading.current_thread().name)
    n = 0
    while n < 500:
        n += 100
        print("thread %s >>> %s" % (threading.current_thread().name, n))
        time.sleep(1)
    print("thread %s end." % threading.current_thread().name)


if __name__ == "__main__":
    t1 = threading.Thread(target=loop)
    t2 = threading.Thread(target=loop)

    t1.start()
    time.sleep(1)
    t2.start()
    t1.join()
    t2.join()
    print("Global End.")
