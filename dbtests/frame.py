import multiprocessing
import os
import random
import string
import subprocess
import time
import traceback

from typing import Tuple

from .dataclass import CmdOption, ResultLog
from .logger import Logger, ThreadLogger
from .service import Service
from .case import CaseManage


class DBTestFrame:
    def __init__(self, opts: CmdOption) -> None:
        self._opts: CmdOption = opts
        self._cmds: str = opts.cmds
        self._T: Service = opts.T

        self._test_root: str = os.environ["TEST_ROOT"]

        self._run_test = self._opts.cases or self._opts.group_dirs or self._opts.group_files
        self._set_up_only: bool = self._opts.setup and not self._run_test

        self._run_log_dir, self._log_dir_name = self._get_run_log_dir()
        self._logger: Logger = None
        self._init_log()

        self._case_group: CaseManage = None


    def _get_run_log_dir(self) -> Tuple[str, str]:
        """ compute run log dir name """
        log_root = os.path.join(self._test_root, "run")
        log_dir_name = []
        if self._T.dbtest_log_dir_variable in os.environ:
            log_root = os.environ[self._T.dbtest_log_dir_variable]
        if self._opts.tag:
            log_dir_name.append(self._opts.tag)
        elif self._opts.destroy:
            log_dir_name.append("destroy")
        elif self._set_up_only:
            log_dir_name.append("setup")
        elif self._opts.cases:
            case_name = self._opts.cases[0]
            log_dir_name.append(case_name)
        elif self._opts.group_files:
            log_dir_name.append(self._opts.group_files[0].split(".")[0])
        elif self._opts.group_dirs:
            log_dir_name.append(self._opts.group_dirs[0])
        log_dir_name.append(time.strftime("_%Y%m%d_%H%M%S") + "_" + self._generate_random_str(8))
        log_dir_name = "".join(log_dir_name)
        return os.path.join(log_root, log_dir_name), log_dir_name

    def _generate_random_str(self, k: int):
        return ''.join(random.sample(string.ascii_letters + string.digits, k))

    def _init_log(self) -> None:
        """
        create logger
        """
        os.makedirs(self._run_log_dir)
        log_queue = multiprocessing.Queue()
        thread_logger = ThreadLogger(os.path.join(self._run_log_dir, self._T.dbtest_log_file_name), log_queue, self._opts.log_level)
        self._logger = Logger(log_queue)
        thread_logger.start()
        # self._logger = Logger(os.path.join(self._run_log_dir, "test.log"))
        self._logger.info(f"run log dir is {self._run_log_dir}")


    def _check_swarm_env(self):
        # check swarm environment
        cmd = "docker swarm join-token manager"
        ret = os.system(cmd)
        if ret != 0:
            self._logger.error("This node is not a swarm manager.")
            return False
        return True

    def _check_swarm_env(self):
        # check swarm environment
        cmd = ["docker", "swarm", "join-token", "manager"]
        try:
            subprocess.check_call(cmd)
            self._logger.info("This node is a swarm manager.")
            return True
        except subprocess.CalledProcessError as e:
            self._logger.error(f"This node is not a swarm manager. Error: {e}")
            return False


    '''
    description: main work flow of test framework
    Author: ccp
    return {*}
    Date: 2023-03-15 00:55:11
    param {*} self
    '''
    def main_work(self):
        if self._opts.setup:
            self._T.setup(self._opts.containers, self._opts.swarm)
        elif self._opts.destroy:
            self._T.destroy()
        elif self._opts.use:
            self._use()

    def _use(self):
        self._T.use()

    def start(self):
        try:
            self.main_work()
        except Exception as e:
            traceback.print_exc()
