#!/usr/bin/env python3

import datetime
import numpy
import os
import pandas
import sys
import time

import matplotlib.pyplot as plt
import PicoNuclear
import PicoNuclear.tools as tools

from scipy.optimize import curve_fit
from PicoNuclear.pico3000a import PicoScope3000A

from PyQt5.QtWidgets import  *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QFont, QIcon

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


class ConfigWindow(QDialog):

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setWindowTitle('MCA settings')
        self.initUI()


    def initUI(self):
        self.onlyFloat = QDoubleValidator()
        self.onlyInt = QIntValidator()

        self.button_done = QPushButton('Done')
        self.button_done.setFixedWidth(100)
        self.button_done.clicked.connect(self.done_clicked)

        self.button_default = QPushButton('Default')
        self.button_default.setFixedWidth(100)
        self.button_default.clicked.connect(self.default_clicked)

        self.button_cancel = QPushButton('Cancel')
        self.button_cancel.setFixedWidth(100)
        self.button_cancel.clicked.connect(self.cancel_clicked)

        self.label_trigger = QLabel()
        self.label_trigger.setText('Trigger')
        self.label_trigger.setFixedWidth(100)

        self.label_source = QLabel()
        self.label_source.setText('Source')
        self.label_source.setFixedWidth(100)

        self.combo_source = QComboBox()
        self.combo_source.addItems(['A', 'B'])
        self.combo_source.setCurrentText(self.config['trigger']['source'])

        self.label_direction = QLabel()
        self.label_direction.setText('Direction')
        self.label_direction.setFixedWidth(100)

        self.combo_direction = QComboBox()
        self.combo_direction.addItems(['RISING', 'FALLING'])
        self.combo_direction.setCurrentText(
                                    self.config['trigger']['direction'])

        self.label_threshold = QLabel()
        self.label_threshold.setText('Threshold')
        self.label_threshold.setFixedWidth(100)

        self.input_threshold = QLineEdit()
        self.input_threshold.setText('{}'.format(
                            self.config['trigger']['threshold']))
        self.input_threshold.setFixedWidth(100)
        self.input_threshold.setValidator(self.onlyFloat)

        self.label_autotrig = QLabel()
        self.label_autotrig.setText('Autotrigger')
        self.label_autotrig.setFixedWidth(100)

        self.input_autotrig = QLineEdit()
        self.input_autotrig.setText('{}'.format(
                            self.config['trigger']['autotrigger']))
        self.input_autotrig.setFixedWidth(100)
        self.input_autotrig.setValidator(self.onlyInt)

        self.label_adc = QLabel()
        self.label_adc.setText('ADC')
        self.label_adc.setFixedWidth(100)

        self.label_E_range = QLabel()
        self.label_E_range.setText('E range')
        self.label_E_range.setFixedWidth(100)

        self.input_E_range = QLineEdit()
        self.input_E_range.setText('{}'.format(self.config['ch_range']))
        self.input_E_range.setFixedWidth(100)
        self.input_E_range.setValidator(self.onlyInt)

        self.label_t_range = QLabel()
        self.label_t_range.setText('T range')
        self.label_t_range.setFixedWidth(100)

        self.input_t_range = QLineEdit()
        self.input_t_range.setText('{}'.format(self.config['t_range']))
        self.input_t_range.setFixedWidth(100)
        self.input_t_range.setValidator(self.onlyInt)

        self.label_timebase = QLabel()
        self.label_timebase.setText('Timebase')
        self.label_timebase.setFixedWidth(100)

        self.input_timebase = QLineEdit()
        self.input_timebase.setText('{}'.format(self.config['timebase']))
        self.input_timebase.setFixedWidth(100)
        self.input_timebase.setValidator(self.onlyInt)

        self.label_pre = QLabel()
        self.label_pre.setText('Presamples')
        self.label_pre.setFixedWidth(100)

        self.input_pre = QLineEdit()
        self.input_pre.setText('{}'.format(self.config['pre']))
        self.input_pre.setFixedWidth(100)
        self.input_pre.setValidator(self.onlyInt)

        self.label_post = QLabel()
        self.label_post.setText('Postsamples')
        self.label_post.setFixedWidth(100)

        self.input_post = QLineEdit()
        self.input_post.setText('{}'.format(self.config['post']))
        self.input_post.setFixedWidth(100)
        self.input_post.setValidator(self.onlyInt)

        self.label_captures = QLabel()
        self.label_captures.setText('Captures')
        self.label_captures.setFixedWidth(100)

        self.input_captures = QLineEdit()
        self.input_captures.setText('{}'.format(self.config['captures']))
        self.input_captures.setFixedWidth(100)
        self.input_captures.setValidator(self.onlyInt)

        self.label_captures = QLabel()
        self.label_captures.setText('Captures')
        self.label_captures.setFixedWidth(100)

        self.label_chA = QLabel()
        self.label_chA.setText('Ch A')
        self.label_chA.setFixedWidth(100)

        self.label_chB = QLabel()
        self.label_chB.setText('Ch B')
        self.label_chB.setFixedWidth(100)

        self.label_coupling = QLabel()
        self.label_coupling.setText('Coupling')
        self.label_coupling.setFixedWidth(100)

        self.combo_couplingA = QComboBox()
        self.combo_couplingA.addItems(['AC', 'DC'])
        self.combo_couplingA.setCurrentText(
                                self.config['A']['coupling'])

        self.combo_couplingB = QComboBox()
        self.combo_couplingB.addItems(['AC', 'DC'])
        self.combo_couplingB.setCurrentText(
                                self.config['B']['coupling'])

        self.label_range = QLabel()
        self.label_range.setText('Range')
        self.label_range.setFixedWidth(100)

        self.combo_rangeA = QComboBox()
        self.combo_rangeA.addItems(['0.01', '0.02', '0.05', '0.1', '0.2', 
                                    '0.5', '1.0', '2.0', '5.0', '10.0', 
                                    '20.0'])
        self.combo_rangeA.setCurrentText('{}'.format(
                                self.config['A']['range']))

        self.combo_rangeB = QComboBox()
        self.combo_rangeB.addItems(['0.01', '0.02', '0.05', '0.1', '0.2', 
                                    '0.5', '1.0', '2.0', '5.0', '10.0', 
                                    '20.0'])
        self.combo_rangeB.setCurrentText('{}'.format(
                                self.config['B']['range']))

        self.label_offset = QLabel()
        self.label_offset.setText('Offset')
        self.label_offset.setFixedWidth(100)

        self.input_offsetA = QLineEdit()
        self.input_offsetA.setText('{}'.format(
                            self.config['A']['offset']))
        self.input_offsetA.setFixedWidth(100)
        self.input_offsetA.setValidator(self.onlyFloat)

        self.input_offsetB = QLineEdit()
        self.input_offsetB.setText('{}'.format(
                            self.config['B']['offset']))
        self.input_offsetB.setFixedWidth(100)
        self.input_offsetB.setValidator(self.onlyFloat)

        self.label_L = QLabel()
        self.label_L.setText('L')
        self.label_L.setFixedWidth(100)

        self.input_LA = QLineEdit()
        self.input_LA.setText('{}'.format(
            self.config['A']['filter']['L']))
        self.input_LA.setFixedWidth(100)
        self.input_LA.setValidator(self.onlyInt)

        self.input_LB = QLineEdit()
        self.input_LB.setText('{}'.format(
            self.config['B']['filter']['L']))
        self.input_LB.setFixedWidth(100)
        self.input_LB.setValidator(self.onlyInt)

        self.label_G = QLabel()
        self.label_G.setText('G')
        self.label_G.setFixedWidth(100)

        self.input_GA = QLineEdit()
        self.input_GA.setText('{}'.format(
            self.config['A']['filter']['G']))
        self.input_GA.setFixedWidth(100)
        self.input_GA.setValidator(self.onlyInt)

        self.input_GB = QLineEdit()
        self.input_GB.setText('{}'.format(
            self.config['B']['filter']['G']))
        self.input_GB.setFixedWidth(100)
        self.input_GB.setValidator(self.onlyInt)

        self.label_B = QLabel()
        self.label_B.setText('B')
        self.label_B.setFixedWidth(100)

        self.input_BA = QLineEdit()
        self.input_BA.setText('{}'.format(
            self.config['A']['filter']['B']))
        self.input_BA.setFixedWidth(100)
        self.input_BA.setValidator(self.onlyInt)

        self.input_BB = QLineEdit()
        self.input_BB.setText('{}'.format(
            self.config['B']['filter']['B']))
        self.input_BB.setFixedWidth(100)
        self.input_BB.setValidator(self.onlyInt)


        self.label_tau = QLabel()
        self.label_tau.setText('tau')
        self.label_tau.setFixedWidth(100)

        self.input_tauA = QLineEdit()
        self.input_tauA.setText('{}'.format(
            self.config['A']['filter']['tau']))
        self.input_tauA.setFixedWidth(100)
        self.input_tauA.setValidator(self.onlyFloat)

        self.input_tauB = QLineEdit()
        self.input_tauB.setText('{}'.format(
            self.config['B']['filter']['tau']))
        self.input_tauB.setFixedWidth(100)
        self.input_tauB.setValidator(self.onlyFloat)

        layout = QGridLayout()

        hline1 = QFrame()
        hline1.setFrameShape(QFrame.HLine)
        hline1.setFrameShadow(QFrame.Sunken)

        hline2 = QFrame()
        hline2.setFrameShape(QFrame.HLine)
        hline2.setFrameShadow(QFrame.Sunken)

        hline3 = QFrame()
        hline3.setFrameShape(QFrame.HLine)
        hline3.setFrameShadow(QFrame.Sunken)

        layout.addWidget(self.label_trigger, 0, 0, 1, 3)
        layout.addWidget(self.label_source, 1, 0)
        layout.addWidget(self.combo_source, 1, 1)
        layout.addWidget(self.label_direction, 2, 0)
        layout.addWidget(self.combo_direction, 2, 1)
        layout.addWidget(self.label_threshold, 3, 0)
        layout.addWidget(self.input_threshold, 3, 1)
        layout.addWidget(self.label_autotrig, 4, 0)
        layout.addWidget(self.input_autotrig, 4, 1)

        layout.addWidget(hline1, 5, 0, 1, 3)

        layout.addWidget(self.label_adc, 6, 0, 1, 3)
        layout.addWidget(self.label_E_range, 7, 0)
        layout.addWidget(self.input_E_range, 7, 1)
        layout.addWidget(self.label_t_range, 8, 0)
        layout.addWidget(self.input_t_range, 8, 1)
        layout.addWidget(self.label_timebase, 9, 0)
        layout.addWidget(self.input_timebase, 9, 1)
        layout.addWidget(self.label_pre, 10, 0)
        layout.addWidget(self.input_pre, 10, 1)
        layout.addWidget(self.label_post, 11, 0)
        layout.addWidget(self.input_post, 11, 1)
        layout.addWidget(self.label_captures, 12, 0)
        layout.addWidget(self.input_captures, 12, 1)

        layout.addWidget(hline2, 13, 0, 1, 3)

        layout.addWidget(self.label_chA, 14, 1)
        layout.addWidget(self.label_chB, 14, 2)
        layout.addWidget(self.label_coupling, 15, 0)
        layout.addWidget(self.combo_couplingA, 15, 1)
        layout.addWidget(self.combo_couplingB, 15, 2)
        layout.addWidget(self.label_range, 16, 0)
        layout.addWidget(self.combo_rangeA, 16, 1)
        layout.addWidget(self.combo_rangeB, 16, 2)
        layout.addWidget(self.label_offset, 17, 0)
        layout.addWidget(self.input_offsetA, 17, 1)
        layout.addWidget(self.input_offsetB, 17, 2)
        layout.addWidget(self.label_L, 18, 0)
        layout.addWidget(self.input_LA, 18, 1)
        layout.addWidget(self.input_LB, 18, 2)
        layout.addWidget(self.label_G, 19, 0)
        layout.addWidget(self.input_GA, 19, 1)
        layout.addWidget(self.input_GB, 19, 2)
        layout.addWidget(self.label_B, 20, 0)
        layout.addWidget(self.input_BA, 20, 1)
        layout.addWidget(self.input_BB, 20, 2)
        layout.addWidget(self.label_tau, 21, 0)
        layout.addWidget(self.input_tauA, 21, 1)
        layout.addWidget(self.input_tauB, 21, 2)

        layout.addWidget(hline2, 22, 0, 1, 3)

        layout.addWidget(self.button_done, 23, 0)
        layout.addWidget(self.button_default, 23, 1)
        layout.addWidget(self.button_cancel, 23, 2)

        self.setLayout(layout)


    def done_clicked(self):
        self.config['timebase'] = int(self.input_timebase.text())
        self.config['pre'] = int(self.input_pre.text())
        self.config['post'] = int(self.input_post.text())
        self.config['captures'] = int(self.input_captures.text())

        self.config['ch_range'] = int(self.input_E_range.text())
        self.config['ch_bins'] = int(self.input_E_range.text())
        self.config['t_range'] = int(self.input_t_range.text())
        self.config['t_bins'] = int(self.input_t_range.text())

        self.config['trigger'] = {
                'source' : self.combo_source.currentText(),
                'direction' : self.combo_direction.currentText(),
                'threshold' : float(self.input_threshold.text()),
                'autotrigger': int(self.input_autotrig.text())
                }


        self.config['A'] = { 
                            'coupling' : self.combo_couplingA.currentText(),
                            'range' : float(self.combo_rangeA.currentText()),
                            'offset' : float(self.input_offsetA.text()),
                            'filter' : {'L' : int(self.input_LA.text()),
                                        'G' : int(self.input_GA.text()), 
                                        'B' : int(self.input_BA.text()),
                                        'tau' : float(self.input_tauA.text()),
                                        'method' : 'trapezoidal'
                                        }
                            }

        self.config['B'] = { 
                            'coupling' : self.combo_couplingB.currentText(),
                            'range' : float(self.combo_rangeB.currentText()),
                            'offset' : float(self.input_offsetB.text()),
                            'filter' : {'L' : int(self.input_LB.text()),
                                        'G' : int(self.input_GB.text()), 
                                        'B' : int(self.input_BB.text()),
                                        'tau' : float(self.input_tauB.text()),
                                        'method' : 'trapezoidal'
                                        }
                            }

        self.close()


    def cancel_clicked(self):
        self.close()


    def default_clicked(self):
        default_config = os.path.join(PicoNuclear.__path__[0], 'config', 
                'default.xml')
        self.config = {}
        self.config = tools.load_configuration(default_config)
        self.close()


class CalibrationWindow(QDialog):

    def __init__(self, calib):
        super().__init__()
        self.calib = calib
        self.setWindowTitle('MCA settings')
        self.initUI()


    def initUI(self):
        self.onlyFloat = QDoubleValidator()

        self.button_done = QPushButton('Done')
        self.button_done.setFixedWidth(70)
        self.button_done.clicked.connect(self.done_clicked)

        self.button_cancel = QPushButton('Cancel')
        self.button_cancel.setFixedWidth(70)
        self.button_cancel.clicked.connect(self.cancel_clicked)

        self.label_eq = QLabel()
        self.label_eq.setText('E = a1 * CH + a0')
        self.label_eq.setFixedWidth(200)
        self.label_eq.setAlignment(Qt.AlignRight)

        self.label_Aa0 = QLabel()
        self.label_Aa0.setText('Ch A: a0 = ')
        self.label_Aa0.setFixedWidth(70)

        self.input_Aa0 = QLineEdit()
        self.input_Aa0.setText('{}'.format(self.calib['A'][0]))
        self.input_Aa0.setFixedWidth(70)
        self.input_Aa0.setValidator(self.onlyFloat)

        self.label_Aa1 = QLabel()
        self.label_Aa1.setText('a1 = ')
        self.label_Aa1.setFixedWidth(70)

        self.input_Aa1 = QLineEdit()
        self.input_Aa1.setText('{}'.format(self.calib['A'][1]))
        self.input_Aa1.setFixedWidth(70)
        self.input_Aa1.setValidator(self.onlyFloat)

        self.label_Ba0 = QLabel()
        self.label_Ba0.setText('Ch B: a0 = ')
        self.label_Ba0.setFixedWidth(70)

        self.input_Ba0 = QLineEdit()
        self.input_Ba0.setText('{}'.format(self.calib['B'][0]))
        self.input_Ba0.setFixedWidth(70)
        self.input_Ba0.setValidator(self.onlyFloat)

        self.label_Ba1 = QLabel()
        self.label_Ba1.setText('a1 = ')
        self.label_Ba1.setFixedWidth(70)

        self.input_Ba1 = QLineEdit()
        self.input_Ba1.setText('{}'.format(self.calib['B'][1]))
        self.input_Ba1.setFixedWidth(70)
        self.input_Ba1.setValidator(self.onlyFloat)

        layout = QGridLayout()
        layout.addWidget(self.label_eq, 0, 0, 1, 4)

        layout.addWidget(self.label_Aa0, 1, 0)
        layout.addWidget(self.input_Aa0, 1, 1)
        layout.addWidget(self.label_Aa1, 1, 2)
        layout.addWidget(self.input_Aa1, 1, 3)

        layout.addWidget(self.label_Ba0, 2, 0)
        layout.addWidget(self.input_Ba0, 2, 1)
        layout.addWidget(self.label_Ba1, 2, 2)
        layout.addWidget(self.input_Ba1, 2, 3)

        layout.addWidget(self.button_done, 3, 1)
        layout.addWidget(self.button_cancel, 3, 2)

        self.setLayout(layout)


    def done_clicked(self):
        self.calib['A'] = [float(self.input_Aa0.text()), 
                           float(self.input_Aa1.text())]
        self.calib['B'] = [float(self.input_Ba0.text()), 
                           float(self.input_Ba1.text())]
        self.close()


    def cancel_clicked(self):
        self.close()


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('MiniPET')

        self.finish = False
        self.status = 'Ready'
        self.data = None
        default_config = os.path.join(PicoNuclear.__path__[0], 'config', 
                'default.xml')
        self.config = tools.load_configuration(default_config)

        self.calib = {
                            'A' : [0, 1],
                            'B' : [0, 1]
                           }
        self.ch_range = [0, self.config['ch_range']]
        self.ch_bins = self.config['ch_range']
        self.t_range = [int(-self.config['t_range']/2), 
                        int(self.config['t_range']/2)]
        self.t_bins = self.config['t_range']

        self.path_name = os.path.expanduser('~')

        try:
            self.s = PicoScope3000A()

            self.s.set_channel('A', coupling_type=self.config['A']['coupling'], 
                    range_value=self.config['A']['range'], 
                    offset=self.config['A']['offset'])
            self.s.set_channel('B', coupling_type=self.config['B']['coupling'],
                    range_value=self.config['B']['range'], 
                    offset=self.config['B']['offset'])
            self.s.set_trigger(self.config['trigger']['source'],
                        threshold=self.config['trigger']['threshold'],
                        direction=self.config['trigger']['direction'], 
                        auto_trigger=self.config['trigger']['autotrigger'])
            self.clock = self.s.get_interval_from_timebase(
                    self.config['timebase'], 
                    self.config['pre'] + self.config['post'])
        except PicoNuclear.pico3000a.DeviceNotFoundError:
            demo_msg = QMessageBox()
            demo_msg.setIcon(QMessageBox.Warning)
            demo_msg.setWindowTitle('Warning')
            demo_msg.setText('PicoScope not found!')
            demo_msg.setInformativeText(
                    'Demo mode will be used. Do you want to continue?')
            demo_msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            ret_val = demo_msg.exec_()
            if ret_val == QMessageBox.No:
                sys.exit()
	
            self.s = None
            demo_data_path = os.path.join(PicoNuclear.__path__[0], 'demo', 
                                        'demo_data.txt')
            self.demo_data = numpy.loadtxt(demo_data_path)


        self.initUI()


    def initUI(self):

        main = QWidget(self)
        self.setCentralWidget(main)

        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage(self.status)

        action_exit = QAction('Quit', self)
        action_exit.setShortcut('Ctrl+Q')
        action_exit.triggered.connect(qApp.quit)

        action_path = QAction('Data path', self)
        action_path.triggered.connect(self.path_dialog)

        action_mca = QAction('MCA', self)
        action_mca.triggered.connect(self.mca_settings)

        action_calib = QAction('Calibration', self)
        action_calib.triggered.connect(self.calibrate)

        menubar = self.menuBar()
        menu_file = menubar.addMenu('File')
        menu_file.addAction(action_path)
        menu_file.addAction(action_exit)

        menu_set = menubar.addMenu('Settings')
        menu_set.addAction(action_mca)
        menu_set.addAction(action_calib)

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

        self.label_file = QLabel()
        self.label_file.setText('Prefix')
        self.label_file.setFixedWidth(70)
        self.label_file.setAlignment(Qt.AlignRight)

        self.input_file = QLineEdit()
        self.input_file.setText('test')
        self.input_file.setFixedWidth(70)

        self.label_time = QLabel()
        self.label_time.setText('T = ')
        self.label_time.setFixedWidth(70)
        self.label_time.setAlignment(Qt.AlignRight)

        self.input_elapsed = QLineEdit()
        self.input_elapsed.setText('0.00 s')
        self.input_elapsed.setFixedWidth(70)
        self.input_elapsed.setReadOnly(True)
        self.input_elapsed.setStyleSheet("color: black; background-color: gray")


        self.input_time = QLineEdit()
        self.input_time.setText('30')
        self.input_time.setFixedWidth(70)
        self.input_time.setValidator(self.onlyInt)

        self.progress = QProgressBar()
        self.progress.setMaximum(100)

        self.label_a0 = QLabel()
        self.label_a0.setText('A0 = ')
        self.label_a0.setFixedWidth(70)
        self.label_a0.setAlignment(Qt.AlignRight)

        self.input_a0 = QLineEdit()
        self.input_a0.setFixedWidth(70)
        self.input_a0.setAlignment(Qt.AlignLeft)
        self.input_a0.setText('0')
        self.input_a0.setValidator(self.onlyInt)

        self.label_a1 = QLabel()
        self.label_a1.setText('A1 = ')
        self.label_a1.setFixedWidth(70)
        self.label_a1.setAlignment(Qt.AlignRight)

        self.input_a1 = QLineEdit()
        self.input_a1.setFixedWidth(70)
        self.input_a1.setAlignment(Qt.AlignLeft)
        self.input_a1.setText('0')
        self.input_a1.setValidator(self.onlyInt)

        self.label_b0 = QLabel()
        self.label_b0.setText('B0 = ')
        self.label_b0.setFixedWidth(70)
        self.label_b0.setAlignment(Qt.AlignRight)

        self.input_b0 = QLineEdit()
        self.input_b0.setFixedWidth(70)
        self.input_b0.setAlignment(Qt.AlignLeft)
        self.input_b0.setText('0')
        self.input_b0.setValidator(self.onlyInt)

        self.label_b1 = QLabel()
        self.label_b1.setText('B1 = ')
        self.label_b1.setFixedWidth(70)
        self.label_b1.setAlignment(Qt.AlignRight)

        self.input_b1 = QLineEdit()
        self.input_b1.setFixedWidth(70)
        self.input_b1.setAlignment(Qt.AlignLeft)
        self.input_b1.setText('0')
        self.input_b1.setValidator(self.onlyInt)

        self.button_count = QPushButton('Sum')
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

        self.button_fit = QPushButton('Fit peak')
        self.button_fit.setFixedWidth(70)
        self.button_fit.clicked.connect(self.fit)

        self.combo_fit = QComboBox()
        self.combo_fit.addItems(['A', 'A gate', 'B', 'B gate', 'dt'])

        self.label_fit = QLabel()
        self.label_fit.setText('Channel')
        self.label_fit.setFixedWidth(70)
        self.label_fit.setAlignment(Qt.AlignRight)

        font_fit = QFont()
        font_fit.setPointSize(11)
        font_fit.setFamily("Mono")

        self.input_fit = QPlainTextEdit()
        self.input_fit.setPlainText('')
        self.input_fit.setFont(font_fit)
        self.input_fit.setReadOnly(True)

        hline1 = QFrame()
        hline1.setFrameShape(QFrame.HLine)
        hline1.setFrameShadow(QFrame.Sunken)

        hline2 = QFrame()
        hline2.setFrameShape(QFrame.HLine)
        hline2.setFrameShadow(QFrame.Sunken)

        layout = QGridLayout()
        layout.addWidget(self.button_start, 0, 0)
        layout.addWidget(self.button_stop, 0, 1)
        layout.addWidget(self.label_file, 0, 2)
        layout.addWidget(self.input_file, 0, 3)
        layout.addWidget(self.label_time, 0, 4)
        layout.addWidget(self.input_time, 0, 5)
        layout.addWidget(self.input_elapsed, 0, 6)
        layout.addWidget(self.progress, 0, 7)

        layout.addWidget(hline1, 1, 0, 1, 8)

        layout.addWidget(self.canvas, 2, 0, 1, 8)
        layout.addWidget(self.toolbar, 3, 0, 1, 8)

        layout.addWidget(hline2, 4, 0, 1, 8)

        layout.addWidget(self.label_a0, 5, 0)
        layout.addWidget(self.input_a0, 5, 1)
        layout.addWidget(self.label_a1, 5, 2)
        layout.addWidget(self.input_a1, 5, 3)
        layout.addWidget(self.input_fit, 5, 4, 4, 3)

        layout.addWidget(self.label_b0, 6, 0)
        layout.addWidget(self.input_b0, 6, 1)
        layout.addWidget(self.label_b1, 6, 2)
        layout.addWidget(self.input_b1, 6, 3)

        layout.addWidget(self.button_count, 7, 1)
        layout.addWidget(self.count_label, 7, 2)
        layout.addWidget(self.count_input, 7, 3)

        layout.addWidget(self.button_fit, 8, 1)
        layout.addWidget(self.label_fit, 8, 2)
        layout.addWidget(self.combo_fit, 8, 3)

        main.setLayout(layout)

        self.resize(1280, 960)


    def path_dialog(self):
        self.path_name  = QFileDialog.getExistingDirectory(
                self, "Select existing path", os.path.expanduser('~'))


    def mca_settings(self):
        config_dialog = ConfigWindow(self.config)
        config_dialog.exec_()

        self.config = config_dialog.config

        if self.s is not None:
            self.s.set_channel('A', coupling_type=self.config['A']['coupling'], 
                    range_value=self.config['A']['range'], 
                    offset=self.config['A']['offset'])
            self.s.set_channel('B', coupling_type=self.config['B']['coupling'],
                    range_value=self.config['B']['range'], 
                    offset=self.config['B']['offset'])
            self.s.set_trigger(self.config['trigger']['source'],
                        threshold=self.config['trigger']['threshold'],
                        direction=self.config['trigger']['direction'], 
                        auto_trigger=self.config['trigger']['autotrigger'])


    def calibrate(self):
        calibration = CalibrationWindow(self.calib)
        calibration.exec_()


    def stop(self):
        self.finish = True
        self.status = 'Ready'
        self.statusbar.showMessage(self.status)


    def init_axes(self):
        for i in range(2):
            for j in range(2):
                self.axes[i][j].cla()
                self.axes[i][j].tick_params(axis='both', labelsize=12)
                self.axes[0][0].set_ylim(0, 1)

        self.axes[0][1].set_xlabel('A (ch)', size=14)
        self.axes[0][1].set_ylabel('Counts', size=14)
        self.axes[0][1].set_xlim(self.ch_range[0] * self.calib['A'][1] +
                                                    self.calib['A'][0],
                                 self.ch_range[1] * self.calib['A'][1] +
                                                    self.calib['A'][0])
        self.axes[1][1].set_xlim(self.ch_range[0] * self.calib['A'][1] +
                                                    self.calib['A'][0],
                                 self.ch_range[1] * self.calib['A'][1] +
                                                    self.calib['A'][0])

        self.axes[1][0].set_xlabel('B (ch)', size=14)
        self.axes[1][0].set_ylabel('Counts', size=14)
        self.axes[1][0].set_xlim(self.ch_range[0] * self.calib['B'][1] +
                                                    self.calib['B'][0],
                                 self.ch_range[1] * self.calib['B'][1] +
                                                    self.calib['B'][0])
        self.axes[1][1].set_ylim(self.ch_range[0] * self.calib['B'][1] +
                                                    self.calib['B'][0],
                                 self.ch_range[1] * self.calib['B'][1] +
                                                    self.calib['B'][0])

        self.axes[0][0].set_xlim(self.t_range)
        self.axes[0][0].set_ylabel('Counts', size=14)
        self.axes[0][0].set_xlabel('$\Delta t_{BA}$ (ns)', size=14)

        self.axes[1][1].set_xlabel('A (ch)', size=14)
        self.axes[1][1].set_ylabel('B (ch)', size=14)

        self.figure.tight_layout()


    def update_data(self):
        try:
            a0 = int(self.input_a0.text())
            a1 = int(self.input_a1.text())
            b0 = int(self.input_b0.text())
            b1 = int(self.input_b1.text())
        except ValueError:
            return None

        xl = int(self.get_channel('A', int(self.input_a0.text())))
        xr = int(self.get_channel('A', int(self.input_a1.text())))
        if xl < self.ch_range[0]:
            xl = self.ch_range[0]
        if xr >= self.ch_range[1]:
            xr = self.ch_range[1] - 1

        yl = int(self.get_channel('B', int(self.input_b0.text())))
        yr = int(self.get_channel('B', int(self.input_b1.text())))
        if yl < self.ch_range[0]:
            yl = self.ch_range[0]
        if yr >= self.ch_range[1]:
            yr = self.ch_range[1] - 1


        df = pandas.DataFrame(self.data, columns=['A', 'B', 'tA', 'tB'])
        good = df[df.A >= xl][df.A <= xr][df.B >= yl][df.B <= yr]
        self.count_input.setText('{}'.format(good.shape[0]))

        bins, edges = numpy.histogram(df.tB - df.tA, 
                range=self.t_range, bins=self.t_bins)
        self.data00.set_ydata(bins)
        self.data00.set_xdata(edges[:-1] * self.config['timebase'])
        self.axes[0][0].set_ylim(0, max(bins[5:]) * 1.1)

        bins, edges = numpy.histogram(good.tB - good.tA, 
                range=self.t_range, bins=self.t_bins)
        self.data00g.set_ydata(bins)
        self.data00g.set_xdata(edges[:-1] * self.config['timebase'])

        bins, edges = numpy.histogram(df.A, range=self.ch_range, 
                bins=self.ch_bins)
        self.data01L.set_ydata([0, max(bins) * 2])
        self.data01L.set_xdata(xl * self.calib['A'][1] 
                              + self.calib['A'][0])
        self.data01R.set_ydata([0, max(bins) * 2])
        self.data01R.set_xdata(xr * self.calib['A'][1] 
                              + self.calib['A'][0])
        self.data01.set_ydata(bins)
        self.data01.set_xdata(edges[:-1] * self.calib['A'][1] 
                              + self.calib['A'][0])
        self.axes[0][1].set_ylim(0, max(bins[5:]) * 1.1)

        bins, edges = numpy.histogram(good.A, range=self.ch_range, 
                bins=self.ch_bins)
        self.data01g.set_ydata(bins)
        self.data01g.set_xdata(edges[:-1] * self.calib['A'][1] 
                              + self.calib['A'][0])

        bins, edges = numpy.histogram(df.B, range=self.ch_range, 
                bins=self.ch_bins)
        self.data10L.set_ydata([0, max(bins) * 2])
        self.data10L.set_xdata(yl * self.calib['B'][1] 
                              + self.calib['B'][0])
        self.data10R.set_ydata([0, max(bins) * 2])
        self.data10R.set_xdata(yr * self.calib['B'][1] 
                              + self.calib['B'][0])
        self.data10.set_ydata(bins)
        self.data10.set_xdata(edges[:-1] * self.calib['B'][1] 
                              + self.calib['B'][0])
        self.axes[1][0].set_ylim(0, max(bins[5:]) * 1.1)

        bins, edges = numpy.histogram(good.B, range=self.ch_range, 
                bins=self.ch_bins)
        self.data10g.set_ydata(bins)
        self.data10g.set_xdata(edges[:-1] * self.calib['B'][1] 
                              + self.calib['B'][0])

        self.data11.set_xdata(df.A * self.calib['A'][1] + self.calib['A'][0])
        self.data11.set_ydata(df.B * self.calib['B'][1] + self.calib['B'][0])

        self.data11g.set_xdata(good.A * self.calib['A'][1] + self.calib['A'][0])
        self.data11g.set_ydata(good.B * self.calib['B'][1] + self.calib['B'][0])



    def start(self):
        if self.status == 'Measuring':
            return None

        t_update = 0.1
        self.status = 'Measuring'
        self.statusbar.showMessage(self.status)

        self.input_time.setReadOnly(True)

        self.init_axes()

        self.data00, = self.axes[0][0].plot([0], [0], ds='steps-mid', color='black')
        
        self.data10L, = self.axes[1][0].plot([0], [0], ls='--', color='red')
        self.data10R, = self.axes[1][0].plot([0], [0], ls='--', color='red')
        self.data10, = self.axes[1][0].plot([0], [0], ds='steps-mid', color='black')

        self.data01L, = self.axes[0][1].plot([0], [0], ls='--', color='red')
        self.data01R, = self.axes[0][1].plot([0], [0], ls='--', color='red')
        self.data01, = self.axes[0][1].plot([0], [0], ds='steps-mid', color='black')

        self.data11, = self.axes[1][1].plot([0], [0], marker='o', mfc='None', 
                ls='None', color='black')

        self.data00g, = self.axes[0][0].plot([0], [0], ds='steps-mid', color='red')
        self.data10g, = self.axes[1][0].plot([0], [0], ds='steps-mid', color='red')
        self.data01g, = self.axes[0][1].plot([0], [0], ds='steps-mid', color='red')
        self.data11g, = self.axes[1][1].plot([0], [0], marker='o', 
                ls='None', color='red')

        self.finish = False

        max_time = int(self.input_time.text())

        self.data = []

        t0 = datetime.datetime.now()
        t_plot = datetime.datetime.now()

        header = 'Start at {}\n'.format(t0)
        header += 'EA  EB  tA  tB\n'

        while True:
            if self.finish:
                break

            try:
                if self.s is not None:
                    t, [A, B] = self.s.measure_relative_adc(
                                        self.config['pre'], self.config['post'],
                                        num_captures=self.config['captures'],
                                        timebase=self.config['timebase'], 
                                        inverse=True)
                    for i, Ai in enumerate(A):
                        xa = tools.amplitude(A[i, :], self.config['A'],
                                self.clock)
                        xb = tools.amplitude(B[i, :], self.config['B'],
                                self.clock)

                        ta = tools.zero_crossing(A[i, :], 
                                self.config['A']['filter']['B'], 
                                falling=False)
                        tb = tools.zero_crossing(B[i, :], 
                                self.config['B']['filter']['B'], 
                                falling=False)

                        self.data.append([xa, xb, ta, tb])
                else:
                    n = self.demo_data.shape[0]
                    self.data.append(self.demo_data[numpy.random.choice(n)])
                    time.sleep(0.01)

                tnow = datetime.datetime.now()
                dt = (tnow - t0).total_seconds()
                self.progress.setValue(int(dt / max_time * 100))
                self.input_elapsed.setText('{:.2f} s'.format(dt))
                dt_plot = (tnow - t_plot).total_seconds()
                if dt_plot > t_update:
                    self.update_data()
                    self.figure.canvas.draw()
                    self.figure.canvas.flush_events()
                    t_plot = datetime.datetime.now()
                if dt > max_time:
                    self.finish = True
            except KeyboardInterrupt:
                print('\r Stop                ')
                break

        tnow = datetime.datetime.now()
        dt = (tnow - t0).total_seconds()

        footer = 'Stop at {}\n'.format(tnow)
        footer += 'Total running time: {:.3f} s\n'.format(dt)
        footer += 'Total events: {}'.format(len(self.data))

        out_file_name = '{0}_{1.year}{1.month:02}{1.day:02}_{1.hour:02}'\
                '{1.minute:02}{1.second:02}.txt'.format(
                        self.input_file.text(), t0)
        out_file_path  = os.path.join(self.path_name, out_file_name)
        numpy.savetxt(out_file_path, self.data, fmt='%.3f', header=header,
                footer=footer, delimiter=' ')

        self.progress.setValue(100)
        self.input_elapsed.setText('{:.2f} s'.format(dt))
        self.input_time.setReadOnly(False)
        self.status = 'Ready'
        self.statusbar.showMessage(self.status)


    def count(self):
        if self.data is None:
            return None
        self.update_data()
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()


    def fit(self):
        if self.data is None:
            return None
        self.update_data()

        xl = int(self.get_channel('A', int(self.input_a0.text())))
        xr = int(self.get_channel('A', int(self.input_a1.text())))
        if xl < self.ch_range[0]:
            xl = self.ch_range[0]
        if xr >= self.ch_range[1]:
            xr = self.ch_range[1] - 1

        yl = int(self.get_channel('B', int(self.input_b0.text())))
        yr = int(self.get_channel('B', int(self.input_b1.text())))
        if yl < self.ch_range[0]:
            yl = self.ch_range[0]
        if yr >= self.ch_range[1]:
            yr = self.ch_range[1] - 1

        df = pandas.DataFrame(self.data, columns=['A', 'B', 'tA', 'tB'])
        good = df[df.A >= xl][df.A <= xr][df.B >= yl][df.B <= yr]

        if self.combo_fit.currentText() == 'A':
            bins, edges = numpy.histogram(df.A, range=self.ch_range, 
                    bins=self.ch_bins)
            col = 0
            row = 1
            ch = 'A'
        if self.combo_fit.currentText() == 'A good':
            bins, edges = numpy.histogram(good.A, range=self.ch_range, 
                    bins=self.ch_bins)
            col = 0
            row = 1 
            ch = 'A'
        elif self.combo_fit.currentText() == 'B':
            bins, edges = numpy.histogram(df.B, range=self.ch_range, 
                    bins=self.ch_bins)
            xl = yl
            xr = yr
            col = 1
            row = 0
            ch = 'B'
        elif self.combo_fit.currentText() == 'B good':
            bins, edges = numpy.histogram(good.B, range=self.ch_range, 
                    bins=self.ch_bins)
            xl = yl
            xr = yr
            col = 1
            row = 0
            ch = 'B'
        elif self.combo_fit.currentText() == 'dt':
            bins, edges = numpy.histogram(good.tB - good.tA, 
                    range=self.t_range, bins=self.t_bins)
            xl = 0
            xr = self.t_bins - 1
            col = 0
            row = 0
            ch = 'dt'

        try:
            x0 = numpy.argmax(bins[xl:xr]) + edges[xl]
        except ValueError:
            self.input_fit.setPlainText('Fit error')
            return None
        s = (xr - xl) / 3
        a1 = (bins[xr] - bins[xl]) / (edges[xr] - edges[xl])
        a0 = bins[xl] - edges[xl] * a1

        A = (sum(bins[xl:xr]) - a1 / 2 * (edges[xr]**2 - edges[xl]**2) 
                - a0 * (edges[xr] - edges[xl]))
        try:
            popt, pcov = curve_fit(self.peak, edges[xl:xr], bins[xl:xr], 
                                    p0=[A, x0, s, a1, a0])
        except RuntimeError:
            self.input_fit.setPlainText('Fit error')
            return None

        if ch == 'dt':
            self.axes[col][row].plot(edges[xl:xr] * self.config['timebase'], 
                    self.peak(edges[xl:xr], *popt), '--')
        else:
            self.axes[col][row].plot(edges[xl:xr] * self.calib[ch][1] + 
                    self.calib[ch][0], self.peak(edges[xl:xr], *popt),
                                '--')

        perr = numpy.sqrt(numpy.diag(pcov))

        params = ['A', 'x0', 's', 'a0', 'a1']
        text = ''
        for i in [1, 2]:
            if ch == 'dt':
                text += '{} = {:.1f} +/- {:.2f}\n'.format(params[i], 
                        popt[i] * self.config['timebase'], 
                        perr[i] * self.config['timebase'])
            else:
                text += '{} = {:.1f} +/- {:.2f}\n'.format(params[i], 
                        popt[i] * self.calib[ch][1] + self.calib[ch][0],
                        perr[i] * self.calib[ch][1] + self.calib[ch][0])
        self.input_fit.setPlainText(text)
        for i in [0, 3, 4]:
            text += '{} = {:.1f} +/- {:.2f}\n'.format(params[i], popt[i], perr[i])
        self.input_fit.setPlainText(text)

        self.figure.canvas.draw()
        self.figure.canvas.flush_events()


    def get_channel(self, ch, energy):
        return (energy - self.calib[ch][0]) / self.calib[ch][1]


    def peak(self, x, A, x0, s, a1, a0):
        return (A / numpy.sqrt(2 * s**2 * numpy.pi) * 
                numpy.exp(-(x - x0)**2 / (2 * s**2)) + a1 * x + a0)


    def closeEvent(self, event):
        self.finish = True



if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec_())
