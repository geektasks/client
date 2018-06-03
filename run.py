import sys
from PyQt5 import Qt
from gui.gui import MyWindow

app = Qt.QApplication(sys.argv)

wnd = MyWindow()
wnd.show()
wnd.sign_in()

sys.exit(app.exec())