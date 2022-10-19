import os
import sys
import json
from multiprocessing import Process, Queue, Value, Pipe
from PyQt5 import QtWidgets, QtGui, QtCore

from data_writer import DataWriter
from realsense_wrapper import RealsenseWrapper
from bluetooth_reciever import BluetoothReciever
from data_bridge import DataBridge
from main_window import MainWindow

if __name__ == "__main__" :
    resource_root_path = "/".join(
        os.path.abspath(
            os.path.dirname(sys.argv[0])
        ).split("/")[:-1]
    ) + "/"

    data_root_path = os.path.join(resource_root_path, "data")
    os.makedirs(data_root_path, exist_ok=True)

    main_window_to_data_writer = Queue()
    realsense_wrapper_to_data_bridtge = Queue()
    pressuer_sensor_to_data_bridge    = Queue()

    data_writer = DataWriter(
        data_root_path,
        main_window_to_data_writer
    )
    data_writer.start()

    realsense_wrapper = RealsenseWrapper(
        realsense_wrapper_to_data_bridtge
    )
    bluetooth_reciever = BluetoothReciever(
        pressuer_sensor_to_data_bridge
    )
    data_bridge = DataBridge(
        from_realsense_wrapper = realsense_wrapper_to_data_bridtge,
        from_bluetooth_reciever = pressuer_sensor_to_data_bridge
    )

    app = QtWidgets.QApplication(sys.argv)

    main_window = MainWindow(
        resource_root_path = resource_root_path,
        realsense_wrapper  = realsense_wrapper,
        bluetooth_reciever = bluetooth_reciever,
        data_bridge        = data_bridge,
        to_data_writer     = main_window_to_data_writer
    )

    sys.exit(app.exec_())
