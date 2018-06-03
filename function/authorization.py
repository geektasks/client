# не используем, все запросы делаются в requests

from client.client import send_queue
from jim.jimrequest import JIMRequest
import hashlib

queue = send_queue
secret = 'secret_key'

session = JIMRequest()


def autorization(name, password):
    pas = hashlib.sha256()
    pas.update(name.encode())
    pas.update(password.encode())
    pas.update(secret.encode())
    password = pas.hexdigest()
    message = session.authorization(name=name, password=password).jim_dict
    queue.put(message)