import sys

from PyQt5 import QtCore, QtWidgets, uic, QtGui
from gui.main_form import Ui_MainWindow as ui_class

from gui.monitor import Monitor



class MyWindow(QtWidgets.QMainWindow):

    def __init__(self, parent = None):

        super().__init__(parent)
        self.ui = ui_class()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)

        self.monitor = Monitor(self)
        self.thread = QtCore.QThread()
        self.start_monitor(QtWidgets.QDialog())

        self.monitor.gotCheck.connect(self.update_console)
        self.monitor.gotError.connect(self.update_error)

        self.sign_in()

    def start_monitor(self, dialog):
        self.monitor.moveToThread(self.thread)
        self.thread.started.connect(self.monitor.recv_msg)
        self.thread.start()
        # connect = self.monitor.client.socket._closed
        connect = self.monitor.client.run()
        if connect:
            QtWidgets.QMessageBox.warning(dialog, 'Warning!', 'Not connect')
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

    def registration(self):
        dialog_reg = uic.loadUi('gui/sign_up.ui')
        dialog_reg.login.setFocus()
        dialog_reg.flag = None

        def reg():
            name = dialog_reg.login.text()
            password = dialog_reg.password.text()
            email = dialog_reg.email.text()
            self.fields_checker(name, password, dialog_reg)
            if dialog_reg.flag:
                self.monitor.client.registration(name, password, email)
            else:
                QtWidgets.QMessageBox.warning(dialog_reg, 'Warning!', 'Uncorrect name')
                self.registration()

        def check_login(monitor):
            text = dialog_reg.login.text()
            monitor.client.check_user(text)

        @QtCore.pyqtSlot(dict)
        def label_check_user(body):
            if body['code'] == 200:
                pixmap = QtGui.QPixmap('gui/icon/ok.png')
                dialog_reg.label_4.resize(23, 23)
                dialog_reg.label_4.setPixmap(pixmap)
                dialog_reg.flag = True
            else:
                pixmap = QtGui.QPixmap('gui/icon/error.png')
                dialog_reg.label_4.resize(23, 23)
                dialog_reg.label_4.setPixmap(pixmap)
                dialog_reg.flag = None


        self.monitor.gotCheck.connect(label_check_user)
        dialog_reg.login.textChanged.connect(lambda: check_login(self.monitor))
        dialog_reg.ok.clicked.connect(reg)
        dialog_reg.cancel.clicked.connect(dialog_reg.close)
        dialog_reg.cancel.clicked.connect(self.sign_in)
        dialog_reg.exec()

    def sign_in(self):

        dialog = uic.loadUi('gui/sign_in.ui')
        dialog.login.setFocus()

        def login():
            name = dialog.login.text()
            password = dialog.password.text()
            self.fields_checker(name, password, dialog)

        dialog.ok.clicked.connect(login)
        dialog.registration.clicked.connect(dialog.close)
        dialog.registration.clicked.connect(self.registration)
        dialog.cancel.clicked.connect(sys.exit)
        dialog.exec()

    def on_createTask_pressed(self):
        dialog = uic.loadUi('gui/task_create.ui')
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
