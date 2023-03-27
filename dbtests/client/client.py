from abc import ABCMeta, abstractmethod

class Client(metaclass=ABCMeta):
    def __init__(self, name):
        self.name = name
        self._connect = None
        self._record = False
        self._run_log_dir = None
        self._configu: str = None

    @abstractmethod
    def connect(self,
        host: str = None,
        port: int = None,
        user: str = None,
        password: str = None,
        config: str = None,  # connect with client config
    ):
        '''
            return a connector to the db-servecice
        '''

    @abstractmethod
    def install(self,
        pkg: str = None,
        host: str = None,
        version: str = None
    ) -> None:
        if pkg:
            '''
                if pkg , install with pkg
            '''

        else:
            '''
                if not pkg, install with command like apt/yum
                or get pkg from host
            '''

    @abstractmethod
    def unstall(self):
        '''
            uninstall client
        '''

    def records(self, sql):
        if self._record:
            with open(self._run_log_dir, "a") as f:
                f.write(f"{sql.strip()};\n")


    @abstractmethod
    def query(self, sql: str, time_out: int = 5):
        cursor = self._connect.cursor()
        cursor.execute(sql)