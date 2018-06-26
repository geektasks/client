import asyncio
import queue
import json
import threading
import time
import concurrent.futures


class FatThing(asyncio.Protocol):

    SOCKET_HANDLERS = {}
    DEFAULT_SOCKET_HANDLER = lambda *args, **kwargs: None
    QUEUE_HANDLERS = {}
    DEFAULT_QUEUE_HANDLER = lambda *args, **kwargs: None
    INIT_FUNC = lambda *args, **kwargs: None
    STOP_FUNC = lambda *args, **kwargs: None
    CONNECTION_REFUSED = lambda *args, **kwargs: None
    PERIODIC_FUNC = []
    CALLS = []

    def __init__(self, host, port):
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        self.data = {'session_id': None, 'username': None}
        self._host = host
        self._port = port
        self._transport = None
        self._loop = asyncio.get_event_loop()
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self._queue_handling_event = asyncio.Event(loop=self._loop)
        self._queue_handling_event.set()
        self._connect()
        self._loop.create_task(self._queue_handler_loop())

    async def _timer(self):
        """
        Хз, зачем оно надо, но без него не работает. Нужно советоваться с опытными питонистами :(
        :return: None
        """
        while True:
            await asyncio.sleep(10)

    def _connect(self):
        """
        Подключиться к серверу
        :return: None
        """
        if self._transport is None:
            self._loop.create_task(self._create_connection())

    async def _create_connection(self):
        """
        Создать подключение к серверу
        :return: None
        """
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
        except (TypeError, KeyError):
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
            await self._queue_handling_event.wait()
            self._handle_queue_message(message)

    def _lock_queue_handle(self):
        """
        Заблокировать обработку сообщений из очереди
        :return: None
        """
        if self._queue_handling_event.is_set():
            self._queue_handling_event.clear()

    def _release_queue_handle(self):
        """
        Разблокировать обработку сообщений из очереди
        :return:
        """
        if not self._queue_handling_event.is_set():
            self._queue_handling_event.set()

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

    def _stop(self):
        """
        Завершение работы обработчика
        :return: None
        """
        self.STOP_FUNC()
        self.input_queue.put(None)
        for func in self.PERIODIC_FUNC:
            func.cancel()
        for func in self.CALLS:
            func.cancel()
        self._loop.stop()

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
            func.__globals__["block_queue"] = handler._lock_queue_handle
            func.__globals__["release_queue"] = handler._release_queue_handle
            func.__globals__["data"] = handler.data
            func.__globals__["call_later"] = handler._call_later
            func.__globals__["call_at"] = handler._call_at

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
        func.__globals__["block_queue"] = self._lock_queue_handle
        func.__globals__["release_queue"] = self._release_queue_handle
        func.__globals__["data"] = self.data
        func.__globals__["call_later"] = self._call_later
        func.__globals__["call_at"] = self._call_at

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
            func.__globals__["block_queue"] = handler._lock_queue_handle
            func.__globals__["release_queue"] = handler._release_queue_handle
            func.__globals__["data"] = handler.data
            func.__globals__["call_later"] = handler._call_later
            func.__globals__["call_at"] = handler._call_at

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
        func.__globals__["block_queue"] = self._lock_queue_handle
        func.__globals__["release_queue"] = self._release_queue_handle
        func.__globals__["data"] = self.data
        func.__globals__["call_later"] = self._call_later
        func.__globals__["call_at"] = self._call_at

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
        func.__globals__["block_queue"] = self._lock_queue_handle
        func.__globals__["release_queue"] = self._release_queue_handle
        func.__globals__["data"] = self.data
        func.__globals__["call_later"] = self._call_later
        func.__globals__["call_at"] = self._call_at

        self.INIT_FUNC = func
        print("Function \"{}\" assigned as init func.".format(func.__name__))
        return func

    def stop_func(self, func):
        """
        Назначить инициализирующую функцию-обработчик
        :param func: назначаемая функция
        :return: назначаемая функция
        """
        func.__globals__["send_message"] = self._send_message
        func.__globals__["put_message"] = self.output_queue.put
        func.__globals__["block_queue"] = self._lock_queue_handle
        func.__globals__["release_queue"] = self._release_queue_handle
        func.__globals__["data"] = self.data
        func.__globals__["call_later"] = self._call_later
        func.__globals__["call_at"] = self._call_at

        self.STOP_FUNC = func
        print("Function \"{}\" assigned as stop func.".format(func.__name__))
        return func

    def connection_refused_func(self, func):
        """
        Назначить инициализирующую функцию-обработчик
        :param func: назначаемая функция
        :return: назначаемая функция
        """
        func.__globals__["send_message"] = self._send_message
        func.__globals__["put_message"] = self.output_queue.put
        func.__globals__["block_queue"] = self._lock_queue_handle
        func.__globals__["release_queue"] = self._release_queue_handle
        func.__globals__["data"] = self.data
        func.__globals__["call_later"] = self._call_later
        func.__globals__["call_at"] = self._call_at

        self.CONNECTION_REFUSED = func
        print("Function \"{}\" assigned as connection refused func.".format(func.__name__))
        return func

    def periodic_func(self, period_time, with_start=True):
        """
        Назначить перидическую функцию
        :param period_time: период вызова функции
        :param with_start: первый вызов произойдет при старте
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
            func.__globals__["block_queue"] = handler._lock_queue_handle
            func.__globals__["release_queue"] = handler._release_queue_handle
            func.__globals__["data"] = handler.data
            func.__globals__["call_later"] = handler._call_later
            func.__globals__["call_at"] = handler._call_at

            async def periodic_func():

                if with_start:
                    func()

                while True:
                    await asyncio.sleep(period_time)
                    func()

            handler.PERIODIC_FUNC.append(handler._loop.create_task(periodic_func()))

            print("Function \"{}\" assigned as periodic one with {} sec. period.".format(func.__name__, period_time))

            return func

        return assignator

    def _call_later(self, delay_time, *args, data_name=None):
        """
        Назначить функцию, вызываемую через промежуток времени
        :param delay_time: промежуток времени (в секундах)
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
            func.__globals__["block_queue"] = handler._lock_queue_handle
            func.__globals__["release_queue"] = handler._release_queue_handle
            func.__globals__["data"] = handler.data
            func.__globals__["call_later"] = handler._call_later
            func.__globals__["call_at"] = handler._call_at

            handler.CALLS.append(handler._loop.call_later(delay_time, func, *args))

            print("Function \"{}\" will call after {} sec.".format(func.__name__, delay_time))

            if data_name is not None:
                handler.data[data_name] = func_call
                print("Function \"{}\" put in data as \"{}\", so you can cancel call.".format(func.__name__, data_name))

            return func

        return assignator

    def _call_at(self, call_time, *args, data_name=None):
        """
        Назначить функцию, вызываемую в определенный момент времени
        :param delay_time: момент времени (в секундах(
        :return: назначающая функция
        """

        handler = self
        loop_time = call_time - time.time() + self._loop.time()

        def assignator(func):
            """
            Назначающая функция
            :param func: назначаемая функция
            :return: назначаемая функция
            """
            func.__globals__["send_message"] = handler._send_message
            func.__globals__["put_message"] = handler.output_queue.put
            func.__globals__["block_queue"] = handler._lock_queue_handle
            func.__globals__["release_queue"] = handler._release_queue_handle
            func.__globals__["data"] = handler.data
            func.__globals__["call_later"] = handler._call_later
            func.__globals__["call_at"] = handler._call_at

            func_call = handler._loop.call_at(loop_time, func, *args)
            handler.CALLS.append(func_call)

            print("Function \"{}\" will call at ".format(func.__name__) + time.strftime("%d.%m.%Y %H:%M:%S"))

            if data_name is not None:
                handler.data[data_name] = func_call
                print("Function \"{}\" put in data as \"{}\", so you can cancel call.".format(func.__name__, data_name))

            return func

        return assignator

    def run(self):
        """
        Запустить обработчик в отделном процессе
        :return: None
        """
        self._loop.call_soon(self.INIT_FUNC)
        self._loop.create_task(self._timer())
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._thread.start()

    def stop(self):
        """
        Остановить работу обработчика
        :return: None
        """
        self._loop.call_soon(self._stop)
        # self._thread.join()
