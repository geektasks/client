import sys
import threading
from PyQt5 import QtCore, QtWidgets, uic, QtGui
from PyQt5.QtCore import QDate, QTime
from gui.templates.main_form import Ui_MainWindow as ui_class
from time import sleep

# from gui.monitor import Monitor
from fat.handlers import handler
import function.requests as request


class MyWindow(QtWidgets.QMainWindow):
    gotCheck = QtCore.pyqtSignal(dict)
    gotConsole = QtCore.pyqtSignal(dict)
    gotErrorRegistration = QtCore.pyqtSignal(dict)
    gotCreatedTask = QtCore.pyqtSignal(dict)
    gotUpdateTaskList = QtCore.pyqtSignal(dict)
    gotAutorization = QtCore.pyqtSignal(dict)
    gotEditedTask = QtCore.pyqtSignal(dict)
    gotTaskId = QtCore.pyqtSignal(dict)
    gotSearchUser = QtCore.pyqtSignal(dict)
    gotPerformer = QtCore.pyqtSignal(dict)  ################################
    gotWatcher = QtCore.pyqtSignal(dict)  ################################
    gotAllPerformers = QtCore.pyqtSignal(dict)  ################################
    gotAllWatchers = QtCore.pyqtSignal(dict)  ################################

    def __init__(self, parent=None):

        super().__init__(parent)
        self.ui = ui_class()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)

        self.NAME = {
            'registration': self.gotConsole,
            'registration error': self.gotErrorRegistration,
            'authorization': self.gotAutorization,
            'check user': self.gotCheck,
            'create task': self.gotCreatedTask,
            'get all tasks': self.gotUpdateTaskList,
            'get task by id': self.gotTaskId,
            'edit task': self.gotEditedTask,
            'search user': self.gotSearchUser,
            'assign performer': self.gotPerformer,  ################################
            'grant access': self.gotWatcher,  ################################
            'get all performers': self.gotAllPerformers,  ################################
            'get all watchers': self.gotAllWatchers  ################################
        }
        self.runThread=True
        self.handler = handler
        self.start_handler()
        self.start_monitor()

        self.ui.action_login.triggered.connect(self.sign_in)
        self.ui.action_exit.triggered.connect(self.exit)

        self.ui.taskList.doubleClicked.connect(self.task)

        self.gotConsole.connect(self.update_console)
        self.gotErrorRegistration.connect(self.update_error)
        self.gotCreatedTask.connect(self.created_task_response)
        self.gotUpdateTaskList.connect(self.update_tasks_list)
        self.gotAutorization.connect(self.autorization_request)
        self.gotEditedTask.connect(self.edited_task_response)
        self.gotPerformer.connect(self.added_performer)  ################################
        self.gotWatcher.connect(self.added_watcher)  ################################
        # self.gotAllPerformers.connect(self.update_performers)
        # self.gotAllWatchers.connect(self.update_watchers)


    def start_monitor(self):
        self.t1 = threading.Thread(target=self.monitor)
        self.t1.daemon = True
        self.t1.start()

    def start_handler(self):
        self.handler.run()
        self.input_queue = self.handler.input_queue
        self.output_queue = self.handler.output_queue

    def closeEvent(self, e):
        result = QtWidgets.QMessageBox.question(self,
                                                "Confirmation",
                                                "Do you really want to close window with tasks?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                QtWidgets.QMessageBox.No)
        if result == QtWidgets.QMessageBox.Yes:
            self.handler.stop()
            e.accept()
            QtWidgets.QWidget.closeEvent(self, e)
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
        while self.runThread:
            data = False
            if not self.output_queue.empty():
                data = self.output_queue.get(timeout=0.2)
            if data:
                print('обрабатываем в гуи', data)
                body = data['body']
                try:
                    if data['head']['name'] in self.NAME:
                        print('будем обрабатывать', data['head']['name'])
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
        # pixmap = QtGui.QPixmap('gui/icon/error.png')
        # dialog_reg.label_4.resize(23, 23)
        # dialog_reg.label_4.setPixmap(pixmap)
        dialog_reg.flag = None

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
            if text == '':
                pixmap = QtGui.QPixmap('gui/icon/error.png')
                dialog_reg.label_4.resize(23, 23)
                dialog_reg.label_4.setPixmap(pixmap)
                dialog_reg.flag = None
            else:
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
    def exit(self):
        print(0)
        self.runThread=False
        print(1)
        self.t1.join()
        print(2)
        self.handler.stop()
        print(3)
        sys.exit(0)
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

    def task(self):
        dialog = uic.loadUi('gui/templates/task_create.ui')

        try:
            current_date = QDate.currentDate()
            dialog.dateEdit.setDate(current_date)
            dialog.dateEdit_2.setDate(current_date)
            dialog.dateEdit_3.setDate(current_date)
            current_time = QTime.currentTime()
            dialog.timeEdit.setTime(current_time)
        except Exception as err:
            print(err)

        task = self.ui.taskList.currentItem().text()
        task = task.split(' ', maxsplit=1)
        task_id = int(task[0])  # server_task_id
        task_name = task[1]
        message = request.get_task_by_id(task_id)
        self.input_queue.put(message)

        message = request.get_all_performers(task_id=task_id)  ################################
        self.input_queue.put(message)  ################################

        message = request.get_all_watchers(task_id=task_id)  ################################
        self.input_queue.put(message)  ################################

        @QtCore.pyqtSlot(dict)  ################################
        def update_performers(body):
            dialog.listPeople.clear()
            for performer in body['performers']:
                print('performer:', performer)
                dialog.listPeople.addItem(performer)

        @QtCore.pyqtSlot(dict)  ################################
        def update_watchers(body):
            dialog.listPeople.clear()
            for watcher in body['watchers']:
                print('watcher:', watcher)
                dialog.listPeople.addItem(watcher)  # чтобы не дублировать с исполнителями

        self.gotAllPerformers.connect(update_performers)  ################################
        self.gotAllWatchers.connect(update_watchers)  ################################

        dialog.topic.setText(task_name)
        dialog.addTask.setFocus()

        def task_update():
            topic = dialog.topic.text()
            description = dialog.description.toPlainText()
            if topic != task_name:
                message = request.edit_task(task_id=task_id, name=topic)
                self.input_queue.put(message)
            if description:
                message = request.edit_task(task_id=task_id, description=description)
                self.input_queue.put(message)

        @QtCore.pyqtSlot(dict)
        def get_task(body):
            dialog.description.setText(body['description'])

        def add_people():
            dialog = uic.loadUi('gui/templates/users.ui')

            def search_user():
                text = dialog.userName.text()
                dialog.listUser.clear()
                message = request.search_user(text)
                self.input_queue.put(message)

            @QtCore.pyqtSlot(dict)
            def update_user(body):
                print(body)
                for user in body['users']:
                    dialog.listUser.addItem(user)

            def add():  ################################
                # отправляем запросы одновременно на performer и watcher
                # task_id = server_task_id
                username = dialog.listUser.currentItem().text()
                message = request.assign_performer(task_id=task_id, user=username)
                self.input_queue.put(message)
                message = request.grant_access(task_id=task_id, user=username)
                self.input_queue.put(message)
                dialog.close()

            self.gotSearchUser.connect(update_user)

            dialog.listUser.doubleClicked.connect(add)
            dialog.userName.textChanged.connect(search_user)
            dialog.exec()

        self.gotTaskId.connect(get_task)
        dialog.addPeople.clicked.connect(add_people)
        dialog.addTask.clicked.connect(task_update)
        dialog.addTask.clicked.connect(dialog.accept)
        dialog.cancel.clicked.connect(dialog.close)
        dialog.exec()

    def get_all_task(self):
        self.ui.taskList.clear()
        message = request.get_all_tasks()
        print('get all tasks from gui', message)
        self.input_queue.put(message)

    def get_all_performers(self):
        print('отправляю запрос на всех исполнителей')
        task = self.ui.taskList.currentItem().text()
        task = task.split(' ', maxsplit=1)
        task_id = int(task[0])  # server_task_id
        message = request.get_all_performers(task_id=task_id)
        self.input_queue.put(message)


    def get_all_watchers(self):
        print('отправляю запрос на всех наблюдателей')
        task = self.ui.taskList.currentItem().text()
        task = task.split(' ', maxsplit=1)
        task_id = int(task[0])  # server_task_id
        message = request.get_all_watchers(task_id=task_id)
        self.input_queue.put(message)

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

    @QtCore.pyqtSlot(dict)
    def created_task_response(self, body):
        if body['code'] == 201:
            self.get_all_task()
        else:
            self.update_console(body)

    @QtCore.pyqtSlot(dict)
    def update_tasks_list(self, body):
        for task_key, task_value in body['message'].items():
            self.ui.taskList.addItem('{} {}'.format(task_key, task_value))

    @QtCore.pyqtSlot(dict)
    def autorization_request(self, body):
        if body['code'] == 200:
            self.get_all_task()
            self.update_console(body)
        else:
            self.update_console(body)

    # баг: если редактировать одновременно имя и описание,
    # то задача дублируется в списке
    @QtCore.pyqtSlot(dict)
    def edited_task_response(self, body):
        if body['code'] == 200:
            self.get_all_task()
            self.update_console(body)

    @QtCore.pyqtSlot(dict)  ################################
    def added_performer(self, body):
        if body['code'] == 200:
            self.get_all_performers()
            self.update_console(body)

    @QtCore.pyqtSlot(dict)  ################################
    def added_watcher(self, body):
        if body['code'] == 200:
            self.get_all_watchers()
            self.update_console(body)
