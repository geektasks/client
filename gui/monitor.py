import os
import logging

from PyQt5 import QtCore

from client.client import Client
from db.client_db import ClientDB
from log_config import log

logger = logging.getLogger('root')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = 'Client_db'

db = ClientDB.create_db(os.path.join(BASE_DIR, DB_NAME))
db.connect()

class Monitor(QtCore.QObject):
    gotCheck = QtCore.pyqtSignal(dict)
    gotConsole = QtCore.pyqtSignal(dict)
    gotError = QtCore.pyqtSignal(dict)

    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        self.client = Client('ddimans.dyndns.org', 8000)
        # self.client = Client('127.0.0.1', 8000)

        self.client = Client('127.0.0.1', 8000)

        self.resv_queue = self.client.recv_queue

    def recv_msg(self):
        while 1:
            data = self.resv_queue.get()
            print('*', data)
            head = data['head']
            body = data['body']
            logger.debug("'%s':'%s' is '%s'", head['type'], head['name'], body['message'])
            if head['type'] == 'server response' and head['name'] == 'check_user':
                self.gotCheck.emit(body)
            elif head['type'] == 'server response' and head['name'] == 'registration':
                print(self.client.username)
                self.gotConsole.emit(body)
            elif head['type'] == 'server response' and head['name'] == 'registration error':
                self.gotConsole.emit(body)
                self.gotError.emit(body)
            elif head['type'] == 'server response' and head['name'] == 'authorization':
                print(data)
                if body['code'] == 200:
                    db.add_user(self.client.username)
                    db.add_session_id(self.client.username, head['session_id'])
            self.resv_queue.task_done()


if __name__ == '__main__':
    from function.requests import authorization, registration
    import os

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_NAME = 'Client_db'

    db = ClientDB.create_db(os.path.join(BASE_DIR, DB_NAME))
    db.connect()

    cl = Client('127.0.0.1', 8000)
    cl.username = 'Bob20'
    cl.run()
    message = authorization(name='Bob20', password='password')
    cl.send_queue.put(message)
