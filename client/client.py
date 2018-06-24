import logging
from time import sleep
import socket
import threading, queue
import hashlib

from jim.convert import json_to_bytes, bytes_to_json

logger = logging.getLogger('root')
send_queue = queue.Queue()



class Client():
    _username = ''

    def __init__(self, host, port):
        self._host = host
        self._port = port
        self.lock = threading.Lock()
        self.recv_queue = queue.Queue()
        self.send_queue = send_queue
        self.thereadRun=True

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def socket(self):
        return self._sock

    def _send_message(self):
        while self.thereadRun:
            data=False
            if not self.send_queue.empty():
                data = self.send_queue.get(timeout=0.2)
            if data:
                msg = json_to_bytes(data)
                self.socket.send(msg)
                print('sent: ', msg)
            self.send_queue.task_done()

    def _get_message(self):

        # получение сообщений от сервера, пока только вывод в консоль, сервер без бд поэтому просто пересылает сообщение

        sock = self.socket
        cont_l = []
        while self.thereadRun:
            try:
                if not self.recv_queue.full():
                    sock.settimeout(12)
                    data_recv = sock.recv(1400)
                    data_recv = bytes_to_json(data_recv)
                    print('received: ', data_recv)  ###########
                    self.recv_queue.put(data_recv)
                else:
                    print('Очердь полна, спим')
                    sleep(0.5)
            except socket.timeout:
                pass

    def start_thread(self):
        self.t1 = threading.Thread(target=self._send_message)
        self.t2 = threading.Thread(target=self._get_message)
        self.t1.daemon = True
        self.t2.daemon = True
        self.t1.start()
        self.t2.start()

    def run(self):
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self._host, self._port))
            logger.debug('Client is connected to server: {}:{}'.format(self._host, self._port))
            self.start_thread()
        except:
            return 'Сервер не отвечает'
    def stop(self):
        self.thereadRun=False
        print('s0')
        self.t1.join()
        print('s1')
        self.t2.join()
        print('s3')
        return 0


if __name__ == '__main__':
    pass
