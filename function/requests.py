from jim.jimrequest import JIMRequest
import hashlib
import fat.handlers as handlers

secret = 'secret_key'

# session_id = handlers.handler.data['session id']
# username = handlers.handler.data['username']


session = JIMRequest()


def registration(name, password, email=None):
    pas = hashlib.sha256()
    pas.update(name.encode())
    pas.update(password.encode())
    pas.update(secret.encode())
    password = pas.hexdigest()
    message = session.registration(name=name, password=password, email=email).jim_dict
    return message


def check_user(name):
    message = session.check_user(name=name).jim_dict
    return message


def authorization(name, password):
    pas = hashlib.sha256()
    pas.update(name.encode())
    pas.update(password.encode())
    pas.update(secret.encode())
    password = pas.hexdigest()
    message = session.authorization(name=name, password=password).jim_dict
    return message


def presence(name):
    message = session.presence(username=name).jim_dict
    return message


def create_task(name, description):
    print('session_id->', handlers.handler.data['session_id'])
    try:
        session.session_id = int(handlers.handler.data['session_id'])
    except Exception as err:
        print('error->', err)
    message = session.create_task(name=name, description=description).jim_dict
    return message


def edit_task(task_id, name=None, description=None):
    try:
        session.session_id = handlers.handler.data['session_id']
    except Exception as err:
        print('error*->', err)
    message = session.edit_task(task_id=task_id, name=name, description=description).jim_dict
    return message

def get_all_tasks():
    try:
        session.session_id = handlers.handler.data['session_id']
    except Exception as err:
        print('error**->', err)
    message = session.get_all_tasks().jim_dict
    print(message)
    return message


def grant_access(task_id, user):
    message = session.grant_access(task_id=task_id, user=user).jim_dict
    return message


def deny_access(task_id, user):
    message = session.deny_access(task_id=task_id, user=user).jim_dict
    return message


def assign_performer(task_id, user=None):
    message = session.assign_performer(task_id=task_id, user=user).jim_dict
    return message


def remove_performer(task_id, user=None):
    message = session.remove_performer(task_id=task_id, user=user).jim_dict
    return message


def change_status(task_id, status):
    '''status == 0 / 1 / 2 '''
    message = session.change_status(task_id=task_id, status=status).jim_dict
    return message


def create_comment(task_id, text, time):
    message = session.create_comment(task_id=task_id, text=text, time=time).jim_dict
    return message


def delete_comment(comment_id):
    message = session.delete_comment(comment_id=comment_id).jim_dict
    return message


if __name__ == '__main__':
    pass
