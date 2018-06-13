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


import sys

from PyQt5 import QtCore, QtWidgets, uic, QtGui
from gui.templates.main_form import Ui_MainWindow as ui_class

import threading
from client.client import Client
from function.requests import check_user
from function.requests import registration as registr
from function.requests import authorization as auth

class MyWindow(QtWidgets.QMainWindow):
    gotCheck = QtCore.pyqtSignal(dict)
    gotConsole = QtCore.pyqtSignal(dict)
    gotError = QtCore.pyqtSignal(dict)

    def __init__(self, parent = None):

        super().__init__(parent)
        self.ui = ui_class()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)

        self.client = Client('127.0.0.1', 8000)
        self.NAME = {
            'registration': self.gotConsole,
            'registration error': self.gotError,
            'authorization': '',
            'check user': self.gotCheck}
        self.start_thread()

        self.gotCheck.connect(self.update_console)
        self.gotError.connect(self.update_error)

        self.ui.action_login.triggered.connect(self.sign_in)

    def start_thread(self):
        t1 = threading.Thread(target= self.control)
        t1.daemon = True
        t1.start()
        connect = self.client.run()
        if connect:
            QtWidgets.QMessageBox.warning(self, 'Warning!', 'Not connect')
            sys.exit()

    def closeEvent(dialog, e):
        result = QtWidgets.QMessageBox.question(dialog,
                       "Confirmation",
                       "Do you really want to close window with tasks?",
                       QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                       QtWidgets.QMessageBox.No)
        if result == QtWidgets.QMessageBox.Yes:
            e.accept()
            QtWidgets.QWidget.closeEvent(dialog, e)
        else:
            e.ignore()

    @staticmethod
    def fields_checker(name, password, dialog):
        if not name and not password:
            QtWidgets.QMessageBox.warning(dialog, 'Warning!', 'Username and password are missing')
        elif not name:
            QtWidgets.QMessageBox.warning(dialog, 'Warning!', 'Username is missing')
        elif not password:
            QtWidgets.QMessageBox.warning(dialog, 'Warning!', 'Password is missing')
        else:
            dialog.accept()

#######################################################################################################################
    ########функция обработки сообщений от сервера################################################################
#######################################################################################################################

    def control(self):
        while 1:
            data = self.client.recv_queue.get()
            body = data['body']
            try:
                if data['head']['name'] in self.NAME:
                    print(data['head']['name'])
                    controller = self.NAME.get(data['head']['name'])
                    controller.emit(body)
                else:
                    print(data['head']['name'])
                    print('unknown_response')
            except Exception as err:
                print(err)

########################################################################################################################
    def registration(self):
        dialog_reg = uic.loadUi('gui/templates/sign_up.ui')
        dialog_reg.login.setFocus()
        dialog_reg.flag = None

        def reg():
            name = dialog_reg.login.text()
            password = dialog_reg.password.text()
            email = dialog_reg.email.text()
            self.client.username = name######## при регистрации запоминаем имя пользователя, при авторизации делать тоже самое
                                                    ### если авторизация прошла, пишем в бд
            self.fields_checker(name, password, dialog_reg)
            if dialog_reg.flag:
                registr(name, password, email)
            else:
                QtWidgets.QMessageBox.warning(dialog_reg, 'Warning!', 'Uncorrect name')
                self.registration()

        def check_login():
            text = dialog_reg.login.text()
            check_user(text)

        @QtCore.pyqtSlot(dict)
        def label_check_user(body):
            print(body)
            if body['code'] == 200:
                print('200')
                pixmap = QtGui.QPixmap('gui/icon/ok.png')
                dialog_reg.label_4.resize(23, 23)
                dialog_reg.label_4.setPixmap(pixmap)
                dialog_reg.flag = True
            else:
                print('409')
                pixmap = QtGui.QPixmap('gui/icon/error.png')
                dialog_reg.label_4.resize(23, 23)
                dialog_reg.label_4.setPixmap(pixmap)
                dialog_reg.flag = None


        self.gotCheck.connect(label_check_user)
        dialog_reg.login.textChanged.connect(check_login)
        dialog_reg.ok.clicked.connect(reg)
        dialog_reg.cancel.clicked.connect(dialog_reg.close)
        dialog_reg.cancel.clicked.connect(self.sign_in)
        dialog_reg.exec()

    def sign_in(self):
        dialog = uic.loadUi('gui/templates/sign_in.ui')
        dialog.login.setFocus()

        def login():
            name = dialog.login.text()
            password = dialog.password.text()
            self.fields_checker(name, password, dialog)
            auth(name, password)

        dialog.ok.clicked.connect(login)
        dialog.registration.clicked.connect(dialog.close)
        dialog.registration.clicked.connect(self.registration)
        dialog.cancel.clicked.connect(sys.exit)
        dialog.exec()

    def on_createTask_pressed(self):
        dialog = uic.loadUi('gui/templates/task_create.ui')
        dialog.topic.setFocus()

        def task_create():
            pass

        dialog.addTask.clicked.connect(task_create)
        dialog.addTask.clicked.connect(dialog.accept)
        dialog.exec()

        ################################################

    @QtCore.pyqtSlot(dict)
    def update_console(self, body):
        self.ui.statusbar.showMessage('{} - {}'.format(body['code'], body['message']))

    @QtCore.pyqtSlot(dict)
    def update_error(self, body):
        QtWidgets.QMessageBox.warning(QtWidgets.QDialog(), 'Warning!', body['message'])
        # sys.exit()
        self.registration()
