import time
from base.utils import act_time
from comment.comment import Comment

status = {0: 'waiting', 1: 'doing', 2: 'done'}  # статус задачи, по умолчанию в ожидании


class Task:

    def __init__(self, creator, viewer=None, name=None):
        '''
        :param creator: имя Пользователя, создатель задачи
        :param viewer: имя Пользователя, кто просматривает задачу
        :param name: название задачи, если не установленно, то New task
        '''
        self.server_task_id = None
        self._creator = creator
        self.viewer = viewer
        self._name = 'New task' if not name else name  # если задача с таким именем уже есть добавить суффикс _1(2, 3...)
        self._description = None
        self._date_create = None  # дата создания
        self._date_deadline = None  # срок (дата) исполнения
        self._date_remind = None  # дата напоминания
        self._time_remind = None  # время напоминания
        self._status = 0
        self._performers = [creator]  # список пользователей, которым задача сопоставленна
        self._watchers = [creator]  # список пользователе у которых есть доступ к задаче
        self.comments = dict()  # {'User_1': [{'text': text, 'time': time}, {}...], ...}

    def __repr__(self):
        return '>>>>>\nTask: {name} / creator: {creator} / created: {time} / deadline: {deadline}\n \
status: {status} / description: {description}\n \
performers: {performers} / access: {access}\n \
comments: {comments}\n>>>>>'.format(name=self._name,
                                    creator=self._creator,
                                    status=self.status,
                                    description=self._description,
                                    performers=self._performers,
                                    access=self._watchers,
                                    comments=self.comments)

    @property
    def task_dict(self):
        t_dict = dict()
        for key in self.__dict__:
            try:
                value = getattr(self, key)
                # if value:
                t_dict.update({key.lstrip('_'): value})
            except AttributeError:
                pass
        return t_dict

    @property
    def creator(self):
        return self._creator

    @creator.setter
    def creator(self, value=None):
        print("<Creator couldn't be set>")

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if self._creator != self.viewer:
            print('<Only creator could change name>')
        else:
            self._name = name

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, text):
        if self._creator != self.viewer:
            print('<Only creator could set text>')
        else:
            self._description = text

    # TODO протестировать изменение текста в qt форме / сделать подтверждение изменения текста задачи
    def description_edit(self):
        '''
        при вызове метода подразумевается, что пользователю становится доступен текст задачи self._text, который
        сохраняется в original_text и доступен для изменения (например в каком-либо QT виджете).
        :return:
        '''
        original_description = self._description
        # обрабатываем исходный текст задачи
        edited_description = original_description + ' _and edited!'
        # переопределяем соответствующее поле
        self.description = edited_description

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value: int):
        '''
        Поменять статус может любой из списка исполнителей или доступа
        :param value: статус задачи: 0 - в очереди, 1 - выполняется, 2 - сделана
        :return:
        '''
        if self.viewer in self._performers or self.viewer in self._watchers:
            self._status = value
        else:
            print('You have not access to edit status')

    @property
    def date_deadline(self):
        return self._date_deadline

    @date_deadline.setter
    def date_deadline(self, value):
        if self.viewer in self._performers or self.viewer in self._watchers:
            self._date_deadline = value
        else:
            print('You have not access to edit deadline')

    @property
    def performer_user(self):
        if self.viewer in self._performers or self.viewer in self._watchers:
            return self._performers
        else:
            print('You have not access to edit performers')
            return False

    def add_performer(self, user):
        '''
        Добавлять исполнителей может любой из списка исполнителей или из доступа к задаче
        :param user:
        :return:
        '''
        if self.performer_user:
            if user not in self._performers:
                self.performer_user.append(user)

    def del_performer(self, user):
        """
        Удалять исполниетелей может любой из списка исполнителей или из доступа к задаче
        создателя удалить нельзя (это надо обсудить)
        :param user:
        :return:
        """
        if self.performer_user:
            if user == self.creator:
                print('<Creator could not be removed>')
            else:
                try:
                    self.performer_user.remove(user)
                except ValueError:
                    pass

    @property
    def access_users(self):
        if self.viewer in self._watchers:
            return self._watchers
        else:
            print('You have not access to edit access list')
            return False

    def add_to_access(self, user):
        if self.access_users:
            if user not in self._watchers:
                self._watchers.append(user)

    def del_from_access(self, user):
        if self.access_users:
            if user == self.creator:
                print('<Creator could not be removed>')
            else:
                self._watchers.remove(user)

    def add_comment(self, comment):
        '''
        комментарии оставляют только пользователи из списка self.performer_user и self.access_users
        :param comment: словарь вида {'text': text, 'time': time, 'user': user} или экземпляр класса Comment
        :return:
        '''
        user = comment.user if isinstance(comment, Comment) else comment['user']
        text = comment.text if isinstance(comment, Comment) else comment['text']
        time_ = comment.time if isinstance(comment, Comment) else comment['time']
        if user in self._performers or user in self._watchers:
            if user in self.comments:
                self.comments[user].append({'time': time_, 'text': text})
            else:
                self.comments[user] = [{'time': time_, 'text': text}]
        else:
            print('You cannot leave comment here')

    def del_comment(self, comment):
        '''
        :param comment: словарь вида {'text': text, 'time': time}, из self._comments[viewer]
        :return:
        '''
        if self.viewer in self.comments:
            for comm in self.comments[self.viewer]:
                if comm == comment:
                    self.comments[self.viewer].remove(comm)
                    return


if __name__ == '__main__':
    task = Task(creator='gkjf')
    print(task.task_dict)
