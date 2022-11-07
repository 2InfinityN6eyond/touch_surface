#import pyautogui

#pyautogui.FAILSAFE = False

from multiprocessing import Process, Queue, Pipe, Value
from PyQt5 import QtWidgets, QtCore, QtGui

class MouseController(Process) :
    def __init__(
        self,
        data_queue:Queue
    ) :
        super(MouseController, self).__init__()

        print("mouse controller initialized")

        #self.screen_height = pyautogui.size().height
        #self.screen_width  = pyautogui.size().width
    
        self.data_queue = data_queue

    def run(self) :

        print("mouse controller started")

        i = 0

        while True :
            i += 1
            if i % 100000 == 0 :
                print(i % 100000)
                if i >= 10000000 :
                    i = 1
            try :
                if not self.data_queue.empty() :

                    print(data)

                    data = self.data_queue.get()
                    self.moveTo(data)
            except :
                pass

    def moveTo(coord) :
        #pyautogui.moveTo(*coord)
        pass
   