"""The controller is the interface for quering the pool
"""
from multitask import pool


class MultiProcessManager(object):
    def __init__(self, n_process=None):
        self._n_process = n_process
        self._pool = pool.Pool(n_process)
    
    def get_update(self):
        return self._pool.current_process_status()
    
    def add_task_to_queue(self, *args, **kwargs):
        self._pool.add_task(*args, **kwargs)
    
    def stop(self):
        self._pool.join()
    
    def kill(self):
        self._pool.terminate()
