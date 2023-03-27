import os
import platform
import asyncio
import shutil
import paramiko
import threading

from typing import List

from ..logger import Logger


class Remote:
    '''
    description: return remote cmd
        example1； to get file from server
            remote = Remote(logger)
            remote.connect(host, user, password)
            remote.get(file, path)
            remote.close()
    return Remote()
    param {*} self
    param {Logger} logger
    '''
    def __init__(self, logger: Logger):
        self._logger = logger
        self._host = platform.node()
        self._transport = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _log_error(self, msg) -> False:
        self._logger.error(msg)
        return False

    async def connect(self, host: str, user: str, password: str = "", private_key: str = None) -> bool:
        assert host, "host is empty"
        assert user, "user is empty"
        # if not host: return self._log_error("host is empty")
        # if not user: return self._log_error("user is empty")
        if private_key and not os.path.exists(private_key):
            return self._log_error(f"private_key_file {private_key} not found")

        try:
            if private_key:
                transport = await self._ssh_connect(host, user, private_key)
            else:
                transport = paramiko.Transport(host)
                if password:
                    transport.connect(username=user, password=password)
                else:
                    transport.connect(username=user)

            self._transport = transport
            return True
        except Exception as e:
            return self._log_error(f"failed to connect to {host}: {e}")

    async def _ssh_connect(self, host, user, private_key):
        key = paramiko.RSAKey.from_private_key_file(private_key)
        transport = paramiko.Transport((host, 22))
        transport.connect(username=user, pkey=key)
        return transport

    async def _ssh_execute(self, transport: paramiko.Transport, cmd_line: str) -> str:
        channel = transport.open_session()
        await asyncio.get_event_loop().run_in_executor(None, channel.exec_command, cmd_line)
        result = await asyncio.get_event_loop().run_in_executor(None, channel.makefile().read)
        channel.close()
        return result.strip()

    async def remote_cmd(self, host: str, cmds: List[str], user: str="root", private_key: str="") -> str:
        cmd_line = " ".join(cmds)
        self._logger.info(f"cmd:{cmds}, is executed on {host}")
        if host == self._host:
            proc = await asyncio.create_subprocess_shell(
                cmd_line,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            output, error = await proc.communicate()
            return output.strip().decode()

        transport = await self._ssh_connect(host, user, private_key)
        result = await self._ssh_execute(transport, cmd_line)
        transport.close()
        return result

    def put(self, host: str, file: str, path: str) -> bool:
        if not os.path.exists(file):
            self._logger.error(f"file {file} not found")
            return False
        if not os.path.isdir(path):
            self._logger.error(f"path {path} is not a directory")
            return False

        self._logger.info("put %s to %s:%s", file, host, path)
        if host == platform.node():
            os.makedirs(path, exist_ok=True)
            if os.path.isdir(file):
                shutil.copytree(file, os.path.join(path, os.path.basename(file)), dirs_exist_ok=True)
            else:
                shutil.copy2(file, path)
            return True

        if not self._transport:
            self._logger.error("transport is not initialized")
            return False

        def _put_file():
            try:
                with paramiko.SFTPClient.from_transport(self._transport) as sftp:
                    sftp.put(file, path)
                self._logger.info(f"put file {file} to {path} successfully")
            except Exception as e:
                self._logger.error(f"failed to put file {file} to remote path {path}: {e}")

        threading.Thread(target=_put_file).start()
        return True

    def get(self, file: str, path: str) -> bool:
        if not os.path.isdir(path):
            self._logger.error(f"path {path} is not a directory")
            return False
        if not self._transport:
            self._logger.error("transport is not initialized")
            return False

        try:
            with paramiko.SFTPClient.from_transport(self._transport) as sftp:
                remote_files = sftp.listdir(os.path.dirname(file))
                if os.path.basename(file) not in remote_files:
                    self._logger.error(f"remote file {file} not found")
                    return False
                sftp.get(file, path)
            self._logger.info(f"get file {file} successfully")
            return True
        except Exception as e:
            self._logger.error(f"failed to get file {file}: {e}")
            return False

    def delete(self, host, file, password=""):
        assert self._transport, "not connected"
        filename = os.path.basename(file)
        delete_cmd = f'rm -rf {filename}'
        self.remote_cmd(host, [delete_cmd], password)

    def close(self):
        if self._transport:
            self._transport.close()
            self._transport = None
