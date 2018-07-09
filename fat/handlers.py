import fat.handlers_base as handlers_base
from db.client_db import ClientDB
from task.task import Task
from comment.comment import Comment
from fat.config import connect_address
import threading
import datetime
import time

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

# Адресс серевера содержиться в файле  fat.config.py
handler = connect_address()


@handler.init_func
def init_func():
    # Инициализируем БД
    data["db"] = ClientDB.create_db("my_db.sqlite")
    data["db"].connect()


@handler.conditional_queue_handler("action", "registration")
def registration(message):
    username = message['body']['name']
    password = message['body']['password']
    data['username'] = username
    data['password'] = password
    block_queue()
    send_message(message)


@handler.conditional_socket_handler('server response', 'registration')
def registration(message):
    if message['body']['code'] == 201:
        data['db'].add_user(data['username'])

        auth_request = {'head': {'type': 'action', 'name': 'authorization'},
                        'body': {'password': data['password'], 'name': data['username']}}

        block_queue()
        send_message(auth_request)
        data.pop('password')

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
    # print(message)
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


def notification(date):
    date_notification = '99.99.9999'
    time_notification = '99:99:99'
    now_date = datetime.datetime.strftime(datetime.datetime.now(), '%d.%m.%Y')
    now_time = datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S')
    for id, t in date.items():
        if t[0] and now_date <= t[0] < date_notification:
            if t[1] and now_time < t[1] < time_notification:
                date_notification = t[0]
                time_notification = t[1]
                server_id = id
                task_name = t[2]
    if date_notification != '99.99.9999':
        def timer(date_notification, time_notification, server_id, task_name):
            date_r = date_notification + ' ' + time_notification
            while datetime.datetime.strptime(date_r, '%d.%m.%Y %H:%M:%S') > datetime.datetime.now():
                time.sleep(10)
            print('<notification>', datetime.datetime.strptime(date_r, '%d.%m.%Y %H:%M:%S'))
            message = {
                "head": {
                    "type": "server response",
                    "name": "notification"
                },
                "body": {
                    "code": '',
                    "message": '{}\n{}'.format(task_name, datetime.datetime.strptime(date_r, '%d.%m.%Y %H:%M:%S')),
                    'server_id': server_id
                }
            }
            put_message(message)
            release_queue()
            notification(date)

        timer = threading.Thread(target=timer, args=(date_notification, time_notification, server_id, task_name))
        timer.start()


@handler.conditional_queue_handler('action', 'create task')
def create_task(message):
    # print('create task ->', message)
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
        task_date_reminder = data['create_task']['body'].get('date_reminder')
        task_time_reminder = data['create_task']['body'].get('time_reminder')
        task_date_create = data['create_task']['body'].get('date_create')
        task_date_deadline = data['create_task']['body'].get('date_deadline')
        data.pop('create_task')

        task = Task(creator=creator, viewer=creator, name=task_name)
        task._date_create = task_date_create
        task.date_deadline = task_date_deadline
        task.date_reminder = task_date_reminder
        task.time_reminder = task_time_reminder
        task.description = task_description
        task.id = int(server_task_id)
        task = task.task_dict
        # print('task->', task)

        data['db'].add_task(task)

    else:
        print(message['body']['code'], message['body']['message'])

    put_message(message)
    release_queue()


@handler.conditional_queue_handler('action', 'delete task')
def delete_task(message):
    # print('delete task ->', message)
    data['delete_task'] = message
    block_queue()
    send_message(message)


@handler.conditional_socket_handler('server response', 'delete task')
def delete_task(message):
    if message['body']['code'] == 200:
        data['db'].delete_task(server_id=data['delete_task']['body']['id'])
    else:
        print(message['body']['code'], message['body']['message'])

    data.pop('delete_task')
    put_message(message)
    release_queue()


@handler.conditional_queue_handler('action', 'edit task')
def edit_task(message):
    # print('edit task ->', message)
    data['edit_task'] = message
    block_queue()
    send_message(message)


@handler.conditional_socket_handler("server response", "edit task")
def edit_task(message):
    # print('data edit task->', data['edit_task'])
    if message['body']['code'] == 200:
        task_name = data['edit_task']['body'].get('name')
        task_description = data['edit_task']['body'].get('description')
        server_task_id = data['edit_task']['body'].get('id')
        # print('task id->', server_task_id)
        local_task_id = data['db'].get_local_task_id(server_task_id)

        if task_name:
            # print('хочу изменить имя в локальной бд')
            # print('имя', task_name)
            data['db'].change_task_name(task_id=local_task_id, task_name=task_name)
            # print('изменил имя')
        if task_description:
            # print('хочу изменить описание в локальной бд')
            # print('описание', task_description)
            data['db'].change_task_description(task_id=local_task_id, task_description=task_description)
            # print('изменил описание')
    else:
        print(message['body']['code'], message['body']['message'])

    data.pop('edit_task')
    put_message(message)
    release_queue()


@handler.conditional_queue_handler('action', 'edit date reminder')
def edit_date_reminder(message):
    data['edit_date_reminder'] = message
    block_queue()
    send_message(message)


@handler.conditional_socket_handler('server response', 'edit date reminder')
def edit_date_reminder(message):
    # print('обрабатываем изменение даты')
    if message['body']['code'] == 200:
        server_task_id = data['edit_date_reminder']['body'].get('id')
        local_task_id = data['db'].get_local_task_id(server_task_id)
        date_reminder = data['edit_date_reminder']['body'].get('date_reminder')
        data['db'].change_date_reminder(task_id=local_task_id, date_reminder=date_reminder)
    else:
        print(message['body']['code'], message['body']['message'])
    data.pop('edit_date_reminder')
    put_message(message)
    release_queue()


@handler.conditional_queue_handler('action', 'edit time reminder')
def edit_time_reminder(message):
    data['edit_time_reminder'] = message
    block_queue()
    send_message(message)


@handler.conditional_socket_handler('server response', 'edit time reminder')
def edit_time_reminder(message):
    # print('обрабатываем изменение времени')
    if message['body']['code'] == 200:
        server_task_id = data['edit_time_reminder']['body'].get('id')
        local_task_id = data['db'].get_local_task_id(server_task_id)
        date_reminder = data['edit_time_reminder']['body'].get('time_reminder')
        data['db'].change_time_reminder(task_id=local_task_id, time_reminder=date_reminder)
    else:
        print(message['body']['code'], message['body']['message'])
    data.pop('edit_time_reminder')
    put_message(message)
    release_queue()


@handler.conditional_queue_handler('action', 'edit date deadline')
def edit_date_deadline(message):
    data['edit_date_deadline'] = message
    block_queue()
    send_message(message)


@handler.conditional_socket_handler('server response', 'edit date deadline')
def edit_date_deadline(message):
    # print('обрабатываем изменение времени')
    if message['body']['code'] == 200:
        server_task_id = data['edit_date_deadline']['body'].get('id')
        local_task_id = data['db'].get_local_task_id(server_task_id)
        date_deadline = data['edit_date_deadline']['body'].get('date_deadline')
        data['db'].change_date_deadline(task_id=local_task_id, date_deadline=date_deadline)
    else:
        print(message['body']['code'], message['body']['message'])
    data.pop('edit_date_deadline')
    put_message(message)
    release_queue()


@handler.conditional_queue_handler('action', 'get all tasks')
def get_all_tasks(message):
    block_queue()
    send_message(message)


@handler.conditional_socket_handler("server response", "get all tasks")
def get_all_tasks(message):
    '''обновим в бд все server_task_id согласно полученному сообщению'''
    # print('get all tasks->', message)
    # da = data['db'].get_all_tasks()
    # notification(da)
    put_message(message)
    if message['body']['code'] == 200:
        for server_task_id, task_ in message['body']['message'].items():
            task_id = data['db'].get_task_id_by_name(task_.get('name'))

            if task_id:
                data['db'].set_task_id(task_id, server_task_id)
                data['db'].change_date_reminder(task_id, task_.get('date_reminder'))
                data['db'].change_time_reminder(task_id, task_.get('time_reminder'))
                data['db'].change_date_deadline(task_id, task_.get('date_deadline'))
                data['db'].set_date_create(task_id, task_.get('date_create'))
            else:
                creator = task_.get('creator')
                viewer = data['username']
                task = Task(creator=creator, viewer=viewer, name=task_.get('name'))
                task.id = int(server_task_id)
                task.description = task_.get('description')
                task.date_reminder = task_.get('date_reminder')
                task.time_reminder = task_.get('time_reminder')
                task.date_create = task_.get('date_create')
                task.date_deadline = task_.get('date_deadline')
                task = task.task_dict
                print('task->', task)
                data['db'].add_task(task)

    # print('before da')
    da = data['db'].get_all_tasks_of_user(username=data['username'])
    print('<All tasks of user>', da)
    notification(da)
    release_queue()


@handler.conditional_queue_handler('action', 'get task by id')
def get_task_by_id(message):
    block_queue()
    send_message(message)


@handler.conditional_socket_handler("server response", "get task by id")
def get_task_by_id(message):
    # print('get task->', message)
    if message['body']['code'] == 200:
        # creator = data['username']
        # name = message['body'].get('task name')
        # description = message['body'].get('description')
        # date_reminder = message['body'].get('date_reminder')
        # time_reminder = message['body'].get('time_reminder')
        # task = Task(name=name, creator=creator, viewer=creator)
        # task.description = description
        # task.date_reminder = date_reminder
        # task.time_reminder = time_reminder
        # task = task.task_dict
        pass

    else:
        print(message['body']['code'], message['body']['message'])

    put_message(message)
    release_queue()


@handler.conditional_queue_handler('action', 'search user')
def search_user(message):
    block_queue()
    send_message(message)


@handler.conditional_socket_handler("server response", "search user")
def search_user(message):
    '''обновим в бд все server_task_id согласно полученному сообщению'''
    # print('search user->', message)
    put_message(message)
    release_queue()


@handler.conditional_queue_handler('action', 'assign performer')
def assign_performer(message):
    # print('assign->', message)
    data['assign_performer'] = message
    block_queue()
    send_message(message)


@handler.conditional_socket_handler('server response', 'assign performer')
def assign_performer(message):
    if message['body']['code'] == 200:
        task_id = int(data['assign_performer']['body']['id'])
        username = data['assign_performer']['body']['user']
        data['db'].add_performer(task_id=task_id, user_name=username)  # task_id локальный
    else:
        print(message['body']['code'], message['body']['message'])
    data.pop('assign_performer')
    put_message(message)
    release_queue()


@handler.conditional_queue_handler('action', 'remove performer')
def remove_performer(message):
    data['remove_performer'] = message
    block_queue()
    send_message(message)


@handler.conditional_socket_handler('server response', 'remove performer')
def remove_performer(message):
    if message['body']['code'] == 200:
        server_task_id = int(data['remove_performer']['body']['id'])
        local_task_id = data['db'].get_local_task_id(server_id=server_task_id)
        performer = data['remove_performer']['body']['user']
        data['db'].remove_performer(task_id=local_task_id, user_name=performer)
    else:
        print(message['body']['code'], message['body']['message'])
    data.pop('remove_performer')
    put_message(message)
    release_queue()


@handler.conditional_queue_handler('action', 'grant access')
def grant_access(message):
    # print('grant access->', message)
    data['grant_access'] = message
    block_queue()
    send_message(message)


@handler.conditional_socket_handler('server response', 'grant access')
def grant_access(message):
    if message['body']['code'] == 200:
        task_id = int(data['grant_access']['body']['id'])
        username = data['grant_access']['body']['user']
        data['db'].add_watcher(task_id=task_id, user_name=username)  # task_id локальный
    else:
        print(message['body']['code'], message['body']['message'])

    data.pop('grant_access')
    put_message(message)
    release_queue()


@handler.conditional_queue_handler('action', 'deny access')
def deny_access(message):
    data['deny_access'] = message
    block_queue()
    send_message(message)


@handler.conditional_socket_handler('server response', 'deny access')
def deny_access(message):
    if message['body']['code'] == 200:
        server_task_id = int(data['deny_access']['body']['id'])
        local_task_id = data['db'].get_local_task_id(server_id=server_task_id)
        watcher = data['deny_access']['body']['user']
        data['db'].remove_watcher(task_id=local_task_id, user_name=watcher)
    else:
        print(message['body']['code'], message['body']['message'])
    data.pop('deny_access')
    put_message(message)
    release_queue()


@handler.conditional_queue_handler('action', 'get all performers')
def get_all_performers(message):
    block_queue()
    send_message(message)


@handler.conditional_socket_handler('server response', 'get all performers')
def get_all_performers(message):
    # print('get all performers->', message)
    put_message(message)
    release_queue()


@handler.conditional_queue_handler('action', 'get all watchers')
def get_all_watchers(message):
    block_queue()
    send_message(message)


@handler.conditional_socket_handler('server response', 'get all watchers')
def get_all_watchers(message):
    # print('get all watchers->', message)
    put_message(message)
    release_queue()


@handler.conditional_queue_handler('action', 'create comment')
def create_comment(message):
    data['create_comment'] = message
    block_queue()
    send_message(message)


@handler.conditional_socket_handler('server response', 'create comment')
def create_comment(message):
    if message['body']['code'] == 200:
        # print('комментарий гуд!!')
        user = data['username']
        text = data['create_comment']['body'].get('text')
        time = data['create_comment']['body'].get('time')
        server_comment_id = int(message['body'].get('id'))
        server_task_id = data['create_comment']['body'].get('id')
        local_task_id = data['db'].get_local_task_id(server_id=server_task_id)
        comment = Comment(user=user, text=text, time_=time)
        comment.id = server_comment_id
        comment = comment.comment_dict
        data['db'].add_comment(comment=comment, task_id=local_task_id)
    else:
        print(message['body']['code'], message['body']['message'])
    data.pop('create_comment')
    put_message(message)
    release_queue()


@handler.conditional_queue_handler('action', 'get comments')
def get_comments(message):
    data['get_comments'] = message
    block_queue()
    send_message(message)


@handler.conditional_socket_handler('server response', 'get comments')
def get_comments(message):
    if message['body']['code'] == 200:
        msg = message['body']['message']
        server_task_id = list(msg.keys())[0]
        srv_comm_ids_server = [int(key) for key in msg[server_task_id]]
        local_task_id = data['db'].get_local_task_id(server_id=server_task_id)
        svr_comm_ids_client = set(int(comment['server_comment_id']) for comment in data['db'].get_comments(local_task_id))
        # print('+++client comments+', svr_comm_ids_client)
        # print('+++server comments+', srv_comm_ids_server)
        for srv_comm_id, comment in msg[server_task_id].items():
            user = comment.get('user')
            text = comment.get('text')
            time = comment.get('time')
            comment = Comment(user=user, text=text, time_=time)
            comment.id = srv_comm_id
            comment = comment.comment_dict

            if int(srv_comm_id) not in svr_comm_ids_client:
                # если комментария нет в бд клиента, то добавляем его
                data['db'].add_comment(comment=comment, task_id=local_task_id)
            else:
                # если комментарий есть, то обновим (пока ничего не делаем))
                pass
    else:
        print(message['body']['code'], message['body']['message'])
    data.pop('get_comments')
    put_message(message)
    release_queue()

#
# @handler.periodic_func(period_time=10, with_start=False)
# def periodic_test():
#     print('/'*15, 'i am periodic function, la-la-laaa', '/'*15)
#     print('/'*12, 'running once per 10 seconds, tra-la-laaa', '/'*12)
