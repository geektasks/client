"""
В данном случае предполагается, что в модуле handlers уже создан экземпляр класса FatThing, его имя — handler.
Для начала работы нужно импортировать модуль и вызвать метод run экземпляра, в отдельном потоке запустится обработчик.
Для получения соответственно входной и выходной очереди используются атрибуты input_queue и output_gueue.
По окончании работы вызовите метод stop.
"""

# ПРИМЕР РАБОТЫ:

# Импорт handlers
import fat.handlers as handlers

# Запуск обработчика в другом потоке
handlers.handler.run()

# Получаем очереди
input_queue = handlers.handler.input_queue

# Создаем сообщение и отправляем сообщение во входную очередь обработчика
message = "Привет, это первое отправленное сообщение!"
input_queue.put(message)

# Ожидаем 7 секунд
import time
time.sleep(7)

# Еще раз отправляем сообщение во входную очередь обработчика
message = """{"head": {"type": "action", "name": "hello"}, "body": "lol"}"""
input_queue.put(message)

# Ожидаем 10 секунд
time.sleep(10)

# Заберем из очереди сообщения
output_queue = handlers.handler.output_queue
print(output_queue.get())
print(output_queue.get())

# Завершаем работу
handlers.handler.stop()
