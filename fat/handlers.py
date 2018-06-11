import fat.handlers_base as handlers_base

"""
Инструкция по созданию функций-обработчиков сообщений

Методы, доступные в функциях-обработчиках (handler — экземпляр класса FatThing)
put_message(message) — поместить сообщение message в выходную очередь
send_message(message) — передать сообщение на сервер (message — строка или объект, поддерживающий сериализацию в json)
db — экземпляр класса ClientDB. По обращению к нему доступны все методы класса
block_queue() — заблокировать обработку сообщений из очереди
release_queue() — разблокировать обработку сообщений из очереди
data — словарь для хранения чего угодно :)


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

# handler = handlers_base.FatThing("127.0.0.1", 8888, "my_db.sqlite")
# handler = handlers_base.FatThing("127.0.0.1", 8000, "my_db.sqlite")


handler = handlers_base.FatThing("ddimans.dyndns.org", 8000, "my_db.sqlite")


@handler.conditional_queue_handler("action", "registration")
def registration(message):
    username = message['body']['name']
    data['username'] = username
    block_queue()
    send_message(message)


@handler.conditional_queue_handler("action", "authorization")
def authorization(message):
    username = message['body']['name']
    data['username'] = username
    block_queue()
    send_message(message)


@handler.conditional_socket_handler("server response", "authorization")
def authorization(message):
    session_id = message['body']['session id']
    data['session_id'] = int(session_id)
    db.add_session_id(data['username'], session_id)
    put_message(message)
    release_queue()


@handler.conditional_queue_handler('action', 'create task')
def create_task(message):
    print('cr task', message)
    block_queue()
    send_message(message)


@handler.conditional_queue_handler('action', 'edit task')
def create_task(message):
    print('edit task', message)
    block_queue()
    send_message(message)

# @handler.conditional_socket_handler('server response', 'check user')
# def check_user(message):
