import contextlib
import logging
import sys
from logging import handlers
import multiprocessing



class ThreadLogger():
    LEVELS = {
        "all": logging.ALL,
        "debug": logging.DEBUG,
        "error": logging.ERROR,
        "fatal": logging.FATAL,
        "info": logging.INFO,
        "off": logging.OFF,
        "warn": logging.WARN
    }
    def __init__(self, filePath: str, queue, logLevel="debug", name="test"):
        super().__init__()
        self._filePath = filePath
        self._queue = queue
        self.t = None
        self.level = self.LEVELS.get(logLevel.lower(), logging.DEBUG)
        self.logger = get_basic_logger(name)

    def work_thread(self):
        logging.basicConfig(
            format="%(asctime)s %(levelname)s: %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S',
            level=self.level,
            handlers=[logging.StreamHandler(sys.stdout)]
        )

        while True:
            with contextlib.suppress(Exception):
                level, msg, args = self._queue.get(block=True)
                log_level = self.LEVELS.get(level.lower(), logging.INFO)
                self.logger.log(log_level, msg, *args)
                if level == "terminate":
                    break

    def start(self):
        # start log threadThreadLogger
        self.t = multiprocessing.Process(target=self.work_thread, args=())
        self.t.start()


def get_basic_logger(name="test"):
    return logging.getLogger(name)


class Logger():
    def __init__(self, queue):
        self._queue = queue

    def debug(self, msg, *args):
        self._queue.put(("debug", msg, args))

    def info(self, msg, *args):
        self._queue.put(("info", msg, args))

    def warning(self, msg, *args):
        self._queue.put(("warning", msg, args))

    def error(self, msg, *args):
        self._queue.put(("error", msg, args))

    def critical(self, msg, *args):
        self._queue.put(("critical", msg, args))

    def terminate(self, msg, *args):
        self._queue.put(("terminate", msg, args))

    def exception(self, msg, *args):
        self._queue.put(("exception", msg, args))
