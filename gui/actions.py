
from db.client_db import ClientDB

client_db = ClientDB.create_db('client_db_1')
client_db.connect()
print('db created!')

def authorization(body):
    code = body.get('code')
    if code == 200:
        client_db.add_session_id(user_name='default', session_id=body.get('session id'))
        print('ok')
    else:
        # render to gui
        pass

def create_task(body):
    pass