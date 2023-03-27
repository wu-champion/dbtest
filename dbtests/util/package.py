import platform
import os

from abc import abstractmethod, ABCMeta

from .remote import Remote

class Package(meta=ABCMeta):
    def __init__(self,
        pkg_name: str = None,
    ):
        self._pkg_name = None
        self._version = None
        self._remote: Remote = None


    def get_pkg(self,
        pkg_path: str = None,
        host: str = None,
        local_path: str = None,
        user: str = None,
    ) :
        self._remote.connect(host, user)
        self._remote.get(pkg_path, local_path)

    @abstractmethod
    def install(self, package_manager, pkg_path):
        # normal pkg install
        if package_manager == 'yum':
            os.system(f'yum localinstall {pkg_path}')
        elif package_manager == 'apt':
            os.system(f'apt-get install {pkg_path}')
        else:
            raise ValueError(f'Unsupported package manager: {package_manager}')

    def get_package_manager(self):
        system = platform.system()
        if system != 'Linux':
            raise OSError('Unsupported operating system')

        if os.path.exists('/etc/redhat-release'):
            # CentOS system, use yum
            return 'yum'
        elif os.path.exists('/etc/lsb-release'):
            # Ubuntu system, use apt
            return 'apt'
        else:
            raise OSError('Unsupported Linux distribution')

    @abstractmethod
    def destroy(self):
        '''
            remove the package
        '''
