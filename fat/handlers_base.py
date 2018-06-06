import asyncio
import queue
import json
import threading
import db.client_db as client_db


class FatThing(asyncio.Protocol):

    SOCKET_HANDLERS = {}
    DEFAULT_SOCKET_HANDLER = lambda self, x: x
    QUEUE_HANDLERS = {}
    DEFAULT_QUEUE_HANDLER = lambda self, x: x
    INIT_FUNC = lambda self: self
    CONNECTION_REFUSED = lambda self: self

    def __init__(self, host, port, db_name):
        self.db = client_db.ClientDB.create_db(db_name)
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        self.info = {}
        self._host = host
        self._port = port
        self._transport = None
        self._loop = asyncio.get_event_loop()
        self._lock = asyncio.Lock()
        self._connect()
        self._loop.create_task(self._queue_handler_loop())

    def _connect(self):
        """
        Подключиться к серверу
        :return: None
        """
        if self._transport is None:
            self._loop.create_task(self._create_connection())

    async def _create_connection(self):
        try:
            await self._loop.create_connection(lambda: self, self._host, self._port)
        except ConnectionRefusedError:
            self.CONNECTION_REFUSED()

    def _handle_socket_message(self, message):
        """
        Менеджер-обработчик. Передает сообщение на обработку конкретной функции
        :param message: сообщение, полуенной из очереди
        :return: None
        """
        try:
            load_message = json.loads(message)
            self.SOCKET_HANDLERS[load_message["head"]["type"]][load_message["head"]["name"]](load_message)
        except (json.decoder.JSONDecodeError, TypeError, KeyError):
            self.DEFAULT_SOCKET_HANDLER(message)

    def _handle_queue_message(self, message):
        """
        Менеджер-обработчик. Передает сообщение на обработку конкретной функции
        :param message: сообщение, полуенной из очереди
        :return: None
        """
        try:
            load_message = json.loads(message)
            self.QUEUE_HANDLERS[load_message["head"]["type"]][load_message["head"]["name"]](load_message)
        except (json.decoder.JSONDecodeError, TypeError, KeyError):
            self.DEFAULT_QUEUE_HANDLER(message)

    async def _queue_handler_loop(self):
        """
        Петля событий, получающая сообщения из очереди и вызывающая менеджер-обработчик
        :return: None
        """
        while self._loop.is_running():
            message = await self._loop.run_in_executor(None, self.input_queue.get)
            if not self._loop.is_running():
                break
            await self._lock.acquire()
            self._lock.release()
            self._handle_queue_message(message)
        print("КОНЕЦ")

    def _lock_queue_handle(self):
        """
        Заблокировать обработку сообщений из очереди
        :return: None
        """
        if not self._lock.locked():
            self._loop.create_task(self._lock.acquire())
        asyncio.sleep(0)

    def _release_queue_handle(self):
        """
        Разблокировать обработку сообщений из очереди
        :return:
        """
        if self._lock.locked():
            self._lock.release()

    def connection_made(self, transport):
        """
        Функция, вызываемая при создании подключения к серверу
        :param transport: транспорт-сокет
        :return: None
        """
        self._transport = transport
        print("Connected to server.")

    def data_received(self, data):
        """
        Функция, вызываемая при получении сообщения от сервера, вызывающая менеджер-обработчик
        :param data: данные, полученные от сервера
        :return: None
        """
        message = data.decode()
        print('Data received:', message)
        self._handle_socket_message(message)

    def connection_lost(self, exc):
        """
        Функция, вызываемая при потере соединения
        :param exc: исключение
        :return: None
        """
        self._transport = None
        print('The server closed the connection. Try to reconnect.')
        self._loop.call_later(5, self._connect)

    def conditional_socket_handler(self, type, name):
        """
        Назначить функцию-обработчик сообщений с сервера
        :param type: тип сообщения
        :param name: имя сообщения
        :return: назначающая функция
        """
        handler = self

        def assignator(func):
            """
            Назначающая функция
            :param func: назначаемая функция
            :return: назначаемая функция
            """
            func.__globals__["send_message"] = handler.send_message
            func.__globals__["put_message"] = handler.output_queue.put
            func.__globals__["db"] = handler.db
            func.__globals__["block_queue"] = handler._lock_queue_handle
            func.__globals__["release_queue"] = handler._release_queue_handle
            handler.SOCKET_HANDLERS[type] = handler.SOCKET_HANDLERS.get(type, {})
            handler.SOCKET_HANDLERS[type][name] = func
            print("Function \"{}\" assigned as handler messages type \"{}\" with name \"{}\".".format(func.__name__, type, name))
            return func

        return assignator

    def default_socket_handler(self, func):
        """
        Назначить функцию-обработчик сообщений с сервера по умолчанию
        :param func: назначаемая функция
        :return: назначаемая функция
        """
        func.__globals__["send_message"] = self.send_message
        func.__globals__["put_message"] = self.output_queue.put
        func.__globals__["db"] = self.db
        func.__globals__["block_queue"] = self._lock_queue_handle
        func.__globals__["release_queue"] = self._release_queue_handle
        self.DEFAULT_SOCKET_HANDLER = func
        print("function \"{}\" assigned as socket handler default.".format(func.__name__))
        return func

    def conditional_queue_handler(self, type, name):
        """
        Назначить функцию-обработчик сообщений из очереди
        :param type: тип сообщения
        :param name: имя сообщения
        :return: назначающая функция
        """
        handler = self

        def assignator(func):
            """
            Назначающая функция
            :param func: назначаемая функция
            :return: назначаемая функция
            """
            func.__globals__["send_message"] = handler.send_message
            func.__globals__["put_message"] = handler.output_queue.put
            func.__globals__["db"] = handler.db
            func.__globals__["block_queue"] = handler._lock_queue_handle
            func.__globals__["release_queue"] = handler._release_queue_handle
            handler.QUEUE_HANDLERS[type] = handler.QUEUE_HANDLERS.get(type, {})
            handler.QUEUE_HANDLERS[type][name] = func
            print("Function \"{}\" assigned as handler messages type \"{}\" with name \"{}\".".format(func.__name__, type, name))
            return func

        return assignator

    def default_queue_handler(self, func):
        """
        Назначить функцию-обработчик сообщений из очереди по умолчанию
        :param func: назначаемая функция
        :return: назначаемая функция
        """
        func.__globals__["send_message"] = self.send_message
        func.__globals__["put_message"] = self.output_queue.put
        func.__globals__["db"] = self.db
        func.__globals__["block_queue"] = self._lock_queue_handle
        func.__globals__["release_queue"] = self._release_queue_handle
        self.DEFAULT_QUEUE_HANDLER = func
        print("Function \"{}\" assigned as queue handler default.".format(func.__name__))
        return func

    def init_func(self, func):
        """
        Назначить инициализирующую функцию-обработчик
        :param func: назначаемая функция
        :return: назначаемая функция
        """
        func.__globals__["send_message"] = self.send_message
        func.__globals__["put_message"] = self.output_queue.put
        func.__globals__["db"] = self.db
        func.__globals__["block_queue"] = self._lock_queue_handle
        func.__globals__["release_queue"] = self._release_queue_handle
        self.INIT_FUNC = func
        print("Function \"{}\" assigned as init func.".format(func.__name__))
        return func

    def connection_refused_func(self, func):
        """
        Назначить инициализирующую функцию-обработчик
        :param func: назначаемая функция
        :return: назначаемая функция
        """
        func.__globals__["send_message"] = self.send_message
        func.__globals__["put_message"] = self.output_queue.put
        func.__globals__["db"] = self.db
        func.__globals__["block_queue"] = self._lock_queue_handle
        func.__globals__["release_queue"] = self._release_queue_handle
        self.CONNECTION_REFUSED = func
        print("Function \"{}\" assigned as init func.".format(func.__name__))
        return func

    def run(self):
        """
        Запустить обработчик в отделном процессе
        :return: None
        """
        self._loop.call_soon(self.db.connect)
        self._loop.call_soon(self.INIT_FUNC)
        self._thread = threading.Thread(target=self._loop.run_forever)
        self._thread.start()

    def stop(self):
        """
        Остановить работу обработчика
        :return:
        """
        self.input_queue.put(None)
        self._loop.stop()

    def send_message(self, message):
        """
        Передать сообщение на сервера
        :param message: сообщение (строка)
        :return: None
        """
        try:
            data = message.encode()
        except AttributeError:
            message = json.dumps(message)
            data = message.encode()
        try:
            self._transport.write(data)
            print('Send data to server:', message)
        except AttributeError:
            self._loop.call_later(5, self._connect)
            self._loop.call_later(6, self.send_message, message)
