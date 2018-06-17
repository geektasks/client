import fat.handlers_base as handlers_base
from db.client_db import ClientDB
from task.task import Task

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

# handler = handlers_base.FatThing("127.0.0.1", 8000)


handler = handlers_base.FatThing("ddimans.dyndns.org", 8000)
# handler = handlers_base.FatThing("185.189.12.43", 8000)


# handler = handlers_base.FatThing("127.0.0.1", 8888)


@handler.init_func
def init_func():
    # Инициализируем БД
    data["db"] = ClientDB.create_db("my_db.sqlite")
    data["db"].connect()


@handler.conditional_queue_handler("action", "registration")
def registration(message):
    username = message['body']['name']
    data['username'] = username
    block_queue()
    send_message(message)


@handler.conditional_socket_handler('server response', 'registration')
def registration(message):
    if message['body']['code'] == 201:
        data['db'].add_user(data['username'])
    else:
        data['username'] = None
        print(message['body']['code'], message['body']['message'])
    put_message(message)
    release_queue()

@handler.conditional_socket_handler('server response', 'registration error')
def registration(message):
    put_message(message)
    release_queue()

@handler.conditional_queue_handler("action", "check user")
def check_user(message):
    block_queue()
    send_message(message)

@handler.conditional_socket_handler('server response', 'check user')
def check_user(message):
    print(message)
    put_message(message)
    release_queue()


@handler.conditional_queue_handler("action", "authorization")
def authorization(message):
    username = message['body']['name']
    data['username'] = username
    block_queue()
    send_message(message)


@handler.conditional_socket_handler("server response", "authorization")
def authorization(message):
    if message['body']['code'] == 200:
        session_id = message['body']['session id']
        data['session_id'] = int(session_id)
        data['db'].add_session_id(data['username'], session_id)
    else:
        data['username'] = None
        print(message['body']['code'], message['body']['message'])
    put_message(message)
    release_queue()


@handler.conditional_queue_handler('action', 'create task')
def create_task(message):
    print('create task ->', message)
    data['create_task'] = message
    block_queue()
    send_message(message)


@handler.conditional_socket_handler('server response', 'create task')
def create_task(message):
    if message['body']['code'] == 201:
        creator = data['username']
        server_task_id = message['body'].get('id')
        task_name = data['create_task']['body'].get('name')
        task_description = data['create_task']['body'].get('description')
        data.pop('create_task')

        task = Task(creator=creator, viewer=creator, name=task_name)
        task.description = task_description
        task.id = int(server_task_id)
        task = task.task_dict
        print('task->', task)

        data['db'].add_task(task)

    else:
        print(message['body']['code'], message['body']['message'])

    put_message(message)
    release_queue()


@handler.conditional_queue_handler('action', 'edit task')
def edit_task(message):
    print('edit task ->', message)
    data['edit_task'] = message
    block_queue()
    send_message(message)


@handler.conditional_socket_handler("server response", "edit task")
def edit_task(message):
    if message['body']['code'] == 200:
        task_name = data['edit_task']['body'].get('name')
        task_description = data['edit_task']['body'].get('description')
        task_id = data['db'].get_task_id_by_name(task_name=task_name)
        data.pop('edit_task')
        if task_name:
            data['db'].change_task_name(task_id=task_id, task_name=task_name)
        if task_description:
            data['db'].change_task_description(task_id=task_id, task_description=task_name)

    else:
        print(message['body']['code'], message['body']['message'])

    put_message(message)
    release_queue()

@handler.conditional_queue_handler('action', 'get all tasks')
def get_all_tasks(message):
    block_queue()
    send_message(message)


@handler.conditional_socket_handler("server response", "get all tasks")
def get_all_tasks(message):
    '''обновим в бд все server_task_id согласно полученному сообщению'''
    print('get all tasks->', message)
    put_message(message)
    if message['body']['code'] == 200:
        for key, value in message['body']['message'].items():
            task_id = data['db'].get_task_id_by_name(value)
            data['db'].set_task_id(task_id, key)

    # put_message(message)
    release_queue()