import time
from base.base import FieldType


class Comment:
    user = FieldType('user', '', str)
    text = FieldType('text', str)
    time = FieldType('time', str)

    def __init__(self, user, text, time_=None):
        self.user = user
        self.text = text
        self.time = time_ if time_ else str(time.time())

    @property
    def comment_dict(self):
        _dict = dict()
        for key in self.__dict__:
            try:
                value = getattr(self, key)
                _dict[key.lstrip('_')] = value
            except AttributeError:
                pass
        return _dict


if __name__ == '__main__':
    comment = Comment(user='user', text='text', time_='456')
    comment.id = 1
    print(comment.comment_dict)
