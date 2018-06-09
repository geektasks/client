import asyncio
import queue
import json
import threading
import db.client_db as client_db
import concurrent.futures


class FatThing(asyncio.Protocol):

    SOCKET_HANDLERS = {}
    DEFAULT_SOCKET_HANDLER = lambda *args, **kwargs: None
    QUEUE_HANDLERS = {}
    DEFAULT_QUEUE_HANDLER = lambda *args, **kwargs: None
    INIT_FUNC = lambda *args, **kwargs: None
    CONNECTION_REFUSED = lambda *args, **kwargs: None

    def __init__(self, host, port, db_name):
        self.db = client_db.ClientDB.create_db(db_name)
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        self.data = {}
        self._host = host
        self._port = port
        self._transport = None
        self._loop = asyncio.get_event_loop()
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self._event = asyncio.Event()
        self._event.set()
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
            self.QUEUE_HANDLERS[message["head"]["type"]][message["head"]["name"]](message)
        except TypeError:
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
        while True:
            message = await self._loop.run_in_executor(self._executor, self.input_queue.get)
            await self._event.wait()
            self._handle_queue_message(message)

    def _lock_queue_handle(self):
        """
        Заблокировать обработку сообщений из очереди
        :return: None
        """
        if self._event.is_set():
            self._event.clear()

    def _release_queue_handle(self):
        """
        Разблокировать обработку сообщений из очереди
        :return:
        """
        if not self._event.is_set():
            self._event.set()

    def _send_message(self, message):
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
            self._loop.call_later(1, self._connect)
            self._loop.call_later(2, self._send_message, message)

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
            func.__globals__["send_message"] = handler._send_message
            func.__globals__["put_message"] = handler.output_queue.put
            func.__globals__["db"] = handler.db
            func.__globals__["block_queue"] = handler._lock_queue_handle
            func.__globals__["release_queue"] = handler._release_queue_handle
            func.__globals__["data"] = handler.data
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
        func.__globals__["send_message"] = self._send_message
        func.__globals__["put_message"] = self.output_queue.put
        func.__globals__["db"] = self.db
        func.__globals__["block_queue"] = self._lock_queue_handle
        func.__globals__["release_queue"] = self._release_queue_handle
        func.__globals__["data"] = self.data
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
            func.__globals__["send_message"] = handler._send_message
            func.__globals__["put_message"] = handler.output_queue.put
            func.__globals__["db"] = handler.db
            func.__globals__["block_queue"] = handler._lock_queue_handle
            func.__globals__["release_queue"] = handler._release_queue_handle
            func.__globals__["data"] = handler.data
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
        func.__globals__["send_message"] = self._send_message
        func.__globals__["put_message"] = self.output_queue.put
        func.__globals__["db"] = self.db
        func.__globals__["block_queue"] = self._lock_queue_handle
        func.__globals__["release_queue"] = self._release_queue_handle
        func.__globals__["data"] = self.data
        self.DEFAULT_QUEUE_HANDLER = func
        print("Function \"{}\" assigned as queue handler default.".format(func.__name__))
        return func

    def init_func(self, func):
        """
        Назначить инициализирующую функцию-обработчик
        :param func: назначаемая функция
        :return: назначаемая функция
        """
        func.__globals__["send_message"] = self._send_message
        func.__globals__["put_message"] = self.output_queue.put
        func.__globals__["db"] = self.db
        func.__globals__["block_queue"] = self._lock_queue_handle
        func.__globals__["release_queue"] = self._release_queue_handle
        func.__globals__["data"] = self.data
        self.INIT_FUNC = func
        print("Function \"{}\" assigned as init func.".format(func.__name__))
        return func

    def connection_refused_func(self, func):
        """
        Назначить инициализирующую функцию-обработчик
        :param func: назначаемая функция
        :return: назначаемая функция
        """
        func.__globals__["send_message"] = self._send_message
        func.__globals__["put_message"] = self.output_queue.put
        func.__globals__["db"] = self.db
        func.__globals__["block_queue"] = self._lock_queue_handle
        func.__globals__["release_queue"] = self._release_queue_handle
        func.__globals__["data"] = self.data
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
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._thread.start()

    def stop(self):
        """
        Остановить работу обработчика
        :return: None
        """
        self._loop.stop()
        self.input_queue.put(None)



