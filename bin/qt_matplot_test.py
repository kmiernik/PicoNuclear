import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QStatusBar,
        QPushButton, QLabel, QLineEdit, QProgressBar, QFrame, QGridLayout)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import numpy
import pandas
import datetime

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('MiniPET')

        self.finish = False
        self.status = 'Ready'

        self.initUI()


    def initUI(self):

        main = QWidget(self)
        self.setCentralWidget(main)

        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage(self.status)

        fig, axes = plt.subplots(2, 2)
        self.figure = fig
        self.axes = axes

        self.init_axes()

        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.onlyInt = QIntValidator()

        self.button_start = QPushButton('Start')
        self.button_start.setFixedWidth(70)
        self.button_start.clicked.connect(self.start)

        self.button_stop = QPushButton('Stop')
        self.button_stop.setFixedWidth(70)
        self.button_stop.clicked.connect(self.stop)

        self.time_label = QLabel()
        self.time_label.setText('T = ')
        self.time_label.setFixedWidth(70)
        self.time_label.setAlignment(Qt.AlignRight)

        self.time_input = QLineEdit()
        self.time_input.setText('10')
        self.time_input.setFixedWidth(70)
        self.time_input.setValidator(self.onlyInt)

        self.progress = QProgressBar()
        self.progress.setMaximum(100)

        self.a0_label = QLabel()
        self.a0_label.setText('A0 = ')
        self.a0_label.setFixedWidth(70)
        self.a0_label.setAlignment(Qt.AlignRight)

        self.a0_input = QLineEdit()
        self.a0_input.setFixedWidth(70)
        self.a0_input.setAlignment(Qt.AlignLeft)
        self.a0_input.setText('0')
        self.a0_input.setValidator(self.onlyInt)

        self.a1_label = QLabel()
        self.a1_label.setText('A1 = ')
        self.a1_label.setFixedWidth(70)
        self.a1_label.setAlignment(Qt.AlignRight)

        self.a1_input = QLineEdit()
        self.a1_input.setFixedWidth(70)
        self.a1_input.setAlignment(Qt.AlignLeft)
        self.a1_input.setText('0')
        self.a1_input.setValidator(self.onlyInt)

        self.b0_label = QLabel()
        self.b0_label.setText('B0 = ')
        self.b0_label.setFixedWidth(70)
        self.b0_label.setAlignment(Qt.AlignRight)

        self.b0_input = QLineEdit()
        self.b0_input.setFixedWidth(70)
        self.b0_input.setAlignment(Qt.AlignLeft)
        self.b0_input.setText('0')
        self.b0_input.setValidator(self.onlyInt)

        self.b1_label = QLabel()
        self.b1_label.setText('B1 = ')
        self.b1_label.setFixedWidth(70)
        self.b1_label.setAlignment(Qt.AlignRight)

        self.b1_input = QLineEdit()
        self.b1_input.setFixedWidth(70)
        self.b1_input.setAlignment(Qt.AlignLeft)
        self.b1_input.setText('0')
        self.b1_input.setValidator(self.onlyInt)

        self.button_count = QPushButton('Count')
        self.button_count.setFixedWidth(70)
        self.button_count.clicked.connect(self.count)

        self.count_label = QLabel()
        self.count_label.setText('N = ')
        self.count_label.setFixedWidth(70)
        self.count_label.setAlignment(Qt.AlignRight)

        self.count_input = QLineEdit()
        self.count_input.setFixedWidth(70)
        self.count_input.setAlignment(Qt.AlignLeft)
        self.count_input.setText('0')
        self.count_input.setReadOnly(True)

        hline1 = QFrame()
        hline1.setFrameShape(QFrame.HLine)
        hline1.setFrameShadow(QFrame.Sunken)

        hline2 = QFrame()
        hline2.setFrameShape(QFrame.HLine)
        hline2.setFrameShadow(QFrame.Sunken)

        hline3 = QFrame()
        hline3.setFrameShape(QFrame.HLine)
        hline3.setFrameShadow(QFrame.Sunken)

        layout = QGridLayout()
        layout.addWidget(self.button_start, 0, 0)
        layout.addWidget(self.button_stop, 0, 1)
        layout.addWidget(self.time_label, 0, 2)
        layout.addWidget(self.time_input, 0, 3)
        layout.addWidget(self.progress, 0, 4, 1, 4)

        layout.addWidget(hline1, 1, 0, 1, 8)

        layout.addWidget(self.canvas, 2, 0, 1, 8)
        layout.addWidget(self.toolbar, 3, 0, 1, 8)

        layout.addWidget(hline2, 4, 0, 1, 8)

        layout.addWidget(self.a0_label, 5, 0)
        layout.addWidget(self.a0_input, 5, 1)
        layout.addWidget(self.a1_label, 5, 2)
        layout.addWidget(self.a1_input, 5, 3)
        layout.addWidget(self.b0_label, 5, 4)
        layout.addWidget(self.b0_input, 5, 5)
        layout.addWidget(self.b1_label, 5, 6)
        layout.addWidget(self.b1_input, 5, 7)

        layout.addWidget(hline3, 6, 0, 1, 8)

        layout.addWidget(self.button_count, 7, 0)
        layout.addWidget(self.count_label, 7, 1)
        layout.addWidget(self.count_input, 7, 2)

        main.setLayout(layout)


    def stop(self):
        self.finish = True
        self.status = 'Ready'
        self.statusbar.showMessage(self.status)


    def init_axes(self):
        for i in range(2):
            for j in range(2):
                self.axes[i][j].cla()
                self.axes[i][j].set_xlim(0, 100)
                self.axes[i][j].set_ylim(0, 100)

        self.axes[0][0].set_xlim(-100, 100)
        self.axes[0][0].set_xlabel('$\Delta$')
        self.axes[0][1].set_xlabel('A')
        self.axes[1][0].set_xlabel('B')

        self.axes[1][1].set_xlabel('A')
        self.axes[1][1].set_ylabel('B')

        self.figure.tight_layout()


    def start(self):
        self.status = 'Running'
        self.statusbar.showMessage(self.status)

        self.time_input.setReadOnly(True)

        self.init_axes()

        data00, = self.axes[0][0].plot([0], [0], ds='steps-mid', color='black')
        data10, = self.axes[1][0].plot([0], [0], ds='steps-mid', color='black')
        data01, = self.axes[0][1].plot([0], [0], ds='steps-mid', color='black')
        data11, = self.axes[1][1].plot([0], [0], marker='o', mfc='None', 
                ls='None', color='black')

        data00g, = self.axes[0][0].plot([0], [0], ds='steps-mid', color='red')
        data10g, = self.axes[1][0].plot([0], [0], ds='steps-mid', color='red')
        data01g, = self.axes[0][1].plot([0], [0], ds='steps-mid', color='red')
        data11g, = self.axes[1][1].plot([0], [0], marker='o', 
                ls='None', color='red')

        self.finish = False

        max_time = int(self.time_input.text())

        data = numpy.zeros((0, 2))

        t0 = datetime.datetime.now()

        x0 = numpy.random.randint(30, 70)
        s = numpy.random.randint(5, 10)
        
        while True:
            if self.finish:
                break

            a0 = int(self.a0_input.text())
            a1 = int(self.a1_input.text())
            b0 = int(self.b0_input.text())
            b1 = int(self.b1_input.text())

            shape = data.shape
            data.resize((shape[0] + 100, 2), refcheck=False)
            data[-100:, :] = numpy.random.normal(x0, s, size=(100, 2))

            df = pandas.DataFrame(data, columns=['A', 'B'])
            good = df[df.A >= a0][df.A <= a1][df.B >= b0][df.B <= b1]
            self.count_input.setText('{}'.format(good.size))

            bins, edges = numpy.histogram(df.B - df.A, 
                    range=(-100, 100), bins=200)
            data00.set_ydata(bins)
            data00.set_xdata(edges[:-1])
            self.axes[0][0].set_ylim(0, max(bins) * 1.1)

            bins, edges = numpy.histogram(good.B - good.A, 
                    range=(-100, 100), bins=200)
            data00g.set_ydata(bins)
            data00g.set_xdata(edges[:-1])
    
            bins, edges = numpy.histogram(df.A, range=(0, 100), bins=100)
            data01.set_ydata(bins)
            data01.set_xdata(edges[:-1])
            self.axes[0][1].set_ylim(0, max(bins) * 1.1)

            bins, edges = numpy.histogram(good.A, range=(0, 100), bins=100)
            data01g.set_ydata(bins)
            data01g.set_xdata(edges[:-1])

            bins, edges = numpy.histogram(df.B, range=(0, 100), bins=100)
            data10.set_ydata(bins)
            data10.set_xdata(edges[:-1])
            self.axes[1][0].set_ylim(0, max(bins) * 1.1)

            bins, edges = numpy.histogram(good.B, range=(0, 100), bins=100)
            data10g.set_ydata(bins)
            data10g.set_xdata(edges[:-1])

            data11.set_xdata(df.A)
            data11.set_ydata(df.B)

            data11g.set_xdata(good.A)
            data11g.set_ydata(good.B)

            self.figure.canvas.draw()
            self.figure.canvas.flush_events()

            dt = (datetime.datetime.now() - t0).total_seconds()
            if dt > max_time:
                self.finish = True
            self.progress.setValue(int(dt / max_time * 100))


        self.time_input.setReadOnly(False)
        self.status = 'Ready'
        self.statusbar.showMessage(self.status)


    def count(self):
        pass


    def closeEvent(self, event):
        self.finish = True



if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec_())
