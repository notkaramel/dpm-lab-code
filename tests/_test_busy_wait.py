import time, threading
from typing import List

def busy_sleep(seconds: float):
    """A different form of time.sleep, which uses a while loop that 
    constantly checks the time, to see if the duration has elapsed."""
    start = time.time()
    while (time.time() - start) < seconds:
        time.sleep(0.005)
    end = time.time()
    print(end-start, start, end)

if __name__=='__main__':
    thread_count = 10000
    ls:List[threading.Thread] = []
    for i in range(thread_count):
        t = threading.Thread(target=busy_sleep, args=(5,), daemon=True)
        ls.append(t)
    for t in ls:
        t.start()
    for t in ls:
        t.join()