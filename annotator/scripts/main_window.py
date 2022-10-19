import os
import time
import cv2
import sys 
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg

from real_time_plot import RealTimePlotWidget
from image_plotter import ImagePlotter
from calibrate import CalibratorWindow

class MainWindow(QtWidgets.QMainWindow):
    def __init__(
        self,
        resource_root_path,
        realsense_wrapper,
        bluetooth_reciever,
        data_bridge,
        to_data_writer
    ):
        super(MainWindow, self).__init__()
        self.to_data_writer = to_data_writer
        self.resource_root_path = resource_root_path

        pressure_sensor_mapping = ["f2", "none", "f3"]
        self.configs_n_vals = {
            "pressure_threshold" : 4000,
            "pressure_sensor_mapping" : pressure_sensor_mapping,
            "image_data" : None,
            "pressure_sensor_data" : {
                "f1" : 0, "f2" : 0, "f3" : 0, "f4" : 0, "f5" : 0,
                "pen" : 0, "eraser" : 0, "none" : 0
            },
            "checker_corner_shape" : (8, 4),
            "homography" : None
        }

        self.initUI()

        def realsenseCb(data) :
            self.configs_n_vals["image_data"] = data
            self.image_plotter_1.update(data["color_1"])
            self.image_plotter_2.update(data["color_2"])
            
            self.saveData()
            return 
            if self.configs_n_vals["homography"] is not None :
                transformed = cv2.warpPerspective(
                    data["color_1"],
                    self.configs_n_vals["homography"],
                    (data['color_1'].shape[1], data["color_1"].shape[0])
                )
                overlayed = np.array(
                    transformed.astype("float32") * 0.5 + 
                    data["color_2"].astype("float32") * 0.5,
                    dtype=np.uint8
                )
                self.image_plotter_3.update(transformed)
                self.image_plotter_4.update(overlayed)
        data_bridge.realsense_recieved.connect(realsenseCb)

        def bluetoothCb(data) :
            binary_vals = list(map(
                lambda x : 1 if x > self.configs_n_vals["pressure_threshold"] else 0,
                data
            ))
            for i, pressure_name in enumerate(self.configs_n_vals["pressure_sensor_mapping"]) :
                self.configs_n_vals["pressure_sensor_data"][pressure_name] = binary_vals[i]

            self.binary_plotter.setText(
                "{:4d} {:4d} {:4d}   {} {} {}".format(
                    data[0], data[1], data[2],
                    binary_vals[0], binary_vals[1], binary_vals[2]
                )
            )
            self.real_widget_1.update(data[0])
            self.real_widget_2.update(data[1])
            self.real_widget_3.update(data[2])
            #self.saveData()
        data_bridge.bluetooth_sensor_recieved.connect(bluetoothCb)

        data_bridge.start()
        realsense_wrapper.start()
        bluetooth_reciever.start()

    def initUI(self) :
        sensor_plot_layout = QtWidgets.QVBoxLayout()
        image_plot_layout  = QtWidgets.QGridLayout()
        main_layout = QtWidgets.QHBoxLayout()

        self.calibrate_trigger_button = QtWidgets.QPushButton(
            "calibrate", self
        )
        self.calibrate_trigger_button.clicked.connect(self.calibrate)
        self.calibrate_trigger_button.setShortcut("c")

        self.record_curr_frame_button = QtWidgets.QPushButton(
            "record_curr_frame", self
        )
        self.record_curr_frame_button.setCheckable(True)
        self.record_curr_frame_button.setChecked(False)
        self.record_curr_frame_button.setShortcut("Ctrl+S")

        self.real_widget_1 = RealTimePlotWidget(
            pen_color=(150, 50, 50), threshold = self.configs_n_vals["pressure_threshold"]
        )
        self.real_widget_2 = RealTimePlotWidget(
            pen_color=(50, 150, 50), threshold = self.configs_n_vals["pressure_threshold"]
        )
        self.real_widget_3 = RealTimePlotWidget(
            pen_color=(50, 50, 150), threshold = self.configs_n_vals["pressure_threshold"]
        )
        self.binary_plotter = QtWidgets.QLabel("0 0 0")
        
        sensor_plot_layout.addWidget(self.record_curr_frame_button)
        sensor_plot_layout.addWidget(self.calibrate_trigger_button)
        sensor_plot_layout.addWidget(self.binary_plotter)
        sensor_plot_layout.addWidget(self.real_widget_1)
        sensor_plot_layout.addWidget(self.real_widget_2)
        sensor_plot_layout.addWidget(self.real_widget_3)

        image_size = (1920, 1080)
        image_size = (960, 540)
        image_size = (480, 270)
        image_size = (720, 405)
        self.image_plotter_1 = ImagePlotter(image_size[0], image_size[1])
        self.image_plotter_2 = ImagePlotter(image_size[0], image_size[1])
        self.image_plotter_3 = ImagePlotter(image_size[0], image_size[1])
        self.image_plotter_4 = ImagePlotter(image_size[0], image_size[1])
        image_plot_layout.addWidget(self.image_plotter_1, 2, 1)
        image_plot_layout.addWidget(self.image_plotter_2, 2, 2)
        image_plot_layout.addWidget(self.image_plotter_3, 1, 1)
        image_plot_layout.addWidget(self.image_plotter_4, 1, 2)

        self.image_plotter_3.update(
            np.zeros((405, 720, 3), dtype=np.uint8) + 255
        )
        self.image_plotter_4.update(
            np.zeros((405, 720, 3), dtype=np.uint8) + 255
        )

        main_layout.addLayout(sensor_plot_layout)
        main_layout.addLayout(image_plot_layout )

        '''
        white_label = ImagePlotter(400, 1900)
        white_label.update(
            c
        )

        main_main_layout = QtWidgets.QVBoxLayout()
        main_main_layout.addLayout(main_layout)
        main_main_layout.addWidget(white_label)
        '''

        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setLayout(main_layout)

        self.setCentralWidget(self.central_widget)
        self.show()
        #self.showMaximized()

    def saveData(self) :
        if self.record_curr_frame_button.isChecked() :
            if (
                    self.configs_n_vals["pressure_sensor_data"] and \
                    self.configs_n_vals["image_data"] # and \
                    #self.configs_n_vals["homography"]
            ) :
                self.to_data_writer.put({
                    "pressure_sensor" : self.configs_n_vals["pressure_sensor_data"],
                    "images" : self.configs_n_vals["image_data"],
                    "homography" : self.configs_n_vals["homography"]
                })

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == QtCore.Qt.Key.Key_Space :
            self.record_curr_frame_button.setChecked(True)
            print("pressed")

    def keyReleaseEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == QtCore.Qt.Key.Key_Space and not a0.isAutoRepeat() :
            self.record_curr_frame_button.setChecked(False)
            print("released")

    def calibrate(self) :
        self.configs_n_vals["homography"] = None
        checkerboard_image_path = os.path.join(
            self.resource_root_path,
            "test",
            "checkerboard_9_5.jpg"
        )

        self.calibrate_window = CalibratorWindow(
            checkerboard_image_path,
            self.configs_n_vals["checker_corner_shape"],
            self
        )
        self.calibrate_window.show()

        def homographyExists() :
            if self.configs_n_vals["homography"] is not None :
                self.calibrate_window = None
        self.timer = QtCore.QTimer()
        self.timer.setInterval(5000)
        self.timer.timeout.connect(homographyExists)
        self.timer.start()
        
if __name__ == "__main__" :
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
