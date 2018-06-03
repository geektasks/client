from client.client import send_queue

queue = send_queue

def check_user(name):
    message = {
        "head": {
            "type": "action",
            "name": "check_user"
        },
        "body": {
            "name": name
        }
    }
    queue.put(message)