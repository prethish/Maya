import multiprocessing as mp
from multiprocessing import Process
from queue import Empty
import logging

from multitask import constants, utils


logger = logging.getLogger(__name__)


class PoolWorker(Process):

    def __init__(self, queue, msg_pipe, name=None):
        super(PoolWorker, self).__init__()
        self._queue = queue
        self._pname = name
        self._msg_pipe = msg_pipe
        self._state = 'UNDEF'
        self._start_event()

    def _start_event(self):
        self._state = "ACTIVE"
        self._send_msg(
            {
                "status": self._state,
                "metadata": "memory:%s" % utils.memory_usage()
            }
        )

    def _shutdown(self, msg=None):
        self._msg_pipe.close()

    def _send_msg(self, msg):
        self._msg_pipe.send(msg)
    
    def _check_msg(self):
        recieved = None
        if self._msg_pipe.poll():
            try:
                recieved = self._msg_pipe.recv()
            except EOFError:
                logger.warn("PIPE to %s closed", self._name)

        if recieved:
            self._send_msg(
                {
                    "status": self._state,
                    "metadata": "memory:%s" % utils.memory_usage()
                }
            )

    def run(self):
        while True:
            # Check for incoming messages
            # ideally this should be done in
            # a seperate thread which pools for 
            # incoming messages.
            self._check_msg()
            try:
                current_task = self._queue.get()
                if current_task == constants.KILL_CMD:
                    self._state = "KILLED"
                    break
            except Empty:
                self._state = "IDLE"
                continue
            #Unpack
            try:
                func = current_task[0]
                args = current_task[1]
                kwargs = current_task[2]
            except IndexError:
                logger.info("Invalid task send to Process")

            #Run
            try:
                self._state = "BUSY"
                func(*args, **kwargs)
            except Exception as e:
                self._send_msg(
                    "%s has errored with %s" %(func, str(e))
                )
            self._state = "ACTIVE"

        self._shutdown()
    



