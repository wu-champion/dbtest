from dataclasses import dataclass
from typing import List, Any
from enum import Enum

import datetime
import json


class TService(Enum):
    # use int number be a test service
    MYSQL: int = 1
    PGSQL: int = 2


# class TService(Enum):
#     # use service name
#     MYSQL = "mysql"
#     PGSQL = "pgsql"

@dataclass
class CmdOption:
    T: TService = TService.MYSQL
    cmds: str = None
    setup: str = None
    destroy: str = None
    use: str = None

    containers: bool = False
    swarm: bool = False

    tag: str = None
    env_init: bool = False

    log_level: str = None

    cases: List[str] = None
    group_files: List[str] = None
    group_dirs: List[str] = None


class DBJsonEncoder(json.JSONEncoder):

    def default(self, o: Any) -> Any:
        if isinstance(o, datetime.datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S.%f")
        else:
            super(DBJsonEncoder, self).default(o)


@dataclass
class ResultLog:
    case_group: str = ""
    case_path: str = ""
    author: str = None
    tags: List[str] = None
    desc: str = None
    start_time: datetime.datetime = None
    stop_time: datetime.datetime = None
    elapse: float = None
    success: bool = None
    error_msg: str = ""
    report: Any = None

    def to_json(self):
        if self.start_time and self.stop_time:
            delta = self.stop_time - self.start_time
            self.elapse = delta.seconds + delta.microseconds / 1000000
        return json.dumps(self.__dict__, cls=DBJsonEncoder, ensure_ascii=False)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args: Any, **kwds: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwds)

        return cls._instances[cls]
