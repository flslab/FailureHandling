import queue
import threading
import time
from multiprocessing import Process

from worker import WorkerProcess
from utils import logger

class Dispatcher(threading.Thread):
    def __init__(self, q, r, coord):
        super(Dispatcher, self).__init__()
        self.q = q
        self.r = r
        self.delay = 1 / r if isinstance(r, int) else 0
        self.coord = coord
        self.should_stop = False
        self.num_dispatched = 0
        self.time_q = queue.Queue()
        self.delay_list = []

    def run(self):
        while not self.should_stop:
            try:
                item = self.q.get(timeout=1)
                enque_time = self.time_q.get()
            except queue.Empty:
                continue
            if isinstance(item, WorkerProcess):
                item.start()
            elif callable(item):
                try:
                    item()
                except BrokenPipeError:
                    continue

            que_delay = time.time() - enque_time
            self.delay_list.append(que_delay)

            if self.delay:
                time.sleep(self.delay)

    def stop(self):
        self.should_stop = True


def create_process():
    return Process(target=time.sleep, args=(1,))


if __name__ == '__main__':
    # test
    q = queue.Queue()
    processes = dict()
    d = Dispatcher(q, 1, [1, 1, 1])
    d.start()
    p = create_process()
    processes[1] = p
    p2 = create_process()
    processes[2] = p2
    q.put(p)
    q.put(p2)
    print(q.qsize())
    time.sleep(1)
    processes[1].join()
    time.sleep(5)
    processes[1].join()
    q.put(False)
    d.join()
