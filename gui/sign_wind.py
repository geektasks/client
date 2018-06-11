from PyQt5 import QtCore, QtWidgets, uic, QtGui
from gui.templates.sign_in import Ui_Dialog as ui_class
from gui.reg_wind import SignUpWind


import sys

class SignWind(QtWidgets.QDialog):

    def __init__(self, monitor, parent = None):
        super().__init__(parent)
        # self.ui = uic.loadUi('gui/templates/sign_in.ui')
        self.monitor = monitor
        self.ui = ui_class()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)
        self.ui.login.setFocus()
        self.ui.ok.clicked.connect(self.login)
        self.ui.cancel.clicked.connect(sys.exit)
        self.ui.registration.clicked.connect(self.registration)

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

    def login(self):
        name = self.ui.login.text()
        password = self.ui.password.text()
        self.fields_checker(name, password, self)

    def registration(self):
        dialog = SignUpWind(self.monitor)
        dialog.exec()


