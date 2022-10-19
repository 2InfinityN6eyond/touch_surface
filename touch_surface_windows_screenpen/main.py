import os
import sys
import json
from multiprocessing import Process, Queue, Value, Pipe
from PyQt5 import QtWidgets, QtGui, QtCore

from scripts.pose_calculator import Posecalculator 

from scripts.server_mp import ScreenDrawInitializer


if __name__ == "__main__" :
    resource_root_path = "/".join(
        os.path.abspath(
            os.path.dirname(sys.argv[0])
        ).split("/")[:-1]
    ) + "/"

    data_root_path = os.path.join(
        resource_root_path, "data"
    )
    os.makedirs(data_root_path, exist_ok=True)

    screen_draw_server = ScreenDrawInitializer()    
    screen_draw_server.start()
    
    pose_calculator = Posecalculator()

