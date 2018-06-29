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
    pattern = '(New task_[\w]+)_[1-9]+'
    num_of_tasks = task_list.count()
    default_names_list = [' '.join(task_list.item(i).text().split(' ')[1:]) for i in range(num_of_tasks)]
    default_names = re.findall(pattern, ''.join(default_names_list))
    task_name = '{}_{}_{}'.format(default_name, user_name, len(default_names))
    if task_name not in default_names_list:
        return task_name
    else:
        i = 0
        while True:
            task_name = '{}_{}_{}'.format(default_name, user_name, i)
            # print('+++', task_name)
            if task_name in default_names_list:
                i += 1
                continue
            else:
                break
        return task_name


if __name__ == '__main__':
    current_day = QDate.currentDate()
    print(next_day(current_day))
