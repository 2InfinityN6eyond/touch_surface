import os
import sys
import json
from multiprocessing import Process, Queue, Value, Pipe
from PyQt5 import QtWidgets, QtGui, QtCore

from scripts.pose_calculator import Posecalculator 
from scripts.bluetooth_reciever import BluetoothReciever
from scripts.data_bridge import DataBridge
from scripts.main_window import  MainWindow

if __name__ == "__main__" :
    resource_root_path = "/".join(
        os.path.abspath(
            os.path.dirname(sys.argv[0])
        ).split("/")[:-1]
    ) + "/"

    data_root_path = os.path.join(resource_root_path, "data")
    os.makedirs(data_root_path, exist_ok=True)

    pose_calculator_to_data_bridtge   = Queue()
    bluetooth_reciever_to_data_bridge = Queue()

    pose_calculator = Posecalculator(
        pose_calculator_to_data_bidge = pose_calculator_to_data_bridtge,
        image_hiegh = 1280,
        image_width = 720
    )

    bluetooth_reciever = BluetoothReciever(
        bluetooth_reciever_to_da1                                                                                                                                                                                                                                           ta_bridge
    )

    data_bridge = DataBridge(
        from_realsense_wrapper = pose_calculator_to_data_bridtge,
        from_bluetooth_reciever = bluetooth_reciever_to_data_bridge
    ) 

    app = QtWidgets.QApplication(sys.argv)

    main_window = MainWindow(
        pose_calculator    = pose_calculator,
        bluetooth_reciever = bluetooth_reciever,
        data_bridge        = data_bridge
    )

    sys.exit(app.exec_())