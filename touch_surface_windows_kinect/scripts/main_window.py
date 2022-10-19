import os
import time
import cv2
import sys 
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg

class MainWindow(QtWidgets.QMainWindow) :
    def __init__(
        self,
        pose_calculator,
        bluetooth_reciever,
        data_bridge
    ) :

        print("main window initializing")

        super(MainWindow, self).__init__()

        self.configs_n_vals = {
            "homography" : None,
            "checker_corner_shape" : (9, 5)
        }

        central_widget = QtWidgets.QWidget()

        self.setCentralWidget(central_widget)

        data_bridge.start()
        pose_calculator.start()
        bluetooth_reciever.start()