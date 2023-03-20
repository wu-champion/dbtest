import os
import signal

from .frame import DBTestFrame
from .dataclass import CmdOption

import json
import argparse
import sys
from dotenv import load_dotenv
import pathlib
from colorama import init

_VERSION = "0.1.0"

def get_env_file(path: str="~") -> str:
    """
    Get .env file path and check the existence.
    If .env not exist, then create an empty one and return None else return the real path.
    """
    frame_setting_path = f"{os.path.expanduser(path)}/.dbtest"
    frame_env_file = f"{frame_setting_path}/.env"

    if not os.path.exists(frame_env_file):
        os.mkdir(frame_setting_path)
        pathlib.Path(frame_env_file).touch()
        return None

    return frame_env_file

def check_env():
    if "TEST_ROOT" in os.environ:
        return True
    env_file_path = get_env_file()
    if env_file_path is None:
        return False
    load_dotenv(env_file_path)
    return "TEST_ROOT" in os.environ

#TODO: complete the  parameter definition of command( properties of class CmdOption)
def parse_command_line():
    prog = "dbtest"
    desc = '''
        \rdatabase test framework.
        \rFor a complete guide please visit:
        \r  https://github.com/wu-champion/dbtest'''
    if "TEST_ROOT" in os.environ:
        desc += f"\nTEST_ROOT={os.environ['TEST_ROOT']}"

    epli = '''
    \rExample:
    dbtest --init
    dbtest --prepare=hostname,passwd
    dbtest --setup=env.yaml --case=mycase.py --keep
    '''

    parser = argparse.ArgumentParser(
        description=desc,
        prog=prog,
        fromfile_prefix_chars='@',
        usage=f"\n    {prog} [options]",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
        epilog=epli
    )
    req_opt = parser.add_argument_group("Options require argument")
    req_opt.add_argument("--setup", metavar="",
                         help="create a test environment specified by a yaml file", )
    req_opt.add_argument("--destroy", metavar="",
                         help="destroy test environment specified by a yaml file", )
    req_opt.add_argument(
        "--server-pkg", metavar="server_pkg",
        help="server package file"
    )
    req_opt.add_argument(
        "--client-pkg", metavar="client_pkg",
        help="client package file"
    )
    req_opt.add_argument("--use", metavar="",
                         help="using an existing test environment", )
    req_opt.add_argument("--group-file", metavar="group_file",
                         action="extend", nargs="+",
                         help="execute test groups", )
    req_opt.add_argument("--group-dir", metavar="group_dir",
                         action="extend", nargs="+",
                         help="execute test groups", )
    req_opt.add_argument("--case", metavar="",
                         action="extend", nargs="+",
                         help="execute cases", )
    req_opt.add_argument("--concurrency", metavar="",
                         type=int,
                         help="number of concurrently execute cases", )
    req_opt.add_argument("--tag", metavar="",
                         help="add some run tag", )
    req_opt.add_argument("--prepare", metavar="",
                         help="install commands that frame depend on including screen, docker, docker-compose", )
    req_opt.add_argument("--servcfg", metavar="",
                         type=json.loads,
                         help="update env yaml", )

    unreq_opt = parser.add_argument_group("Options not require argument")
    unreq_opt.add_argument('-h', '--help', action="help", help="show this help message and exit")
    unreq_opt.add_argument('-v', '--version',
                           action="store_true", default=False,
                           help="print version")
    unreq_opt.add_argument('-i', '--init',
                           action="store_true", default=False,
                           help="initialize directory structure of $TEST_ROOT")
    unreq_opt.add_argument('--keep',
                           action="store_true", default=False,
                           help="whether to keep the environment after executing")
    unreq_opt.add_argument('--reset',
                           action="store_true", default=False,
                           help="whether to reset the environment before executing")
    unreq_opt.add_argument('--early_stop',
                           action="store_true", default=False,
                           help="stop execute left cases on any case failed")
    unreq_opt.add_argument('--env_init',
                           action="store_true", default=False,
                           help="stop execute left cases on any case failed")
    unreq_opt.add_argument(
        "--containers",
        action="store_true", default=False,
        help="create containers"
    )
    unreq_opt.add_argument(
        "--swarm",
        action="store_true", default=False,
        help="swarm mode"
    )
    unreq_opt.add_argument(
        "--disable_collection",
        action="store_true", default=False,
        help="disable data collection in case of test failure"
    )
    unreq_opt.add_argument(
        "--sql_recording",
        action="store_true", default=False,
        help="record sql"
    )
    unreq_opt.add_argument(
        "--rm_containers",
        action="store_true", default=False,
        help="remove containers"
    )
    req_opt.add_argument(
        "--log-level", metavar="log_level",
        help="log level"
    )
    req_opt.add_argument(
        "--source-dir", metavar="source_dir",
        help="source directory"
    )
    req_opt.add_argument(
        "--dbtest-pkg", metavar="dbtest_pkg",
        help="dbtest package for container mode"
    )
    req_opt.add_argument(
        "--docker-network", metavar="docker_network",
        help="docker network name for container mode"
    )
    req_opt.add_argument(
        "--cfg-file", metavar="cfg_file",
        help="case configuration file"
    )
    req_opt.add_argument(
        "--case-param", metavar="case_param",
        help="case parameters"
    )
    unreq_opt.add_argument(
        "--stop",
        action="store_true", default=False,
        help="stop service or valgrind"
    )
    pars = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
        return

    opts = CmdOption()
    opts.version = bool(pars.version)
    opts.init = bool(pars.init)
    opts.keep = bool(pars.keep)
    opts.reset = bool(pars.reset)
    opts.early_stop = bool(pars.early_stop)
    opts.env_init = bool(pars.env_init)
    opts.containers = bool(pars.containers)
    opts.swarm = bool(pars.swarm)
    opts.rm_containers = bool(pars.rm_containers)
    opts.stop = bool(pars.stop)
    opts.disable_collection = bool(pars.disable_collection)
    opts.sql_recording = bool(pars.sql_recording)
    # if opts.sql_recording:
    #     os.environ[DBSql.dbtest_enable_sql_recording_variable] = "TRUE"

    opts.setup = pars.setup or None
    opts.destroy = pars.destroy or None
    opts.server_pkg = pars.server_pkg or None
    if opts.server_pkg is not None and not os.path.exists(opts.server_pkg):
        print(f"--server-pkg {opts.server_pkg} not exist")
        sys.exit(1)
    opts.client_pkg = pars.client_pkg or None
    if opts.client_pkg is not None and not os.path.exists(opts.client_pkg):
        print(f"--client-pkg {opts.client_pkg} not exist")
        sys.exit(1)
    opts.use = pars.use or None
    opts.group_files = pars.group_file or None
    opts.group_dirs = pars.group_dir or None
    opts.cases = pars.case or None
    opts.log_level = pars.log_level or None
    opts.source_dir = pars.source_dir or None
    opts.dbtest_pkg = pars.dbtest_pkg or None
    if opts.dbtest_pkg is not None and not os.path.exists(opts.dbtest_pkg):
        print(f"--dbtest-pkg {opts.dbtest_pkg} not exist")
        sys.exit(1)
    opts.docker_network = pars.docker_network or None
    opts.cfg_file = pars.cfg_file or None
    opts.case_param = pars.case_param or None
    if pars.concurrency:
        if pars.concurrency < 1:
            print("--concurrency can't less than 1")
            sys.exit(1)
        else:
            opts.concurrency = pars.concurrency
    opts.uniform_dist = pars.uniform_dist or None
    opts.tag = pars.tag or None
    opts.prepare = pars.prepare or None
    opts.servcfg = pars.servcfg or None

    origin_cmds = sys.argv[1:]
    origin_cmds.insert(0, "dbtest")
    print(origin_cmds)
    str_cmds = ' '.join(origin_cmds)
    opts.cmds = str_cmds

    return opts

def check_opts(opts):
    # have one
    if (
        not opts.destroy
        and not opts.use
        and not opts.setup
        and not opts.prepare
    ):
        print("Must specify one option in:[ --destroy, --use, --setup, --prepare]")
        return False
    # have only one
    if (opts.destroy and opts.use) or (opts.use and opts.setup) or (opts.destroy and opts.setup):
        print("Can only specify one environment option: --destroy or --use or --setup")
        return False
    # test groups and test cases can't run together.
    if (opts.group_dirs or opts.group_files) and opts.cases:
        print("--group-dir or --group-file can't be used together with --case")
        return False
    # rm_containers  option must use with --containters
    if opts.containers:
        print(" It will exec in containters ")
    if opts.rm_containers and not opts.containers:
        print("--rm_containers must be used together with --containers")
        return False
    # --env_init must appear with --init
    if opts.env_init and not opts.init:
        print("--env_init must be used when using --init")
        return False

    if opts.cfg_file is not None:
        if not opts.cfg_file.startswith("/"):
            opts.cfg_file = os.environ["TEST_ROOT"] + "/" + opts.cfg_file
        if not os.path.exists(opts.cfg_file):
            print(f"--cfg-file {opts.cfg_file} not exist")
            return False
    return True


def set_test_root_interactively() -> str:
    print("Please input a path relative to current work directory or an absolute path:")
    ans = sys.stdin.readline()
    ans = ans.strip()
    test_root = os.path.abspath(ans)
    frame_setting_path = os.path.expanduser("~") + "/.dbtest"
    os.makedirs(frame_setting_path, exist_ok=True)
    frame_env_file = f"{frame_setting_path}/.env"
    with open(frame_env_file, 'wt') as f:
        f.write("TEST_ROOT=")
        f.write(test_root)
    print(f"Write 'TEST_ROOT={test_root}' to file {frame_env_file}.\nNote that variables in this file have lower priority than environment variable")
    return test_root


def ans_yes(ans):
    return ans in ['yes', 'y', '']


def confirm(text):
    print(text)
    ans = sys.stdin.readline()
    ans = ans.strip()
    return ans_yes(ans)


def init_test_root(env_ok):
    if env_ok:
        test_root = os.environ["TEST_ROOT"]
        if confirm(f"Do you want to initialize TEST_ROOT {test_root} ?"):
            create_test_root_sub_dirs(test_root)
        elif confirm("Do you want to change TEST_ROOT?"):
            test_root = set_test_root_interactively()
            create_test_root_sub_dirs(test_root)
    else:
        test_root = set_test_root_interactively()
        create_test_root_sub_dirs(test_root)


def init_default_env():
    """when dbtest --env_init, generate a default env toml
    """
    print("init a env yaml file to ${testroot}/env ")

    test_root = os.environ["TEST_ROOT"]
    env = Env()
    service_env = env.set_service_env()  #TODO: complete the service installation
    client_env = env.set_client_env()   #TODO: complete the client installation
    env_dict = [service_env, client_env, ]
    env_dir = os.path.join(test_root, 'env')
    # TODO: complete the function for generate env_file
    env.set_env_file(env_dict=env_dict, path=env_dir, filename="env_init.toml")


def create_test_root_sub_dirs(test_root):
    __create_test_root_sub_dirs(test_root, "cases", "create root dir of cases:")
    __create_test_root_sub_dirs(test_root, "groups", "create root dir of test group:")
    __create_test_root_sub_dirs(test_root, "run", "create root dir of run log:")
    __create_test_root_sub_dirs(test_root, "env", "create root dir of env settings:")
    print("done!")

def __create_test_root_sub_dirs(test_root, arg1, arg2):
    result = os.path.join(test_root, arg1)
    print(arg2, result)
    os.makedirs(result, exist_ok=True)
    return result

def main():
    """
    1. check TEST_ROOT environment variable.
    2. parse command line arguments.
    3. construct dbtestFrame object.
    4. start test dbtestFrame.
    """
    env_ok = check_env()
    opts = parse_command_line()

    if opts.version:
        print(_VERSION)
        return

    if opts.init:
        init_test_root(env_ok)
        if opts.env_init:
            init_default_env()
        return 1

    if not env_ok:
        print("Please set TEST_ROOT")
        print("You can set TEST_ROOT by two methods:")
        print("1. Write 'TEST_ROOT=xxxx' to", get_env_file())
        print("2. Use command: dbtest --init")
        return 1

    if not check_opts(opts):
        return 1

    db_test = DBTestFrame(opts)
    return db_test.start()


def signal_handler(signum, frame):
    print("receive signal:", signum)


def handle_signal():
    '''
    description: Used for setting signal processing functions"
    Author: ccp
    return {*}
    Date: 2023-03-20 20:24:03
    '''
    signal.signal(signal.SIGSEGV, signal.SIGTERM)

def init_colorama():
    try:
        init()
    except BaseException as e:
        print("Init colorama error", e)

def run_program():
    ret = main()
    sys.exit(ret)

if __name__ == '__main__':
    handle_signal()
    init_colorama()
    run_program()
