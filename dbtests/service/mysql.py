'''
description:
Author: ccp
return {*}
Date: 2023-03-14 20:18:01
'''
from .server import Service

class MysqlCom(Service):
    def __init__(self, name: str = None, version: str = None) -> None:
        super().__init__(name, version)

    def install(self, *args, **kwargs):
        return super().install()

    def destroy(self):
        return super().destroy()

    def use(self):
        return super().use()

    def start(self,
        config=None,
    ):
        '''
            start by:
                1. mysqld
                2. mysql_safe
                3. mysql_multi
                4. mysql.server
        '''
        return super().start()