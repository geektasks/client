"""
В данном случае предполагается, что в модуле handlers уже создан экземпляр класса FatThing, его имя — handler.
Для начала работы нужно импортировать модуль и вызвать метод run экземпляра, в отдельном потоке запустится обработчик.
Для получения соответственно входной и выходной очереди используются атрибуты input_queue и output_gueue.
По окончании работы вызовите метод stop.
"""

# ПРИМЕР РАБОТЫ:

# Импорт handlers
import fat.handlers as handlers

import function.requests as request


# Запуск обработчика в другом потоке
handlers.handler.run()



# Получаем очереди
input_queue = handlers.handler.input_queue

# Создаем сообщение и отправляем сообщение во входную очередь обработчика
message = request.registration('Bobby', '123')
# message = request.authorization('Bobby', '123')
input_queue.put(message)

# Ожидаем 7 секунд
import time
time.sleep(3)

# message = request.create_task(name='Task', description='Description')
# print(message)
# input_queue.put(message)

# time.sleep(2)

# message = request.edit_task(task_id=1, name='Taaask')
# print(message)
# input_queue.put(message)

# time.sleep(2)

print(handlers.handler.data)

# Заберем из очереди сообщения
# output_queue = handlers.handler.output_queue
# print(output_queue.get())
# print(output_queue.get())

# Завершаем работу
handlers.handler.stop()
