import inspect
from base.base import FieldType


class JIMRequest:
    session_id = FieldType('session_id', 0, int)
    name = FieldType('name', '', str, 25)
    password = FieldType('password', '', str)
    email = FieldType('email', '', str)
    description = FieldType('description', '', str)
    id = FieldType('id', 0, int)
    user = FieldType('user', '', str, 25)
    status = FieldType('status', 0, int)
    text = FieldType('text', '', str)
    time = FieldType('time', '', str, 25)
    date_create = FieldType('date_create', '', str, 25)
    date_deadline = FieldType('date_deadline', '', str, 25)
    date_reminder = FieldType('date_reminder', '', str, 25)
    time_reminder = FieldType('time_reminder', '', str, 25)

    __slots__ = {'head', session_id.name,
                 name.name,
                 password.name,
                 email.name,
                 description.name,
                 id.name,
                 user.name,
                 status.name,
                 text.name,
                 time.name,
                 date_create.name,
                 date_deadline.name,
                 date_reminder.name,
                 time_reminder.name}

    def __init__(self, session_id=0, **kwargs):
        self.session_id = session_id
        for key, value in kwargs.items():
            setattr(self, key, value)
        method_name = inspect.stack()[1][3]
        self.head = {'type': 'action', 'name': method_name.replace('_', ' '), 'session_id': self.session_id}

    @property
    def body(self):
        dict_ = dict()
        for key in self.__slots__:
            if key != 'head' and key != '_session_id':
                try:
                    value = getattr(self, key)
                    dict_.update({key.lstrip('_'): value})
                except AttributeError:
                    pass
        return dict_

    @property
    def jim_dict(self):
        if self.session_id == 0:
            self.head.pop('session_id')
        return {'head': self.head, 'body': self.body}

    def check_user(self, name):
        return JIMRequest(name=name)

    def registration(self, name, password, email=None):
        '''пароль сразу хэшировать??'''
        if email:
            return JIMRequest(name=name, password=password, email=email)
        else:
            return JIMRequest(name=name, password=password)

    def authorization(self, name, password):
        '''передавать хэш пароля??
           или будем проверять session_id???'''
        return JIMRequest(name=name, password=password)

    def presence(self, username):
        return JIMRequest(session_id=self.session_id, name=username)

    def create_task(self, name, description, date_create=None,
                    date_deadline=None,
                    date_reminder=None,
                    time_reminder=None):
        return JIMRequest(session_id=self.session_id, name=name, description=description, date_create=date_create,
                          date_deadline=date_deadline,
                          date_reminder=date_reminder,
                          time_reminder=time_reminder)

    def delete_task(self, task_id):
        '''

        :param task_id:server_task_id
        :return:
        '''
        return JIMRequest(session_id=self.session_id, id=task_id)

    def edit_task(self, task_id, name=None, description=None):
        '''task_id == server_task_id'''
        if name:
            return JIMRequest(session_id=self.session_id, id=task_id, name=name)
        if description:
            return JIMRequest(session_id=self.session_id, id=task_id, description=description)
        if name and description:
            return JIMRequest(session_id=self.session_id, id=task_id, name=name, description=description)

    def edit_date_reminder(self, task_id, date_reminder):
        return JIMRequest(session_id=self.session_id, id=task_id, date_reminder=date_reminder)

    def edit_time_reminder(self, task_id, time_reminder):
        return JIMRequest(session_id=self.session_id, id=task_id, time_reminder=time_reminder)

    def edit_date_deadline(self, task_id, date_deadline):
        return JIMRequest(session_id=self.session_id, id=task_id, date_deadline=date_deadline)

    def get_all_tasks(self):
        return JIMRequest(session_id=self.session_id)

    def get_task_by_id(self, task_id):
        return JIMRequest(session_id=self.session_id, id=task_id)

    def grant_access(self, task_id, user):
        return JIMRequest(session_id=self.session_id, id=task_id, user=user)

    def deny_access(self, task_id, user):
        return JIMRequest(session_id=self.session_id, id=task_id, user=user)

    def assign_performer(self, task_id, user=None):
        if user:
            return JIMRequest(session_id=self.session_id, id=task_id, user=user)
        else:
            return JIMRequest(session_id=self.session_id, id=task_id)

    def remove_performer(self, task_id, user=None):
        if user:
            return JIMRequest(session_id=self.session_id, id=task_id, user=user)
        else:
            return JIMRequest(session_id=self.session_id, id=task_id)

    def change_status(self, task_id, status):
        '''status == 0 / 1 / 2 '''
        return JIMRequest(session_id=self.session_id, id=task_id, status=status)

    def create_comment(self, task_id, text, time):
        return JIMRequest(session_id=self.session_id, id=task_id, text=text, time=time)

    def delete_comment(self, comment_id):
        return JIMRequest(session_id=self.session_id, id=comment_id)

    def search_user(self, name):
        return JIMRequest(session_id=self.session_id, name=name)

    def get_all_performers(self, task_id):
        '''task_id = server_task_id'''
        return JIMRequest(session_id=self.session_id, id=task_id)

    def get_all_watchers(self, task_id):
        '''task_id = server_task_id'''
        return JIMRequest(session_id=self.session_id, id=task_id)


if __name__ == '__main__':
    session = JIMRequest()

    session.session_id = 1
    print(session.session_id)

    check = session.check_user('User').jim_dict
    print('check user', check)

    session.session_id = 1
    print(session.session_id)

    check = session.check_user('User').jim_dict
    print('check user', check)

    registr = session.registration('Jack', '123').jim_dict
    print('registration', registr)

    auth = session.authorization('Jack', '123').jim_dict
    print('authorization', auth)

    presence = session.presence('Jack').jim_dict
    print('presence', presence)

    create_task = session.create_task(name='New', description='new description', date_create='date', date_deadline=
    'date', date_reminder='date', time_reminder='time').jim_dict
    print('create', create_task)

    print('-' * 50)
    # session.session_id = 0

    print('get task')
    get_task = session.get_all_tasks().jim_dict
    print(get_task)

    edit_name = session.edit_task(task_id=1, name='Edit name').jim_dict
    print('edit name', edit_name)

    edit_description = session.edit_task(task_id=1, description='Edit description').jim_dict
    print('edit discription', edit_description)

    grant_access = session.grant_access(task_id=1, user='Jack').jim_dict
    print('grant access', grant_access)

    deny_access = session.deny_access(task_id=1, user='Jack').jim_dict
    print('deny access', deny_access)

    assign_self = session.assign_performer(task_id=1).jim_dict
    print('assign self', assign_self)

    assign = session.assign_performer(task_id=1, user='Jack').jim_dict
    print('assign', assign)

    remove_self = session.remove_performer(task_id=1).jim_dict
    print('remove self', remove_self)

    remove = session.remove_performer(task_id=1, user='Jack').jim_dict
    print('remove', remove)

    status = session.change_status(task_id=1, status=2).jim_dict
    print('status', status)

    create_comment = session.create_comment(task_id=1, text='new comment', time='12:50').jim_dict
    print('create comment', create_comment)

    delete_comment = session.delete_comment(comment_id=1).jim_dict
    print('delete comment', delete_comment)
