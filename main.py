import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from Maps_API import Ui_MainWindow
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPixmap
from os import remove
from requests import get
from PyQt5.QtCore import Qt
import math

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


def screen_to_geo(self, pos):
    dy = 225 - pos[1]
    dx = pos[0] - 300
    lx = self.lon + dx * 0.0000428 * math.pow(2, 15 - self.zoom)
    ly = self.lat + dy * 0.0000428 * math.cos(math.radians(self.lat)) * math.pow(2, 15 - self.zoom)
    return lx, ly


class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.z = 10
        self.lon = 37.620070
        self.lat = 55.753630
        self.overwrite_image()

    def overwrite_image(self):
        open("map.png", "wb").write(
            get(f"http://static-maps.yandex.ru/1.x/?ll={','.join(map(str, [self.lon, self.lat]))}&z={self.z}&l=sat,skl")
            .content)
        self.label.setPixmap(QPixmap("map.png"))

    def screen_to_geo(self, pos):
        dy = 225 - pos[1]
        dx = pos[0] - 300
        lx = self.lon + dx * 0.0000428 * math.pow(2, 15 - self.zoom)
        ly = self.lat + dy * 0.0000428 * math.cos(math.radians(self.lat)) * math.pow(2, 15 - self.zoom)
        return lx, ly

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp and self.z < 17:
            self.z += 1
        elif event.key() == Qt.Key_PageDown and self.z > 0:
            self.z -= 1
        elif event.key() == Qt.Key_Left:
            self.lon -= LON_STEP * math.pow(2, 15 - self.z)
        elif event.key() == Qt.Key_Right:
            self.lon += LON_STEP * math.pow(2, 15 - self.z)
        elif event.key() == Qt.Key_Up and self.lat < 85:
            self.lat += LAT_STEP * math.pow(2, 15 - self.z)
        elif event.key() == Qt.Key_Down and self.lat > -85:
            self.lat -= LAT_STEP * math.pow(2, 15 - self.z)
        if self.lon > 180:
            self.lon -= 360
        if self.lon < -180:
            self.lon += 360
        self.overwrite_image()

    def closeEvent(self, event):
        remove("map.png")


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    LAT_STEP = 0.008
    LON_STEP = 0.01938
    app = QApplication(sys.argv)
    form = MyMainWindow()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
