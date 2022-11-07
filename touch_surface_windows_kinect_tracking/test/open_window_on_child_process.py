import sys
import multiprocessing as mp

from PyQt5.QtWidgets import QApplication, QMainWindow


class GuiMain(QMainWindow):
    ...
    # Main window with several functions. When a button is clicked, executes 
    # self.button_pressed()

    def button_pressed(self):
        proc1 = OpenWindowProcess()
        proc1.start()


class OpenWindowProcess(mp.Process) :

    def __init__(self):
        mp.Process.__init__(self)
        print("Process PID: " + self.pid)


    def run(self):
        print("Opening window...")
        app = QApplication(sys.argv)
        window = QMainWindow()
        window.show()
        sys.exit(app.exec_())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    application = GuiMain()
    application.show()
    sys.exit(app.exec_())