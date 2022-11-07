import os
import cv2
import sys
import numpy as np
from PyQt5 import QtGui
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                             QToolTip, QMessageBox, QLabel)

from PyQt5 import QtWidgets, QtCore


class CalibratorWindow(QtWidgets.QMainWindow) :
    def __init__(
        self,
        image_path,
        parent
    ) :
        super(CalibratorWindow, self).__init__()
        
        self.parent = parent
        size_object = QtWidgets.QDesktopWidget().screenGeometry(-1)
        self.width  = size_object.width()
        self.height = size_object.height()

        self.showMaximized()
        #self.resize(self.width, self.height)

        self.label = QtWidgets.QLabel()
        self.setCentralWidget(self.label)

        checkerboard_image = cv2.imread(image_path)
        checkerboard_image = cv2.cvtColor(checkerboard_image, cv2.COLOR_BGR2RGB)
        h, w, ch = checkerboard_image.shape
        bytes_per_line = ch * w
        q_image = QtGui.QImage(
            checkerboard_image.data, w, h,
            bytes_per_line,
            QtGui.QImage.Format_RGB888
        ).scaled(self.width - 10, self.height - 100, QtCore.Qt.KeepAspectRatio)
        self.label.setPixmap(QtGui.QPixmap.fromImage(q_image))

        self.timer = QtCore.QTimer()
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.calibrateBase)
        self.timer.start()        

    def calibrateBase(self) :
        print("calibrating")
        try :
            configs_n_vals = self.parent.configs_n_vals

            image_1 = configs_n_vals["image_data"]["color_1"]
            image_2 = configs_n_vals["image_data"]["color_2"]

            ret, corners_1 = cv2.findChessboardCorners(
            image_1, (9, 6), 
            flags = cv2.CALIB_CB_ADAPTIVE_THRESH +
                cv2.CALIB_CB_FAST_CHECK +
                cv2.CALIB_CB_NORMALIZE_IMAGE
            )

            ret, corners_2 = cv2.findChessboardCorners(
                image_2, (9, 6), 
                flags = cv2.CALIB_CB_ADAPTIVE_THRESH +
                    cv2.CALIB_CB_FAST_CHECK +
                    cv2.CALIB_CB_NORMALIZE_IMAGE
            )

            if corners_1 is not None and corners_2 is not None :
                homography, status = cv2.findHomography(corners_1, corners_2)

                self.parent.configs_n_vals["homography"] = homography
        except :
            pass

class Window(QMainWindow):
    def __init__(
        self,
        iamge_path
    ):
        super().__init__()

        self.image_path = iamge_path

        self.title = "First Window"
        self.top = 100
        self.left = 100
        self.width = 680
        self.height = 500

        self.pushButton = QPushButton("Start", self)
        self.pushButton.move(275, 200)
        self.pushButton.setToolTip("<h3>Start the Session</h3>")

        self.pushButton.clicked.connect(self.window2)              # <===

        self.configs_n_vals = {
            "image_data" : {
                "color_1" : np.zeros((100, 100, 3), dtype=np.uint8),
                "color_2" : np.zeros((100, 100, 3), dtype=np.uint8)
            },
            "homography" : None
        }

        self.main_window()

    def main_window(self):
        self.label = QLabel("Manager", self)
        self.label.move(285, 175)
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.show()

    def window2(self):                                             # <===
        self.w = CalibratorWindow(self.image_path, self)
        self.w.show()

        

if __name__ == "__main__":


    resource_root_path = "/".join(
        os.path.abspath(
            os.path.dirname(sys.argv[0])
        ).split("/")[:-1]
    ) + "/"

    app = QApplication(sys.argv)
    window = Window(
        os.path.join(resource_root_path, "test", "checkerboard_11_7.png")
    )
    sys.exit(app.exec())