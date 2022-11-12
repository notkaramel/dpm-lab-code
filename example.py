import threading
import time

class AtomicActor:
    def __init__(self):
        self.__atomic_lock = threading.RLock()

    def __atomic(func):
        def inner(*args, **kwargs):
            if len(args) == 0 or not isinstance(args[0], AtomicActor):
                raise RuntimeError("atomic decorator must be applied to a subclass of itself")
            self = args[0]
            with self.__atomic_lock:
                return func(*args, **kwargs)
        return inner

class SlowActor(AtomicActor):
    def __init__(self):
        super(SlowActor, self).__init__()
        self.i = 0

    @AtomicActor._AtomicActor__atomic
    def do(self, seconds=3):
        self.i += 1
        time.sleep(seconds)
        print("done", self.i)

if __name__=='__main__':
    slow = SlowActor()
    def func():
        slow.do()
    t1 = threading.Thread(target=func, daemon=True)
    t2 = threading.Thread(target=func, daemon=True)
    t3 = threading.Thread(target=func, daemon=True)

    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()
