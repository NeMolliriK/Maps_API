import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from Maps_API import Ui_MainWindow
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPixmap
from os import remove
from requests import get

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        open("map.png", "wb").write(
            get(f"http://static-maps.yandex.ru/1.x/?ll=37.620070,55.753630&z=10&l=sat,skl").content)
        self.label.setPixmap(QPixmap("map.png"))

    def closeEvent(self, event):
        remove("map.png")


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MyMainWindow()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
