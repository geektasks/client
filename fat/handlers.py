import fat.handlers_base as handlers_base
"""
Инструкция по созданию функций-обработчиков сообщений

Методы, доступные в функциях-обработчиках (handler — экземпляр класса FatThing)
put_message(message) — поместить сообщение message в выходную очередь
send_message(message) — передать сообщение на сервер (message — строка или объект, поддерживающий сериализацию в json)
db — экземпляр класса ClientDB. По обращению к нему доступны все методы класса
block_queue() — заблокировать обработку сообщений из очереди
release_queue() — разблокировать обработку сообщений из очереди


A. Обработчик сообщений из очередиs
Вызывается при получении сообщения из очереди. 
    
    А.1 Обработчик по умолчанию
        Обработчик по умолчанию получает на обработку все сообщения, которые не получили условные обработчики,
        сообщеине — объект, помещенный в очередь
        
        Для назначения обработчика по умолчанию, установите перед функцией декоратор:
        декоратор — @handler.default_queue_handler
        
    А.2 Условный обработчик
        Получает на обработку сообщения, имеющие указанный тип и имя (сообщение — словарь, имеющий (помимо возможных
        прочих) ключ "head", по которому находится другой словарь, имеющий (помимо возможных прочих) два ключа: "type"
        и "name", определяющий соответственно тип и имя сообщения). Пример сообщения типа «action» с именем «hello»:
        message = {
            "head": {
                "type": "action",
                "name": "hello,
                "another key": "another value"
            },
            "another key": "some value"
        }
        
        Для назначения условного обработчика, установите перед функцией декоратор:
        @handler.conditional_queue_handler(type, name),
        где type — тип сообщения
            name — имя сообщения
        
В. Обработчик сообщений с сервера
Вызывается при получении сообщения от сервера.

    В.1 Обработчик по умолчанию
        Обработчик по умолчанию получает на обработку все сообщения, которые не получили условные обработчики,
        сообщеине — строка
        
        Для назначения обработчика по умолчанию, установите перед функцией (принимает сообщение) декоратор:
        декоратор — @handler.default_socket_handler
    
    В.2 Условный обработчик
        Получает на обработку сообщения, имеющие указанный тип и имя (сообщение — словарь, имеющий (помимо возможных
        прочих) ключ "head", по которому находится другой словарь, имеющий (помимо возможных прочих) два ключа: "type"
        и "name", определяющий соответственно тип и имя сообщения). Пример сообщения типа «action» с именем «hello»:
        message = {
            "head": {
                "type": "action",
                "name": "hello,
                "another key": "another value"
            },
            "another key": "some value"
        }
        
        Для назначения условного обработчика, установите перед функцией (принимает сообщение) декоратор:
        @handler.conditional_socket_handler(type, name),
        где type — тип сообщения
            name — имя сообщения
            
C. Инициализирующая функция
Вызывается в начале работы обработчика

Для назначения инициализирующей функции, установите перед функцией (без аргументов) декоратор:
@handler.init_func

D. Функция, вызываемая в случае отключенного червера
Вызывается при неудачном подключении к серверу

Для назначения инициализирующей функции, установите перед функцией (без аргументов) декоратор:
@handler.connection_refused_func
            
* декорируемые функции могут иметь одинаковые названия
"""

handler = handlers_base.FatThing("127.0.0.1", 8888, "my_db.sqlite")


# Пример инициализирующей функции
@handler.init_func
def init_func():
    print("Инициализирующая функция!!!")


# Пример назначения обработчика по умолчанию
@handler.default_queue_handler
def handler_func(message):
    print("Call default queue message handler. Message:", message)
    block_queue()
    send_message(message)


# Пример назначения условного обработчика
@handler.conditional_queue_handler("action", "hello")
def handler_func(message):
    print("Call conditional queue message handler (type — \"action\", name — \"hello\"). Message:", message)
    block_queue()
    send_message(message)


# Пример назначения обработчика по умолчанию
@handler.default_socket_handler
def handler_func(message):
    print("Call default socket message handler. Message:", message)
    put_message(message)
    release_queue()


# Пример назначения условного обработчика
@handler.conditional_socket_handler("action", "hello")
def handler_func(message):
    print("Call conditional socket message handler (type — \"action\", name — \"hello\"). Message:", message)
    put_message(message)
    release_queue()


# Пример функции, вызываемой при неудачном подключении к серверу
@handler.connection_refused_func
def handler_func():
    print("Can't connect...")