import logging

from PyQt5 import QtCore

from client.client import Client
from log_config import log

logger = logging.getLogger('root')


class Monitor(QtCore.QObject):

    gotCheck = QtCore.pyqtSignal(dict)
    gotConsole = QtCore.pyqtSignal(dict)
    gotError = QtCore.pyqtSignal(dict)


    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.client = Client('127.0.0.1', 8000)
        self.resv_queue = self.client.recv_queue

    def recv_msg(self):
        while 1:
            data = self.resv_queue.get()
            head = data['head']
            body = data['body']
            logger.debug("'%s':'%s' is '%s'", head['type'], head['name'], body['message'])
            if head['type'] == 'server response' and head['name'] == 'check_user':
                self.gotCheck.emit(body)
            elif head['type'] == 'server response' and head['name'] == 'registration':
                self.gotConsole.emit(body)
            elif head['type'] == 'server response' and head['name'] == 'registration error':
                self.gotConsole.emit(body)
                self.gotError.emit(body)
            self.resv_queue.task_done()
