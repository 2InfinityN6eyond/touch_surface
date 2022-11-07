
import sys 
import random
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg

class RealTimePlotWidget(pg.PlotWidget) :
    def __init__(
        self,
        plot_length = 100,
        pen_color = (150, 50, 50),
        threshold = 4090
    ) :
        super(RealTimePlotWidget, self).__init__()
        self.setBackground("w")
        self.pen = pg.mkPen(color = pen_color)
       
        self.x = list(range(plot_length))
        self.y = [0] * plot_length
        self.data_plot = self.plot(self.x, self.y, pen=pen_color)
        
        self.plot(
            x = list(range(plot_length)),
            y = [threshold] * plot_length
        )
        self.plot(
            x = list(range(plot_length)),
            y = [0] * plot_length
        )


    def update(self, data) :
        self.y = self.y[1:]
        self.y.append(data)
        self.data_plot.setData(x = self.x, y = self.y)


if __name__ == "__main__" :

    class MainWindow(QtWidgets.QMainWindow):

        def __init__(self, *args, **kwargs):
            super(MainWindow, self).__init__(*args, **kwargs)

            self.real_widget_1 = RealTimePlotWidget(pen_color=(50, 150, 50))

            self.timer = QtCore.QTimer()
            self.timer.start(50)
            self.timer.timeout.connect(
                lambda :  self.real_widget_1.update(random.randint(1, 100))
            )

            self.setCentralWidget(self.real_widget_1)


    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
