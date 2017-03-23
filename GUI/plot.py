from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtCore import (QLineF, QPointF, QRectF, Qt, QTimer, QCoreApplication)
from PyQt5.QtGui import (QBrush, QColor, QPainter)
from PyQt5.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem,
                             QGridLayout, QVBoxLayout, QHBoxLayout, QSizePolicy,
                             QLabel, QLineEdit, QPushButton, QDesktopWidget)


# FigureCanvas inherits QWidget
class PlotFrame(FigureCanvas):
    def __init__(self, parent=None, width=4, height=3, dpi=100, data_q=None):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(313)  # PROCESS MEMORY
        self.axes2 = fig.add_subplot(311)  # CPU
        self.axes3 = fig.add_subplot(312)  # GLOBAL MEMORY
        self.axes.hold(False)
        self.axes2.hold(False)
        self.axes3.hold(False)
        self.q = data_q

        super(PlotFrame, self).__init__(fig)
        self.setParent(parent)
        self.resize(600, 1200)
        self.center()

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        timer = QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1000)

        self.setWindowTitle("Monitor")

    def update_figure(self):
        if self.q:
            # print(self.q)
            xx, yy_cpu, yy_global_memory, yy_memory = self.serialize()
            self.axes.plot(xx, yy_memory)
            self.axes2.plot(xx, yy_cpu)
            self.axes3.plot(xx, yy_global_memory)
            self.axes.set_ylim(bottom=0.0, top=75.0)
            self.axes2.set_ylim(bottom=0.0, top=100.0)
            self.axes3.set_ylim(bottom=0.0, top=100.0)
            self.axes.set_ylabel("Process Memory%")
            self.axes2.set_ylabel("CPU%")
            self.axes3.set_ylabel("Global Memory%")
            self.draw()

    def serialize(self):
        xx = []
        yy_cpu = []
        yy_global_memory = []
        yy_memory = []
        for x, y_cpu, y_global_memory, y_memory in self.q:
            xx.append(x)
            yy_cpu.append(y_cpu)
            yy_global_memory.append(y_global_memory)
            yy_memory.append(y_memory)
        if len(xx) > 0:
            offset = xx[0]
            for i in range(0, len(xx)):
                xx[i] -= offset
        return xx, yy_cpu, yy_global_memory, yy_memory

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    mainWindow = PlotFrame(width=6, height=3)
    mainWindow.show()
    sys.exit(app.exec_())
