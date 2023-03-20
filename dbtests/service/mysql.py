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

    def setup(self):
        return super().setup()

    def destroy(self):
        return super().destroy()

    def use(self):
        return super().use()

    def start(self):
        return super().start()