import sys

from PyQt5 import QtCore, QtWidgets, uic, QtGui
from gui.templates.sign_up import Ui_Dialog as ui_class
from function.registration import registration as registr
from function.check import check_user

class SignUpWind(QtWidgets.QDialog):

    def __init__(self, monitor, parent = None):
        super().__init__(parent)
        self.monitor = monitor
        self.ui = ui_class()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)

        self.flag = None






        self.monitor.gotCheck.connect(self.label_check_user)
        self.ui.login.textChanged.connect(self.check_login)
        self.ui.ok.clicked.connect(self.reg)
        # self.ui.cancel.clicked.connect(self.ui.close)
        # self.ui.cancel.clicked.connect(self.sign_in)
        # self.ui.exec()

    def reg(self):
        name = self.ui.login.text()
        password = self.ui.password.text()
        email = self.ui.email.text()
        self.fields_checker(name, password, self)
        if self.flag:
            registr(name, password, email)
        else:
            QtWidgets.QMessageBox.warning(self.ui, 'Warning!', 'Uncorrect name')
            self.registration()

    def check_login(self):
        text = self.ui.login.text()
        check_user(text)

    @QtCore.pyqtSlot(dict)
    def label_check_user(self, body):
        if body['code'] == 200:
            pixmap = QtGui.QPixmap('gui/icon/ok.png')
            self.ui.label_4.resize(23, 23)
            self.ui.label_4.setPixmap(pixmap)
            self.ui.flag = True
        else:
            pixmap = QtGui.QPixmap('gui/icon/error.png')
            self.ui.label_4.resize(23, 23)
            self.ui.label_4.setPixmap(pixmap)
            self.ui.flag = None

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