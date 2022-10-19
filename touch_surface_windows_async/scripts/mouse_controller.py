from pynput.mouse import Button, Controller
from multiprocessing import Process, Queue, Pipe, Value
from PyQt5 import QtWidgets, QtCore, QtGui

class MouseController(Process) :
    def __init__(
        self,
        data_queue:Queue
    ) :
        super(MouseController, self).__init__()
        self.data_queue = data_queue
        self.mouse = Controller()

    def run(self) :
        while True :
            try :
                if not self.data_queue.empty() :
                    data = self.data_queue.get()
                    self.moveTo(data)
            except :
                pass

    def moveTo(coord) :
        """
        x, y coordinate, int
        """

        self.mouse.position = coord