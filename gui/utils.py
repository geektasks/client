import re
import datetime
from PyQt5.QtCore import QDate, Qt


def next_day(current_day, days=1):
    day = current_day.day()
    month = current_day.month()
    year = current_day.year()
    curr_day = datetime.date(day=day, month=month, year=year)
    nxt_day = str(curr_day + datetime.timedelta(days=days))
    date_deadline = QDate.fromString(nxt_day, 'yyyy-MM-dd')
    return date_deadline


def default_name(task_list, user_name=None):
    '''

    :param task_list: self.ui.taskList
    :return:
    '''
    default_name = 'New task'
    num_of_tasks = task_list.count()
    default_names_list = [task_list.item(i).text() for i in range(num_of_tasks)]
    default_names = re.findall(default_name, ''.join(default_names_list))

    if len(default_names) == 0:
        return default_name if not user_name else default_name + '_' + user_name
    else:
        return default_name + '_' + str(len(default_names)) if not user_name else default_name + '_' + str(
            len(default_names)) + '_' + user_name


if __name__ == '__main__':
    current_day = QDate.currentDate()
    print(next_day(current_day))
