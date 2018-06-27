from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sys


class PopupWindowClass(QtWidgets.QWidget):
    popuphidden = QtCore.pyqtSignal()

    def __init__(self, text, func):
        super(PopupWindowClass, self).__init__()
        self.setWindowFlags(QtCore.Qt.SplashScreen | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        self.setMinimumSize(QtCore.QSize(300, 100))
        self.animation = QtCore.QPropertyAnimation(self, b"windowOpacity", self)
        self.animation.finished.connect(self.hide)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.hideAnimation)
        self.setupUi()
        self.setPopupText(text)
        self.func = func

    def setupUi(self):
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel(self)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.label)
        appearance = self.palette()
        appearance.setColor(QtGui.QPalette.Normal, QtGui.QPalette.Window,
                     QtGui.QColor("gray"))
        self.setPalette(appearance)


    def setPopupText(self, text):
        self.label.setText(text)
        self.label.adjustSize()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseDoubleClickEvent(self, QMouseEvent):
        self.func()
        QtWidgets.QWidget.hide(self)
        self.popuphidden.emit()
        # if __name__ == '__main__':
        #     sys.exit()

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

    def show(self):
        self.setWindowOpacity(0.0)
        self.animation.setDuration(1500)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(0.7)
        QtWidgets.QWidget.show(self)
        self.animation.start()
        self.timer.start(5000)

    def hideAnimation(self):
        self.timer.stop()
        self.animation.setDuration(1500)
        self.animation.setStartValue(0.7)
        self.animation.setEndValue(0.0)
        self.animation.start()

    def hide(self):
        if self.windowOpacity() == 0:
            QtWidgets.QWidget.hide(self)
            self.popuphidden.emit()
            if __name__ == '__main__':
                sys.exit()

    def move2RightBottomCorner(win):
        try:
            screen_geometry = QtWidgets.QApplication.desktop().availableGeometry()
            screen_size = (screen_geometry.width(), screen_geometry.height())
            win_size = (win.frameSize().width(), win.frameSize().height())
            x = screen_size[0] - win_size[0] - 10
            y = screen_size[1] - win_size[1] - 10
            win.move(x, y)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    def func():
        dialog = uic.loadUi('templates/dial.ui')
        dialog.exec()
    app = QtWidgets.QApplication(sys.argv)
    main_window = PopupWindowClass('некий текст', func)
    main_window.show()
    main_window.move2RightBottomCorner()
    sys.exit(app.exec_())