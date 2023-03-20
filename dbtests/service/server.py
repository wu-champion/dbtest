'''
description:
Author: ccp
return {*}
Date: 2023-03-14 19:13:49
'''

from abc import ABCMeta, abstractmethod

from ..dataclass import TService as T


class Service(metaclass=ABCMeta):
    # log file name
    dbtest_log_file_name = "test.log"
    # taostest log dir variable
    dbtest_log_dir_variable = "DBTEST_LOG_DIR"
    def __init__(self,
            name: T = None,
            version: str = None,
        ) -> None:
        self.name = name
        self.version = version

    @abstractmethod
    def setup(self): ...

    @abstractmethod
    def destroy(self): ...

    @abstractmethod
    def use(self): ...
    """
    When use an existing environment, only need to generate cfg of service in run log dir.
    """

    @abstractmethod
    def start(self):...
