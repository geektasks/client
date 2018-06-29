import datetime
from PyQt5.QtCore import QDate


def next_day(current_day, days=1):
    day = current_day.day()
    month = current_day.month()
    year = current_day.year()
    curr_day = datetime.date(day=day, month=month, year=year)
    nxt_day = str(curr_day + datetime.timedelta(days=days))
    date_deadline = QDate.fromString(nxt_day, 'yyyy-MM-dd')
    return date_deadline


if __name__ == '__main__':
    current_day = QDate.currentDate()
    print(next_day(current_day))
