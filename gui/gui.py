import sys
import threading
from PyQt5 import QtCore, QtWidgets, uic, QtGui
from gui.templates.main_form import Ui_MainWindow as ui_class

# from gui.monitor import Monitor
from fat.handlers import handler
import function.requests as request



class MyWindow(QtWidgets.QMainWindow):
    gotCheck = QtCore.pyqtSignal(dict)
    gotConsole = QtCore.pyqtSignal(dict)
    gotError = QtCore.pyqtSignal(dict)

    def __init__(self, parent = None):

        super().__init__(parent)
        self.ui = ui_class()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)

        self.NAME = {
            'registration': self.gotConsole,
            'registration error': self.gotError,
            'authorization': '',
            'check user': self.gotCheck}


        self.handler = handler
        self.start_handler()
        self.start_monitor()

        self.ui.action_login.triggered.connect(self.sign_in)

        self.gotConsole.connect(self.update_console)
        self.gotError.connect(self.update_error)

    def start_monitor(self):
        t1 = threading.Thread(target= self.monitor)
        t1.daemon = True
        t1.start()

    def start_handler(self):
        self.handler.run()
        self.input_queue = self.handler.input_queue
        self.output_queue = self.handler.output_queue

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

    ####################################################################################################################
    ########функция обработки сообщений от сервера################################################################
    ####################################################################################################################
    def monitor(self):
        while 1:
            data = self.output_queue.get()
            print(data)
            body = data['body']
            try:
                if data['head']['name'] in self.NAME:
                    print(data['head']['name'])
                    controller = self.NAME.get(data['head']['name'])
                    print('сообщение для вывода в гуи', data)
                    controller.emit(body)
                else:
                    print(data['head']['name'])
                    print('unknown_response')
            except Exception as err:
                print(err)
    ####################################################################################################################

    def registration(self):
        dialog_reg = uic.loadUi('gui/templates/sign_up.ui')
        dialog_reg.login.setFocus()
        dialog_reg.flag = True

        def reg():
            name = dialog_reg.login.text()
            password = dialog_reg.password.text()
            email = dialog_reg.email.text()
            self.fields_checker(name, password, dialog_reg)
            if dialog_reg.flag:
                message = request.registration(name=name, password=password, email=email)
                self.input_queue.put(message)
            else:
                QtWidgets.QMessageBox.warning(dialog_reg, 'Warning!', 'Uncorrect name')
                self.registration()

        def check_login():
            text = dialog_reg.login.text()
            message = request.check_user(text)
            self.input_queue.put(message)

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
            message = request.authorization(name=name, password=password)
            self.input_queue.put(message)

        dialog.ok.clicked.connect(login)
        dialog.registration.clicked.connect(dialog.close)
        dialog.registration.clicked.connect(self.registration)
        dialog.cancel.clicked.connect(sys.exit)
        dialog.exec()

    def on_createTask_pressed(self):
        dialog = uic.loadUi('gui/templates/task_create.ui')
        dialog.topic.setFocus()

        def task_create():
            topic = dialog.topic.text()
            description = dialog.description.toPlainText()
            message = request.create_task(name=topic, description=description)
            self.input_queue.put(message)

        dialog.addTask.clicked.connect(task_create)
        dialog.addTask.clicked.connect(dialog.accept)
        dialog.exec()

        ###############################################################################################################
        ############## функции обработки сообщений от сервера, запускаются по сигналу от функции обработчика###########
        ###############################################################################################################

    @QtCore.pyqtSlot(dict)
    def update_console(self, body):
        self.ui.statusbar.showMessage('{} - {}'.format(body['code'], body['message']))

    @QtCore.pyqtSlot(dict)
    def update_error(self, body):
        QtWidgets.QMessageBox.warning(QtWidgets.QDialog(), 'Warning!', body['message'])
        # sys.exit()
        self.registration()
