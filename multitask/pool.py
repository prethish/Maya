from multiprocessing import JoinableQueue
from multiprocessing import TimeoutError
import multiprocessing as mp
import queue
import logging

from multitask.pool_worker import PoolWorker
from multitask import constants

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class Pool(object):
    def __init__(self, n_workers=None):
        self.n_workers = n_workers or mp.cpu_count()
        self._work_queue = JoinableQueue()
        self._workers = []
        self._process_pipes = []
        self._func_list = []
        for id in range(n_workers):
            parent_conn, child_conn = mp.Pipe()
            thr = PoolWorker(self._work_queue, child_conn)
            thr.start()
            self._process_pipes.append(parent_conn)
            self._workers.append(thr)
        logger.info("Started %s Threads" % n_workers)

    def join(self):
        logger.debug("Waiting for all threads to complete.")
        for thr in self._workers:
            self._work_queue.put(constants.KILL_CMD)
        for thr in self._workers:
            thr.join()

    def wait(self):
        logger.debug("Starting Wait to finish current queue.")
        self._work_queue.join()

    def terminate(self):
        logger.debug("Terminating all threads")
        try:
            while True:
                self._work_queue.get_nowait()
        except queue.Empty:
            logger.debug("Queue is Empty")

        for thr in self._workers:
            self._work_queue.put(constants.KILL_CMD)
    
    def current_process_status(self):
        statuses = []
        for process, pipe in zip(self._workers, self._process_pipes):
            if not process.is_alive():
                continue
            proc_info = {
                "name": process.name,
                "pid": process.pid,
                "task": "UNDEF",
            }

            pipe.send("all")
            if pipe.poll():
                try:
                    recieved = pipe.recv()
                    proc_info.update(recieved)
                except EOFError:
                    logger.warn("PIPE closed")
            statuses.append(proc_info)
        return statuses
    
    def add_task(self, *args, **kwargs):
        args = list(args)
        func = args.pop(0)
        self._work_queue.put(
            (func, args, kwargs)
        )
        logger.debug("Added %s job with %s", func, args)
        return True


            
            