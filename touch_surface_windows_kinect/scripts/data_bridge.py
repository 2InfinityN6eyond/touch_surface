
from multiprocessing import Process, Queue, Pipe, Value
from PyQt5 import QtCore
import mediapipe
import cv2

class DataBridge(QtCore.QThread) :
    realsense_recieved = QtCore.pyqtSignal(dict)
    bluetooth_sensor_recieved  = QtCore.pyqtSignal(list)

    def __init__(
        self,
        from_realsense_wrapper = None,
        from_bluetooth_reciever = None
    ) :
        super(DataBridge, self).__init__()
        
        self.from_realsense_wrapper = from_realsense_wrapper
        self.from_bluetooth_reciever = from_bluetooth_reciever
        
    def run(self) :
        while True :
            try :
                if not self.from_realsense_wrapper.empty() :
                    data = self.from_realsense_wrapper.get()
                    self.realsense_recieved.emit(data)
            except :
                pass

            try :
                if not self.from_bluetooth_reciever.empty() :
                    data = self.from_bluetooth_reciever.get()
                    self.bluetooth_sensor_recieved.emit(data)
            except :
                pass