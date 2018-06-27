from PyQt5 import QtCore, QtWidgets, uic, QtGui

def time_mgm():
    dialog = uic.loadUi('gui/templates/TimeMgm_form.ui')
    try:
        dialog.NameOfTask.setText(task_name)
        dialog.NameOfTask.setAlignment(QtCore.Qt.AlignCenter)
    except Exception as err:
        print(err)

    def get_work():
        interval_of_work = dialog.interval_of_work.value()
        print('interval_of_work', interval_of_work, 'minutes')

    def get_relax():
        interval_of_relax = dialog.interval_of_relax.value()
        print('interval_of_relax', interval_of_relax, 'minutes')

    def sum_work():
        summary_of_work = dialog.SummaryOfWork.value()
        print('summary of work', summary_of_work, 'hours')
        sum_relax()

    def sum_relax():
        summary_of_work = dialog.SummaryOfWork.value()
        interval_of_work = dialog.interval_of_work.value()
        interval_of_relax = dialog.interval_of_relax.value()
        period = (summary_of_work * 60) / (interval_of_work + interval_of_relax)
        dialog.SummaryOfRelax.setText(str(round((interval_of_relax * period) / 60, 1)))