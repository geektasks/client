import time, sys
import socket
import threading, queue
import hashlib

from jim.convert import json_to_bytes, bytes_to_json

class Client():

    username = ''

    def __init__(self, host, port):
        self._host = host
        self._port = port
        self.lock = threading.Lock()
        self.recv_queue = queue.Queue()
        self.secret = 'secretkey'

    @property
    def socket(self):
        return self._sock

    def connect_guest(self, name, password):
        # Функция авторизации пользователя
        pass

    def registration(self, name, password, email):
        pas = hashlib.sha256()
        pas.update(self.username.encode())
        pas.update(password.encode())
        pas.update(self.secret.encode())
        password = pas.hexdigest()
        message = {
            "head": {
                "type": "action",
                "name": "registration"
            },
            "body": {
                "name": name,
                "password": password
            }
        }
        message = json_to_bytes(message)
        self.socket.send(message)

    def check_user(self, name):
        message = {
            "head": {
                "type": "action",
                "name": "check_user"
            },
            "body": {
                "name": name
            }
        }
        msg = json_to_bytes(message)
        # time.sleep(0.2)  # непонятная задержка которая нужна при JSON
        self.socket.send(msg)

    def add_task(self):
        # функция добавления задачи
        pass


    def _get_message(self):

        #получение сообщений от сервера, пока только вывод в консоль, сервер без бд поэтому просто пересылает сообщение

        sock = self.socket
        cont_l = []
        while True:
            try:
                sock.settimeout(12)
                data_recv = sock.recv(1024)
                data_recv = bytes_to_json(data_recv)
                self.recv_queue.put(data_recv)

            except socket.timeout:
                pass

    def start_thread(self):
        t2 = threading.Thread(target=self._get_message)
        t2.daemon = True
        t2.start()


    def run(self):
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self._host, self._port))
            print('подключился к {}:{}'.format(self._host, self._port))
            self.start_thread()
        except:
            return 'Сервер не отвечает'