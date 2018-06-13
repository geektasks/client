# не используем, все запросы делаются в requests
'''
from client.client import send_queue
from jim.jimrequest import JIMRequest
import hashlib

queue = send_queue
<<<<<<< HEAD
secret = 'secret_key'

session = JIMRequest()

=======
secret = 'secretkey'
>>>>>>> master

def registration(name, password, email):
    pas = hashlib.sha256()
    pas.update(name.encode())
    pas.update(password.encode())
    pas.update(secret.encode())
    password = pas.hexdigest()
    message = session.registration(name=name, password=password, email=email).jim_dict
    queue.put(message)
'''
