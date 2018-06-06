import sqlite3

"""
ИНСТРУКЦИЯ ПО РАБОТЕ С ИДЕНТИФИКАТОРАМИ СЕССИЙ

А. Создать БД, если она, возможно, не создана (или подключиться, если она точно создана)
    1. Не уверены, что БД создана (db_name — имя БД)
        db = ClientDB.create_db(db_name) 
    2. Уверены, что БД уже создана (если не уверены, то делаем 1-й шаг, второй не нужно)
        db = ClientDB(db_name) 
    3. Радоваться и юзать.

Б. Для сохранения идентификатора сессии (db — экзампляр класса ClientDB):
    1. Если необходимо, удалить все идентификаторы сессий в БД (если нет — пропускаем шаг)
        db.del_all_session_ids()
    2. Добавить идентификатор сессии (user_name — имя пользователя, session_id — идентификатор сессии)
        db.add_session_id(user_name, session_id)
    3. Радоваться.

В. Для получения идентификатора сессии (пока предполагаю, что в БД только один идентификатор):
    1. Получить имя пользователя с идентификатором сессии
        user_name = db.get_all_users_with_session_ids()[0]
    2. Получить идентификатор сессии (user_name — имя пользователя, полученное на предыдущем шаге)
        session_id = db.get_session_ids(user_name)[0]
    3. Радоваться и юзать.
"""

class ClientDB:

    ###############################
    # Инициализация и создание БД #
    ###############################

    def __init__(self, db_name):
        """
        Инициализация класса доступа к БД
        :param db_name: имя БД
        """
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    @classmethod
    def create_db(cls, db_name):
        """
        Создать БД
        :param db_name: имя БД
        :return: экземпляр класса доступа к БД
        """

        # Подключаемся или создаем БД, создаем курсор
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Создание таблицы «ЗАДАЧИ»
        cursor.execute("""CREATE TABLE IF NOT EXISTS tasks
                          (task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                          task_name TEXT,
                          task_description TEXT,
                          status_id INTEGER,
                          user_id INTEGER,
                          FOREIGN KEY (status_id) REFERENCES statuses(id),
                          FOREIGN KEY (user_id) REFERENCES users(id))
                          """)

        # Создание таблицы «ПОЛЬЗОВАТЕЛИ»
        cursor.execute("""CREATE TABLE IF NOT EXISTS users
                          (user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_name TEXT)
                          """)

        # Создание таблицы «КОММЕНТАРИИ»
        cursor.execute("""CREATE TABLE IF NOT EXISTS comments
                          (comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                          task_id INTEGER,
                          comment_text TEXT,
                          comment_time INTEGER,
                          user_id INTEGER,
                          FOREIGN KEY (task_id) REFERENCES tasks(task_id)
                          FOREIGN KEY (user_id) REFERENCES users(user_id))
                          """)

        # Создание таблицы «ПОЛЬЗОВАТЕЛИ С ДОСТУПОМ»
        cursor.execute("""CREATE TABLE IF NOT EXISTS watchers
                          (watcher_id INTEGER PRIMARY KEY AUTOINCREMENT,
                          task_id INTEGER,
                          user_id INTEGER, 
                          FOREIGN KEY (task_id) REFERENCES tasks(task_id),
                          FOREIGN KEY (user_id) REFERENCES users(user_id))
                          """)

        # Создание таблицы «ИСПОЛНИТЕЛИ»
        cursor.execute("""CREATE TABLE IF NOT EXISTS performers
                          (performer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                          task_id INTEGER,
                          user_id INTEGER,
                          FOREIGN KEY (task_id) REFERENCES tasks(task_id),
                          FOREIGN KEY (user_id) REFERENCES users(user_id))
                          """)

        # Создание таблицы «СТАТУСЫ»
        cursor.execute("""CREATE TABLE IF NOT EXISTS statuses
                          (status_id INTEGER PRIMARY KEY AUTOINCREMENT,
                          status_name TEXT)
                          """)

        # Создание таблицы «ИДЕНТИФИКАТОРЫ СЕССИЙ»
        cursor.execute("""CREATE TABLE IF NOT EXISTS sessions
                              (session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                              user_id INTEGER,
                              session_identificator TEXT,
                              FOREIGN KEY (user_id) REFERENCES users(user_id))
                              """)

        conn.close()

        return cls(db_name)

    #######################################
    # Добавление строк в основные таблицы #
    #######################################

    def add_user(self, user_name):
        """
        Добавить пользователя в БД
        :param user_name: имя пользователя
        :return: user_id идентификатор пользователя в локальной БД
        """
        self.cursor.execute("""SELECT * FROM users WHERE users.user_name = ?""", [user_name])
        try:
            user_id = self.cursor.fetchone()[0]
            return user_id
        except TypeError:
            self.cursor.execute("""INSERT INTO users (user_name) VALUES (?)""", [user_name])
            self.conn.commit()
            return self.cursor.lastrowid

    def add_status(self, status_name):
        """
        Добавить статус в БД
        :param status_name: имя статуса
        :return: status_id идентификатор статуса в локальной БД
        """
        self.cursor.execute("""SELECT * FROM statuses WHERE statuses.status_name = ?""", [status_name])
        try:
            status_id = self.cursor.fetchone()[0]
            return status_id
        except TypeError:
            self.cursor.execute("""INSERT INTO statuses (status_name) VALUES (?)""", [status_name])
            self.conn.commit()
            return self.cursor.lastrowid

    def add_watcher(self, task_id, user_name):
        """
        Добавить наблюдателя (пользователя, имеющего доступ к задаче) в БД
        :param task_id: идентификатор задачи
        :param user_name: имя пользователя
        :return: watcher_id идентификатор наблюдателя в локальной БД
        """
        user_id = self.add_user(user_name)
        self.cursor.execute("""SELECT * FROM watchers WHERE task_id = ? AND user_id = ?""", [task_id, user_id])
        try:
            watcher_id = self.cursor.fetchone()[0]
            return watcher_id
        except TypeError:
            self.cursor.execute("""INSERT INTO watchers (task_id, user_id) VALUES (?, ?)""", [task_id, user_id])
            self.conn.commit()
            return self.cursor.lastrowid

    def add_performer(self, task_id, user_name):
        """
        Добавить исполнителя (пользователя, сопоставленного задаче) в БД
        :param task_id: идентификатор задачи
        :param user_name: имя пользователя
        :return: performer_id идентификатор исполнителя в локальной БД
        """
        user_id = self.add_user(user_name)
        self.cursor.execute("""SELECT * FROM performers WHERE task_id = ? AND user_id = ?""", [task_id, user_id])
        try:
            performer_id = self.cursor.fetchone()[0]
            return performer_id
        except TypeError:
            self.cursor.execute("""INSERT INTO performers (task_id, user_id) VALUES (?, ?)""", [task_id, user_id])
            self.conn.commit()
            return self.cursor.lastrowid

    def add_task(self, task):
        """
        Добавить задачу в БД
        :param task: экземпляр класса «Задача»
        :return: task_id идентификатор задачи в локальной БД
        """
        user_id = self.add_user(task["creator"])
        status_id = self.add_status(task["status"])
        values = [
            task["name"],
            task["description"],
            status_id,
            user_id
        ]
        self.cursor.execute("""INSERT INTO tasks (task_name, task_description, status_id, user_id) VALUES (?, ?, ?, ?)""", values)
        task_id = self.cursor.lastrowid
        for watcher in task["watchers"]:
            self.add_watcher(task_id, watcher)
        for performer in task["performers"]:
            self.add_performer(task_id, performer)
        for comment in task["comments"]:
            self.add_comment(comment, task_id=task_id)
        self.conn.commit()
        return task_id

    def add_comment(self, comment, task_id=None):
        """
        Добавить комментарий в БД
        :param comment: экземпляр класса «Комментарий»
        :param task_id: если поле «task_id» переданного экземпляра класса «Комментарий» содержит значение None, то в
        качестве поля «task_id» при сохранении в БД будет использовано это значение
        :return: comment_id идентификатор комментария в локальной БД
        """
        user_id = self.add_user(comment["user"])
        if comment["task id"] is not None:
            task_id = comment["task id"]
        values = [
            task_id,
            comment["text"],
            comment["time"],
            user_id
        ]
        self.cursor.execute("""INSERT INTO comments (task_id, comment_text, comment_time, user_id) VALUES (?, ?, ?, ?)""", values)
        self.conn.commit()
        return self.cursor.lastrowid

    #######################################
    # Извлечение строк из основных таблиц #
    #######################################

    def get_watchers(self, task_id):
        """
        Получить наблюдателей (пользователей, имеющих доступ к задаче)
        :param task_id: идентификатор задачи
        :return: список имен пользователей
        """
        self.cursor.execute("""SELECT users.user_name FROM users INNER JOIN watchers ON users.user_id = watchers.user_id WHERE watchers.task_id = ?""", [task_id])
        return [x[0] for x in self.cursor.fetchall()]

    def get_performers(self, task_id):
        """
        Получить исполнителей (пользователя, сопоставленных задаче)
        :param task_id: идентификатор задачи
        :return: список имен пользователей
        """
        self.cursor.execute("""SELECT users.user_name FROM users INNER JOIN performers ON users.user_id = performers.user_id WHERE performers.task_id = ?""", [task_id])
        return [x[0] for x in self.cursor.fetchall()]

    def get_comments(self, task_id):
        """
        Получить комментарии
        :param task_id: идентификатор задачи
        :return: список экземпляров класса «Комментарий»
        """
        self.cursor.execute("""SELECT comments.comment_id, comments.comment_text, comments.comment_time, users.user_name FROM comments INNER JOIN users ON comments.user_id = users.user_id WHERE comments.task_id = ?""", [task_id])
        data = self.cursor.fetchall()
        comments = [{
            "comment id": comment[0],
            "text": comment[1],
            "time": comment[2],
            "user": comment[3]
        } for comment in data]
        return comments

    #####################
    # Работа с задачами #
    #####################

    def get_tasks(self):
        """
        Получить задачи из БД
        :return: Список экземпляров класса «Задача»
        """
        tasks = []
        self.cursor.execute("""SELECT tasks.task_id FROM tasks""")
        task_ids = self.cursor.fetchall()
        for id in task_ids:
            tasks.append(self.get_task(id[0]))
        return tasks

    def get_task(self, task_id):
        """
        Получить задачу из БД
        :param task_id: идентификатор задачи
        :return: экземпляр класса «Задача»
        """
        self.cursor.execute("""SELECT tasks.task_name, tasks.task_description, statuses.status_name, users.user_name FROM tasks INNER JOIN statuses ON tasks.status_id = statuses.status_id INNER JOIN users ON tasks.user_id = users.user_id WHERE tasks.task_id = ?""", [task_id])
        data = self.cursor.fetchone()
        task = {
            "id": task_id,
            "name": data[0],
            "description": data[1],
            "status": data[2],
            "watchers": self.get_watchers(task_id),
            "performers": self.get_performers(task_id),
            "creator": data[3],
            "comments": self.get_comments(task_id)
        }
        return task

    def change_task_name(self, task_id, task_name):
        """
        Изменить имя задачи
        :param task_id: идентификатор задачи
        :param task_name: новое имя
        :return: экземпляр класса «Задача»
        """
        self.cursor.execute("""UPDATE tasks SET task_name = ? WHERE task_id = ?""", [task_name, task_id])
        self.conn.commit()
        return self.get_task(task_id)

    def change_task_description(self, task_id, task_description):
        """
        Изменить описание задачи
        :param task_id: идентификатор задачи
        :param task_description: новое описание
        :return: экземпляр класса «Задача»
        """
        self.cursor.execute("""UPDATE tasks SET task_description = ? WHERE task_id = ?""", [task_description, task_id])
        self.conn.commit()
        return self.get_task(task_id)

    def remove_watcher(self, task_id, user_name):
        """
        Удалить наблюдателя (пользователя, имеющего доступ к задаче) — закрыть доступ
        :param task_id: идентификатор задачи
        :param user_name: имя наболюдателя
        :return: экземпляр класса «Задача»
        """
        user_id = self.add_user(user_name)
        self.cursor.execute("""DELETE FROM watchers WHERE task_id = ? AND user_id = ?""", [task_id, user_id])
        self.conn.commit()
        return self.get_task(task_id)

    def remove_performer(self, task_id, user_name):
        """
        Удалить исполнителя (пользователя, сопоставленного задаче)
        :param task_id: идентификатор задачи
        :param user_name: имя исполнителя
        :return: экземпляр класса «Задача»
        """
        user_id = self.add_user(user_name)
        self.cursor.execute("""DELETE FROM performers WHERE task_id = ? AND user_id = ?""", [task_id, user_id])
        self.conn.commit()
        return self.get_task(task_id)

    def remove_comment(self, comment_id):
        """
        Удалить комментарий
        :param comment_id: идентификатор комментария
        :return: экземпляр класса «Задача»
        """
        self.cursor.execute("SELECT task_id FROM comments WHERE comments.comment_id = ?", [comment_id])
        task_id = self.cursor.fetchone()[0]
        self.cursor.execute("""DELETE FROM comments WHERE comment_id = ?""", [comment_id])
        self.conn.commit()
        return self.get_task(task_id)

    ####################################
    # Работа с идентификаторами сессий #
    ####################################

    def add_session_id(self, user_name, session_id):
        """
        Добавить идентификатор сессиии
        :param user_name: Имя пользователя
        :param session_id: Идентификатор сессии
        :return: None
        """
        user_id = self.add_user(user_name)
        self.cursor.execute("""INSERT INTO sessions (user_id, session_identificator) VALUES (?, ?)""", [user_id, session_id])
        self.conn.commit()

    def get_all_users_with_session_ids(self):
        """
        Получить всех пользователей с идентификаторами сессий
        :return: список имен пользователей
        """
        self.cursor.execute("""SELECT users.user_name FROM users INNER JOIN sessions ON users.user_id = sessions.user_id GROUP BY users.user_name""")
        return [x[0] for x in self.cursor.fetchall()]

    def get_session_ids(self, user_name):
        """
        Получить идентификаторы сессий пользователя
        :param user_name: имя пользователя
        :return: список идентификаторов сессий пользователя
        """
        self.cursor.execute("""SELECT sessions.session_identificator FROM sessions INNER JOIN users ON sessions.user_id = users.user_id WHERE users.user_name = ?""", [user_name])
        session_ids = list(map(lambda x: x[0], self.cursor.fetchall()))
        return session_ids

    def del_all_session_ids(self):
        """
        Удалить все идентификаторы сессий
        :return: None
        """
        self.cursor.execute("""DELETE FROM sessions""")
        self.conn.commit()

    #########################
    # Окончание работы с БД #
    #########################

    def close(self):
        """        Закрыть соединение с БД
        :return: None
        """
        self.conn.close()