import platform
import os

from abc import ABCMeta, abstractmethod

from ..dataclass import TService as T
from ..util.remote import Remote


class Service(metaclass=ABCMeta):
    # log file name
    dbtest_log_file_name = "test.log"
    # taostest log dir variable
    dbtest_log_dir_variable = "DBTEST_LOG_DIR"
    def __init__(self,
            name: T = None,
            version: str = None,
            host: str = None
        ) -> None:
        self.name = name
        self.version = version
        self.host = host
        self.pkg_path = None


    @abstractmethod
    def install(self, package_manager, pkg_path):
        '''
            include；
                1. deploy one point  service instance
                2. deploy multi-points service instance
                3. deploy cluster service instance
        '''

    @abstractmethod
    def destroy(self): ...

    @abstractmethod
    def use(self,
        env: str = None,
    ):
        return  self.start(config=env)
    """
        When use an existing environment, only need to generate cfg of service in run log dir.
    """

    @abstractmethod
    def start(self,
        config : str = None,
    ):
        '''
            include start type:
                1. start db service by service/systemctl
                2. start db service by config
            include start service instance num:
                1. start a db instance
                2. start part of points
                3. start all cluster/points instance
        '''


    @abstractmethod
    def down(self):
        '''
            service down
        '''

    @abstractmethod
    def restart(self):
        '''
            restart service
        '''
