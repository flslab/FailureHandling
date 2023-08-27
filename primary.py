import math
import queue
import socket
import random
import threading
import sys
import time
import os
from abc import ABC, abstractmethod
import numpy as np

from dispatcher import Dispatcher
from test_config import TestConfig
from config import Config
from constants import Constants
from message import Message, MessageTypes
import worker
import utils
from utils import logger
from utils.file import read_cliques_xlsx, get_group_mapping
from utils.socket import send_msg
from utils.generate_circle_coord import generate_circle_coordinates
from utils.sanity_metrics import *
from utils.report import *
from random import choice

from worker.metrics import point_to_id

CONFIG = TestConfig if TestConfig.ENABLED else Config


def join_config_properties(conf, props):
    return "_".join(
        f"{k[1] if isinstance(k, tuple) else k}{int(getattr(conf, k[0] if isinstance(k, tuple) else k)) if isinstance(getattr(conf, k[0] if isinstance(k, tuple) else k), float) else getattr(conf, k[0] if isinstance(k, tuple) else k)}"
        for k in
        props)


class DispatchPolicy(ABC):
    @abstractmethod
    def assign(self, **kwargs):
        pass


class PoDPolicy(DispatchPolicy):
    def assign(self, **kwargs):
        ds = kwargs["dispatchers"]

        if len(ds) == 1:
            return ds[0]
        elif len(ds) == 2:
            if ds[0].q.qsize() < ds[1].q.qsize():
                return ds[0]
            return ds[1]

        rand_ds = random.sample(ds, 2)
        if rand_ds[0].q.qsize() < rand_ds[1].q.qsize():
            return rand_ds[0]
        return rand_ds[1]


class RRPolicy(DispatchPolicy):
    def assign(self, **kwargs):
        ds = kwargs["dispatchers"]
        pid = kwargs["pid"]

        return ds[pid % len(ds)]


class ShortestDistancePolicy(DispatchPolicy):
    def assign(self, **kwargs):
        ds = kwargs["dispatchers"]
        coord = kwargs["gtl"]

        dispatcher_coords = np.stack([d.coord for d in ds])
        return ds[np.argmin(np.linalg.norm(dispatcher_coords - coord, axis=1))]


class PrimaryNode:
    def __init__(self, N, name):
        self.N = N  # number of secondary servers
        self.name = name
        self.sock = None
        self.failure_handler_socket = None
        self.client_sockets = []
        self.result_name = None
        self.dir_experiment = None
        self.dir_meta = None
        self.dir_figure = None
        self.start_time = 0
        self.end_time = 0
        self.dispatchers_coords = []
        self.dispatchers = []
        self.groups = []
        self.radio_ranges = []
        self.group_members = {}
        self.group_standby_id = {}
        self.group_standby_coord = {}
        self.group_radio_range = {}
        self.pid = 0
        self.dispatch_policy = ShortestDistancePolicy()
        self.num_handled_failures = 0
        self.num_initial_flss = 0
        self.num_initial_standbys = 0
        self.num_replaced_flss = 0
        self.num_replaced_standbys = 0
        self.stop_flag = False
        self.stop_thread = None
        self.center = []
        self.init_num = 0

    def _create_server_socket(self):
        # Experimental artifact to gather theoretical stats for scientific publications.
        self.sock = socket.socket()

    def _bind_server_socket(self):
        logger.info(f"Binding primary node to {Constants.SERVER_ADDRESS}")

        while True:
            try:
                self.sock.bind(Constants.SERVER_ADDRESS)
            except OSError:
                time.sleep(10)
                continue
            break

    def _listen_to_secondary_nodes(self):
        logger.info("Waiting for secondary nodes to connect")

        self.sock.listen(N)
        for i in range(N):
            client, address = self.sock.accept()
            logger.debug(address)
            self.client_sockets.append(client)

    def _setup_results_directory(self):
        if len(CONFIG.FILE_NAME_KEYS):
            result_config = join_config_properties(CONFIG, CONFIG.FILE_NAME_KEYS)
        else:
            result_config = self.name
        self.result_name = f"{Config.SHAPE}_{result_config}"

        if len(CONFIG.DIR_KEYS):
            group_config = join_config_properties(CONFIG, CONFIG.DIR_KEYS)
        else:
            group_config = ""

        self.dir_experiment = os.path.join(Config.RESULTS_PATH, Config.SHAPE, group_config)
        self.dir_meta = os.path.join(self.dir_experiment, self.result_name)
        self.dir_figure = os.path.join(self.dir_experiment, 'figures')

        if not os.path.exists(self.dir_meta):
            os.makedirs(os.path.join(self.dir_meta, 'json'), exist_ok=True)
        if not os.path.exists(self.dir_figure):
            os.makedirs(self.dir_figure, exist_ok=True)

    def _define_dispatcher_coords(self):
        l = 60
        w = 60
        if Config.DISPATCHERS == 1:
            if Config.SANITY_TEST > 0:
                self.dispatchers_coords = np.array([self.center])
            else:
                self.dispatchers_coords = np.array([[l / 2, w / 2, 0]])
        elif Config.DISPATCHERS == 3:
            self.dispatchers_coords = np.array([[l / 2, w / 2, 0], [l, w, 0], [0, 0, 0]])
            # self.dispatchers_coords = np.array([[l / 2, w / 2, 0], [l / 2, w / 2, 0],[l / 2, w / 2, 0]])
        elif Config.DISPATCHERS == 5:
            self.dispatchers_coords = np.array([[l / 2, w / 2, 0], [l, 0, 0], [0, w, 0], [l, w, 0], [0, 0, 0]])

    def _initialize_dispatchers(self):
        logger.info(f"Initializing {Config.DISPATCHERS} dispatchers")

        for coord in self.dispatchers_coords:
            q = queue.Queue()
            d = Dispatcher(q, Config.DISPATCH_RATE, coord)
            self.dispatchers.append(d)

    def _start_dispatchers(self):
        logger.info(f"Starting {Config.DISPATCHERS} dispatchers")

        for d in self.dispatchers:
            d.start()

    def _send_msg_to_all_nodes(self, msg):
        for nid in range(len(self.client_sockets)):
            self._send_msg_to_node(nid, msg)

    def _send_msg_to_node(self, nid, msg):
        send_msg(self.client_sockets[nid], msg)

    def _receive_msg_from_node(self, nid):
        return self.client_sockets[nid].recv(1024)

    def _start_secondary_nodes(self):
        logger.info(f"Starting {N} secondary nodes")
        self.start_time = time.time()
        self._send_msg_to_all_nodes((self.start_time, self.dir_meta))

    def _read_groups(self):
        if Config.SANITY_TEST == 0:
            self.groups, self.radio_ranges = read_cliques_xlsx(
                os.path.join(self.dir_experiment, f'{Config.INPUT}.xlsx'))
        elif Config.SANITY_TEST == 1:
            height = min([2, math.sqrt(Config.SANITY_TEST_CONFIG[1][1])])
            radius = math.sqrt(Config.SANITY_TEST_CONFIG[1][1] ** 2 - height ** 2)
            self.center = [radius + 1, radius + 1, 0]
            self.groups = generate_circle_coordinates(self.center, radius, height, Config.SANITY_TEST_CONFIG[0][1])
            self.radio_ranges = [Config.MAX_RANGE] * len(self.groups)

        elif Config.SANITY_TEST == 2:
            height = Config.STANDBY_TEST_CONFIG[1][1]
            radius = Config.STANDBY_TEST_CONFIG[0][1]
            self.center = [radius + 1, radius + 1, 10]
            self.groups = generate_circle_coordinates(self.center, radius, height, Config.K)
            self.radio_ranges = [Config.MAX_RANGE] * len(self.groups)

        if Config.DEBUG and Config.SANITY_TEST == 0:
            self.groups = self.groups[:2]
            self.radio_ranges = self.radio_ranges[:2]

        for group in self.groups:
            for coord in group:
                self.init_num += 1

        single_members = []
        single_indexes = []
        max_dist_singles = 0
        for k in range(len(self.groups)):
            if self.groups[k].shape[0] == 1:
                if len(single_indexes):
                    max_dist_n = np.max(np.linalg.norm(np.stack(single_members) - self.groups[k][0], axis=1))
                    max_dist_singles = max(max_dist_singles, max_dist_n)
                single_members.append(self.groups[k][0])
                single_indexes.append(k)

        # remove single nodes from groups
        for k in reversed(single_indexes):
            self.groups.pop(k)
            self.radio_ranges.pop(k)

        # add single nodes as one group to the groups
        if len(single_members):
            self.groups.append(np.stack(single_members))
            self.radio_ranges.append(max_dist_singles)

    def _assign_dispatcher(self, properties):
        return self.dispatch_policy.assign(dispatchers=self.dispatchers, **properties)

    def _deploy_fls(self, properties, deploy_at_destination=False):
        nid = properties["fid"] % self.N
        dispatcher = self._assign_dispatcher(properties)
        if deploy_at_destination:
            properties["el"] = properties["gtl"]

        if properties["el"] is None:
            properties["el"] = dispatcher.coord
        dispatcher.q.put(lambda: self._send_msg_to_node(nid, properties))
        dispatcher.time_q.put(time.time())
        dispatcher.num_dispatched += 1

    def _dispatch_initial_formation(self):
        logger.info("Assigning FLSs to dispatchers")

        for i in range(len(self.groups)):
            group = self.groups[i]
            group_id = self.pid + 1
            self.group_radio_range[group_id] = self.radio_ranges[i]
            self.group_standby_coord[group_id] = None
            self.group_standby_id[group_id] = None

            if Config.K:
                member_count = group.shape[0]
                sum_x = np.sum(group[:, 0])
                sum_y = np.sum(group[:, 1])
                sum_z = np.sum(group[:, 2])
                stand_by_coord = np.array([
                    float(round(sum_x / member_count)),
                    float(round(sum_y / member_count)),
                    float(round(sum_z / member_count))
                ])
                self.group_standby_coord[group_id] = stand_by_coord
                self.group_standby_id[group_id] = group_id + len(group)

            # deploy group members
            for member_coord in group:
                self.pid += 1
                fls = {
                    "fid": self.pid,
                    "el": None, "gtl": member_coord,
                    "radio_range": self.group_radio_range[group_id],
                    "group_id": group_id,
                }

                # If is doing stnadby sanity test, deploy the FLS directly to points on ring
                self._deploy_fls(fls, Config.SANITY_TEST == 2)
                self.num_initial_flss += 1

            # deploy standby
            if Config.K:
                self.pid += 1
                fls = {
                    "fid": self.pid,
                    "el": None, "gtl": self.group_standby_coord[group_id],
                    "radio_range": self.group_radio_range[group_id],
                    "is_standby": True, "group_id": group_id,
                }
                self._deploy_fls(fls, Config.SANITY_TEST == 2)
                self.num_initial_standbys += 1

        logger.info(f"Assigned {self.pid} FLSs to dispatchers")

    def _create_failure_handler_socket(self):
        self.failure_handler_socket = worker.WorkerSocket()
        self.failure_handler_socket.sock.settimeout(1)

    def _handle_failures(self):
        logger.info("Handling Failures")

        self.stop_thread.start()

        # while time.time() - self.start_time <= Config.DURATION:
        while not self.stop_flag:
            try:
                msg, _ = self.failure_handler_socket.receive()
            except socket.timeout:
                continue

            if msg.dest_fid == 0:
                if msg.type == MessageTypes.REPLICA_REQUEST_HUB:
                    self.pid += 1
                    group_id = msg.swarm_id
                    is_illuminating = msg.args[0]

                    if is_illuminating:
                        fls = {
                            "fid": self.pid,
                            "el": None, "gtl": msg.gtl,
                            "radio_range": self.group_radio_range[group_id],
                            "group_id": group_id,
                        }
                        self._deploy_fls(fls)
                        self.num_replaced_flss += 1

                        logger.debug(f"fid={self.pid} normal failed_fid={msg.fid}")
                    else:
                        self.group_standby_id[group_id] = self.pid

                        # dispatch the new standby fls
                        fls = {
                            "fid": self.pid,
                            "el": None, "gtl": self.group_standby_coord[group_id],
                            "radio_range": self.group_radio_range[group_id],
                            "is_standby": True, "group_id": group_id,
                        }
                        self._deploy_fls(fls)
                        self.num_replaced_standbys += 1

                        logger.debug(f"fid={self.pid} standby failed_fid={msg.fid}")

                    self.num_handled_failures += 1

        self.end_time = time.time()

    def _stop_dispatchers(self):
        logger.info("Stopping dispatchers")

        delay_list = []

        for d in self.dispatchers:
            d.stop()
        for d in self.dispatchers:
            d.join()
        return delay_list

    def _stop_secondary_nodes(self):
        logger.info("Stopping secondary nodes")
        self._send_msg_to_all_nodes(False)
        client_threads = []
        for nid in range(len(self.client_sockets)):
            t = threading.Thread(target=self._receive_msg_from_node, args=(nid,))
            t.start()
            client_threads.append(t)
        for t in client_threads:
            t.join()

    def _get_metrics(self):
        return [
            ["Metric", "Value"],
            ["Initial illuminating FLSs", self.num_initial_flss],
            ["Initial standby FLSs", self.num_initial_standbys],
            ["Handled failures", self.num_handled_failures],
            ["Dispatched replica illuminating FLSs", self.num_replaced_flss],
            ["Dispatched replica standby FLSs", self.num_replaced_standbys],
            ["Queued FLSs", sum([d.q.qsize() for d in self.dispatchers])],
        ]

    def _get_dispatched_num(self):
        info = [["dispatcher_coord", "num_dispatched", "avg_delay", "delay_info"]]
        for dispatcher in self.dispatchers:
            if Config.RESET_AFTER_INITIAL_DEPLOY:
                info.append([dispatcher.coord.tolist(), dispatcher.num_dispatched - self.num_initial_standbys,
                             sum(dispatcher.delay_list[self.num_initial_standbys:]) / len(
                                 dispatcher.delay_list[self.num_initial_standbys:])
                             if len(dispatcher.delay_list) > self.num_initial_standbys else 0,
                             dispatcher.delay_list])
            else:
                info.append([dispatcher.coord.tolist(), dispatcher.num_dispatched,
                             sum(dispatcher.delay_list) / len(dispatcher.delay_list) if len(
                                 dispatcher.delay_list) > 0 else 0,
                             dispatcher.delay_list])
        return info

    def gen_group_map(self):
        if Config.SANITY_TEST == 0:
            group_map, group_id = get_group_mapping(os.path.join(self.dir_experiment, f'{Config.INPUT}.xlsx'))
        else:
            group_map = dict()
            for group in self.groups:
                for coord in group:
                    group_map[point_to_id(coord)] = 0
            group_id = [0]
        return group_map, group_id

    def write_sanity_results(self):
        sanity_result = [['', 'Stander Result', 'Experiment Result']]

        if Config.SANITY_TEST == 1:
            experiment_result = read_sanity_metrics(self.dir_meta, [round(Config.SANITY_TEST_CONFIG[2][1]),
                                                                    round(Config.SANITY_TEST_CONFIG[2][2], 5)])

            stander_mttr = time_to_arrive(Config.MAX_SPEED, Config.ACCELERATION, Config.DECELERATION,
                                          Config.SANITY_TEST_CONFIG[1][1] * Config.DISPLAY_CELL_SIZE)
        else:
            experiment_result = read_sanity_metrics(self.dir_meta, [round(Config.STANDBY_TEST_CONFIG[3][1]),
                                                                    round(Config.STANDBY_TEST_CONFIG[3][2], 5)])
            stander_mttr = time_to_arrive(Config.MAX_SPEED, Config.ACCELERATION, Config.DECELERATION,
                                          Config.STANDBY_TEST_CONFIG[0][1] * Config.DISPLAY_CELL_SIZE)
        cur_midflight = 0
        num_illuminate = 0
        num_midflight = 0

        if Config.SANITY_TEST == 1:
            checkRange = range(round(Config.SANITY_TEST_CONFIG[2][1]), round(Config.SANITY_TEST_CONFIG[2][2], 5))
        else:
            checkRange = range(round(Config.STANDBY_TEST_CONFIG[3][1]), round(Config.STANDBY_TEST_CONFIG[3][2], 5))
        for t in checkRange:

            if Config.SANITY_TEST == 1:
                cur_midflight = num_mid_flight(Config.SANITY_TEST_CONFIG[0][1], experiment_result[4],
                                               experiment_result[3])
                num_midflight += cur_midflight
                num_illuminate += num_illuminating(Config.SANITY_TEST_CONFIG[0][1], cur_midflight)
            else:
                cur_midflight = 1 if t % Config.STANDBY_TEST_CONFIG[2][1] >= experiment_result[4] else 0
                num_midflight += cur_midflight
                num_illuminate += num_illuminating(Config.K, cur_midflight)

        if Config.SANITY_TEST == 1:
            num_midflight /= len(
                range(round(Config.SANITY_TEST_CONFIG[2][1]), round(Config.SANITY_TEST_CONFIG[2][2], 5)))
            num_illuminate /= len(
                range(round(Config.SANITY_TEST_CONFIG[2][1]), round(Config.SANITY_TEST_CONFIG[2][2], 5)))
        else:
            num_midflight /= len(
                range(round(Config.STANDBY_TEST_CONFIG[3][1]), round(Config.STANDBY_TEST_CONFIG[3][2], 5)))
            num_illuminate /= len(
                range(round(Config.STANDBY_TEST_CONFIG[3][1]), round(Config.STANDBY_TEST_CONFIG[3][2], 5)))

        if Config.SANITY_TEST == 1:
            num_failed = num_of_failed(Config.SANITY_TEST_CONFIG[2][2], experiment_result[3],
                                       Config.SANITY_TEST_CONFIG[0][1])
        else:
            num_failed = Config.DURATION / Config.STANDBY_TEST_CONFIG[2][1]

        sanity_result.append(['Total Failed', num_failed, experiment_result[0]])
        sanity_result.append(['Avg mid_flight', num_midflight, experiment_result[1]])
        sanity_result.append(['Avg_illuminate', num_illuminate, experiment_result[2]])

        if Config.SANITY_TEST <= 1:
            theo_MTTF = Config.FAILURE_TIMEOUT / 2
        else:
            theo_MTTF = Config.DURATION / 2
        sanity_result.append(['MTTF', theo_MTTF, experiment_result[3]])
        sanity_result.append(['MTTR', stander_mttr, experiment_result[4]])
        utils.write_csv(self.dir_meta, sanity_result, 'sanity_check')


    def write_final_report(self,group_id):

        report_key = [
            "Total Dispatched",
            "Total Failed",
            "Mid-Flight",
            "Illuminating",
            "Avg Dist Traveled",
            "Min Dist Traveled",
            "Max Dist Traveled",
            "Median Dist Traveled",
            "Avg MTTR",
            "Min MTTR",
            "Max MTTR",
            "Median MTTR",
            "Deploy Rate",
            "Number of Groups",
        ]
        time_range = [0, Config.DURATION + 10]
        report_metrics = get_report_metrics(self.dir_meta, time_range, len(group_id))
        report_metrics = [str(metric) for metric in report_metrics]
        report_metrics.append(str(Config.DISPATCH_RATE))
        report_metrics.append(str(len(group_id)))

        report = []

        for i in range(len(report_key)):
            report.append([report_key[i], report_metrics[i]])

        utils.write_csv(self.dir_meta, report, self.result_name + '_final_report')


    def _write_results(self):
        logger.info("Writing results")
        utils.write_csv(self.dir_meta, self._get_dispatched_num(), 'dispatcher')
        utils.write_csv(self.dir_meta, self._get_metrics(), 'metrics')

        group_map, group_id = self.gen_group_map()

        utils.create_csv_from_json(Config, self.init_num, self.dir_meta,
                                   os.path.join(self.dir_figure, f'{self.result_name}.jpg'), group_map)
        utils.write_configs(self.dir_meta, self.start_time)
        utils.combine_csvs(self.dir_meta, self.dir_experiment, "reli_" + self.result_name)

        if Config.SANITY_TEST > 0:
            self.write_sanity_results()
        else:
            self.write_final_report(group_id)

    def stop_experiment(self):
        self._stop_dispatchers()

        logger.info(f"Stopping the experiment, experiment time={time.time() - self.start_time}")

        stop_send_time = time.time()
        self._stop_secondary_nodes()
        logger.info(f"Time for All process stop={time.time() - stop_send_time}")

        self.stop_flag = True
        self._write_results()

    def start_experiment(self):
        self._setup_results_directory()

        utils.file.delete_previous_json_files(self.dir_meta)

        self._create_server_socket()
        self._bind_server_socket()
        self._listen_to_secondary_nodes()
        self._read_groups()
        self._define_dispatcher_coords()
        self._start_secondary_nodes()
        self._initialize_dispatchers()
        self._dispatch_initial_formation()
        self._create_failure_handler_socket()
        self._start_dispatchers()
        self._handle_failures()

    def start_termination_timer(self):
        self.stop_thread = threading.Timer(Config.DURATION, self.stop_experiment)


if __name__ == '__main__':
    N = 1
    name = str(int(time.time()))
    if len(sys.argv) > 1:
        N = int(sys.argv[1])
        name = sys.argv[2]

    primary_node = PrimaryNode(N, name)

    primary_node.start_termination_timer()
    primary_node.start_experiment()
    primary_node.stop_experiment()

    # for c in range(0,24):
    #     # CONFIG = eval(f"config{c}").Config
    #     # Config = CONFIG
    #
    #     if len(CONFIG.FILE_NAME_KEYS):
    #         result_config = join_config_properties(CONFIG, CONFIG.FILE_NAME_KEYS)
    #     else:
    #         result_config = name
    #     result_name = f"{Config.SHAPE}_{result_config}"
    #     print(result_name)
    #
    #     if len(CONFIG.DIR_KEYS):
    #         group_config = join_config_properties(CONFIG, CONFIG.DIR_KEYS)
    #     else:
    #         group_config = ""
    #
    #     dir_experiment = os.path.join(Config.RESULTS_PATH, Config.SHAPE, group_config)
    #     dir_meta = os.path.join(dir_experiment, result_name)
    #     dir_figure = os.path.join(dir_experiment, 'figures')

        # utils.create_csv_from_timeline(dir_meta)
        #
        # utils.combine_csvs(dir_meta, dir_experiment, "reli_" + result_name)
        #
        # report_key = [
        #     "Total Dispatched",
        #     "Total Failed",
        #     "Mid-Flight",
        #     "Illuminating",
        #     "Avg Dist Traveled",
        #     "Min Dist Traveled",
        #     "Max Dist Traveled",
        #     "Median Dist Traveled",
        #     "Avg MTTR",
        #     "Min MTTR",
        #     "Max MTTR",
        #     "Median MTTR",
        #     "Deploy Rate",
        #     "Number of Groups",
        # ]
        # time_range = [0, Config.DURATION + 10]
        # report_metrics = get_report_metrics_no_group(dir_meta, time_range)
        # report_metrics = [str(metric) for metric in report_metrics]
        # report_metrics.append(str(Config.DISPATCH_RATE))
        #
        # if CONFIG.K == 3:
        #     group_num = 152
        # elif CONFIG.K == 10:
        #     group_num = 46
        # else:
        #     group_num = 22
        # report_metrics.append(str(group_num))
        #
        # report = []
        #
        # for i in range(len(report_key)):
        #     report.append([report_key[i], report_metrics[i]])
        #
        # utils.write_csv(dir_meta, report, result_name + '_final_report')
