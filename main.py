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


def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000
    a_lon, a_lat = a
    b_lon, b_lat = b
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor
    distance = math.sqrt(dx * dx + dy * dy)
    return distance


class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.z = 10
        self.lon = 37.620070
        self.lat = 55.753630
        self.type = "sat,skl"
        self.pt = []
        self.pushButton.clicked.connect(self.change_type)
        self.pushButton_2.clicked.connect(self.change_type)
        self.pushButton_3.clicked.connect(self.change_type)
        self.pushButton_4.clicked.connect(self.search)
        self.pushButton_5.clicked.connect(self.remove_last_label)
        self.checkBox.stateChanged.connect(self.update_full_address)
        self.o = 0
        self.overwrite_image()

    def overwrite_image(self):
        open("map.png", "wb").write(
            get(f"http://static-maps.yandex.ru/1.x/?ll={','.join(map(str, [self.lon, self.lat]))}&z={self.z}&l="
                f"{self.type}{'&pt=' if self.pt else ''}{'~'.join(self.pt)}").content)
        self.label.setPixmap(QPixmap("map.png"))

    def screen_to_geo(self, pos):
        dy = 425 - pos[1]
        dx = pos[0] - 225
        lx = self.lon + dx * 0.0000428 * math.pow(2, 15 - self.z)
        ly = self.lat + dy * 0.0000428 * math.cos(math.radians(self.lat)) * math.pow(2, 15 - self.z)
        return lx, ly

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and 199 < event.y() < 651:
            c = ','.join(map(str, self.screen_to_geo((event.x(), event.y()))))
            g = get(f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={c}&format"
                    f"=json").json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"][
                "metaDataProperty"]["GeocoderMetaData"]
            self.pt += [c]
            self.lineEdit.setText(c)
            try:
                self.lineEdit_2.setText(
                    g["text"] + (f' {g["Address"]["postal_code"]}' if self.checkBox.isChecked() else ""))
            except KeyError:
                self.lineEdit_2.setText(g["text"])
            self.overwrite_image()
        elif event.button() == Qt.RightButton and 199 < event.y() < 651:
            c = ','.join(map(str, self.screen_to_geo((event.x(), event.y()))))
            try:
                g = get(f'https://search-maps.yandex.ru/v1/?apikey=dda3ddba-c9ea-4ead-9010-f43fbc15c6e3&text='
                        f'{self.lineEdit_3.text()}&lang=ru_RU&type=biz&ll={c}').json()["features"][0]
                org_coords = g["geometry"]["coordinates"]
                if lonlat_distance(org_coords, map(float, c.split(","))) <= 50:
                    org_coords = ','.join(map(str, org_coords))
                    response = get(f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geo"
                                   f"code={org_coords}&format=json").json()["response"]["GeoObjectCollection"][
                        "featureMember"][0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]
                    self.pt += [org_coords]
                    self.lineEdit.setText(g["properties"]["CompanyMetaData"]["name"])
                    try:
                        self.lineEdit_2.setText(
                            response["text"] + (
                                f' {response["Address"]["postal_code"]}' if self.checkBox.isChecked() else ""))
                    except KeyError:
                        self.lineEdit_2.setText(response["text"])
                    self.o = 1
                    self.overwrite_image()
            except LookupError:
                pass

    def search(self):
        try:
            g = get(f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode="
                    f"{self.lineEdit.text()}&format=json").json()["response"]["GeoObjectCollection"]["featureMember"][
                0]["GeoObject"]
            self.lon, self.lat = map(float, g["Point"]["pos"].split())
            self.pt += [f'{self.lon},{self.lat}']
            g = g["metaDataProperty"]["GeocoderMetaData"]
            self.lineEdit_2.setText(
                g["text"] + (f' {g["Address"]["postal_code"]}' if self.checkBox.isChecked() else ""))
            self.o = 0
            self.overwrite_image()
        except LookupError:
            pass

    def update_full_address(self):
        if self.lineEdit_2.text():
            try:
                g = get(f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode="
                        f"{self.lineEdit_2.text() if self.o else self.lineEdit.text()}&format=json").json()["response"][
                    "GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]
                self.lineEdit_2.setText(
                    g["text"] + (f' {g["Address"]["postal_code"]}' if self.checkBox.isChecked() else ""))
            except KeyError:
                pass

    def remove_last_label(self):
        self.pt = self.pt[:-1]
        self.lineEdit_2.clear()
        self.lineEdit.clear()
        self.overwrite_image()

    def change_type(self):
        self.type = MAP_TYPES[self.sender().text()]
        self.overwrite_image()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp and self.z < 17:
            self.z += 1
        elif event.key() == Qt.Key_PageDown and self.z > 0:
            self.z -= 1
        elif event.key() == Qt.Key_Left:
            self.lon -= LON_STEP * math.pow(2, 15 - self.z)
        elif event.key() == Qt.Key_Right:
            self.lon += LON_STEP * math.pow(2, 15 - self.z)
        elif event.key() == Qt.Key_Up:
            self.lat += LAT_STEP * math.pow(2, 15 - self.z)
        elif event.key() == Qt.Key_Down:
            self.lat -= LAT_STEP * math.pow(2, 15 - self.z)
        if self.lon > 180:
            self.lon -= 360
        elif self.lon < -180:
            self.lon += 360
        if self.lat > 85:
            self.lat -= 170
        elif self.lat < -85:
            self.lat += 170
        self.overwrite_image()

    def closeEvent(self, event):
        remove("map.png")


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    LAT_STEP = 0.01085
    LON_STEP = 0.01933
    MAP_TYPES = {"Схема": "map", "Спутник": "sat", "Гибрид": "sat,skl"}
    app = QApplication(sys.argv)
    form = MyMainWindow()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
