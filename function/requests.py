from client.client import send_queue
from jim.jimrequest import JIMRequest
from db.client_db import ClientDB
import hashlib

queue = send_queue
secret = 'secret_key'

db = ClientDB('client_db_1')
user_name = 'Jack'  # как будем получать имя текущего (залогиненного) пользователя?

try:
    session_id = db.get_session_ids(user_name)[0]  # получаем из бд, если авторизация (регистрация?) ок
except:
    session_id = 0
session = JIMRequest(session_id=session_id)


def registration(name, password, email):
    pas = hashlib.sha256()
    pas.update(name.encode())
    pas.update(password.encode())
    pas.update(secret.encode())
    password = pas.hexdigest()
    message = session.registration(name=name, password=password, email=email).jim_dict
    queue.put(message)


def check_user(name):
    message = session.check_user(name=name).jim_dict
    queue.put(message)


def authorization(name, password):
    message = session.authorization(name=name, password=password).jim_dict
    queue.put(message)


def presence(name):
    message = session.presence(username=name).jim_dict
    queue.put(message)


def create_task(name, description):
    message = session.create_task(name=name, description=description)
    queue.put(message)


def edit_task(task_id, name=None, description=None):
    message = session.edit_task(task_id=task_id, name=name, description=description)
    queue.put(message)


def grant_access(task_id, user):
    message = session.grant_access(task_id=task_id, user=user)
    queue.put(message)


def deny_access(task_id, user):
    message = session.deny_access(task_id=task_id, user=user)
    queue.put(message)


def assign_performer(task_id, user=None):
    message = session.assign_performer(task_id=task_id, user=user)
    queue.put(message)


def remove_performer(task_id, user=None):
    message = session.remove_performer(task_id=task_id, user=user)
    queue.put(message)


def change_status(task_id, status):
    '''status == 0 / 1 / 2 '''
    message = session.change_status(task_id=task_id, status=status)
    queue.put(message)


def create_comment(task_id, text, time):
    message = session.create_comment(task_id=task_id, text=text, time=time)
    queue.put(message)


def delete_comment(comment_id):
    message = session.delete_comment(comment_id=comment_id)
    queue.put(message)


if __name__ == '__main__':
    pass
