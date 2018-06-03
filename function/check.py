# не используем, все запросы делаются в requests

from client.client import send_queue
from jim.jimrequest import JIMRequest

queue = send_queue
secret = 'secret_key'

session = JIMRequest()


def check_user(name):
    message = session.check_user(name=name).jim_dict
    queue.put(message)
