import os
import socket
import pickle
import threading
import time
import psutil
import stop
from config import Config
from constants import Constants
import worker
from utils import logger
from utils.com_socket import recv_msg
import sys


class SecondaryNode:
    def __init__(self, argv):
        self.sock = None
        self.start_time = 0
        self.dir_meta = ''
        self.processes = dict()
        self.should_stop = False
        self.failure_handler_thread = None
        self.cpu_util = []
        self.id = argv

    def _connect_to_primary(self):
        logger.info("Connecting to the primary node")

        self.sock = socket.socket()
        while True:
            try:
                self.sock.connect(Constants.SERVER_ADDRESS)
            except OSError:
                time.sleep(10)
                continue
            break

    def _wait_for_start_command(self):
        logger.info("Waiting for the start command from the primary node")

        start_cmd = recv_msg(self.sock)
        self.start_time, self.dir_meta = start_cmd

    def _handle_deployments(self):
        logger.info("Started deployment handler")

        while True:
            self.cpu_util.append((time.time(), psutil.cpu_percent()))

            msg = recv_msg(self.sock)
            logger.debug(msg)

            if not msg:
                break
            else:
                logger.debug(f"CREATE PROCESS fid={msg['fid']} time={time.time()}")
                default_failure_timeout = None
                if Config.SANITY_TEST >= 2:
                    default_failure_timeout = msg['fid'] * Config.STANDBY_TEST_CONFIG[2][1]
                p = worker.WorkerProcess(start_time=self.start_time, dir_meta=self.dir_meta,
                                         fail_timeout=default_failure_timeout,
                                         **msg)
                logger.debug(f"PROCESS_START fid={msg['fid']} time={time.time()}")
                p.start()
                self.processes[msg["fid"]] = p

    def _handle_failures(self):
        # to join the processes of failed FLSs
        error_handling_socket = worker.WorkerSocket()
        error_handling_socket.sock.settimeout(1)
        while self.should_stop:
            try:
                msg, _ = error_handling_socket.receive()
            except socket.timeout:
                continue

            if msg.fid in self.processes:
                self.processes.pop(msg.fid).join()

    def _start_failure_handler_thread(self):
        self.failure_handler_thread = threading.Thread(target=self._handle_failures)
        self.failure_handler_thread.start()

        logger.info("Started failure handler")

    def _stop_failure_handler_thread(self):
        self.should_stop = True
        self.failure_handler_thread.join()

    def _ack_primary_node(self):
        self.sock.sendall(pickle.dumps(True))

    def _stop_processes(self):
        logger.info(f"Stopping FLS processes {time.time()}")

        stop.stop_all()

        for p in self.processes.values():
            if p.is_alive():
                logger.debug(f"Process UNFINISHED: {p.name}")
                p.join(Config.PROCESS_JOIN_TIMEOUT)

        for p in self.processes.values():
            if p.is_alive():
                logger.debug(f"Process Alive: {p.name}")
                p.terminate()

    def _write_cpu_data(self, filename):
        with open(filename, 'w') as file:
            for data in self.cpu_util:
                file.write(f"{data[0]},{data[1]}\n")

    def start_node(self):
        self._connect_to_primary()
        self._wait_for_start_command()
        self._start_failure_handler_thread()
        self._handle_deployments()

    def stop_node(self):
        self._stop_failure_handler_thread()
        self._stop_processes()
        self._ack_primary_node()

        if not os.path.exists(f"{self.dir_meta}/cpu_util/"):
            os.makedirs(f"{self.dir_meta}/cpu_util/", exist_ok=True)

        self._write_cpu_data(f"{self.dir_meta}/cpu_util/{self.id}_cpu_util.txt")


if __name__ == '__main__':
    node = SecondaryNode(sys.argv[1:])
    node.start_node()
    node.stop_node()
