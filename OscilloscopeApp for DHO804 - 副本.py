import sys
import pyvisa
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QPushButton,QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QComboBox, QMessageBox, QInputDialog    
from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QGuiApplication
import time
            

class ToggleButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)  # 使按钮可切换
        self.setStyleSheet("background-color: red")  # 初始颜色为红色
        self.clicked.connect(self.toggle_color)

    def toggle_color(self):
        if self.isChecked():
            self.setStyleSheet("background-color: green")  # 打开时变绿
            self.setText("ON")
        else:
            self.setStyleSheet("background-color: red")  # 关闭时变红
            self.setText("OFF")


class OscilloscopeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.rm = pyvisa.ResourceManager()
        self.prompt_for_device_address()
        self.oscilloscope.write(':AUToset:PEAK ON')
        self.oscilloscope.write(':AUToset:OPENch ON')
        self.oscilloscope.write(':AUToset:OVERlap ON')
        self.oscilloscope.write(':AUToset:KEEPcoup ON')
        self.oscilloscope.write(':WAVeform:MODE NORMal')
        self.oscilloscope.write(':WAVeform:POINts 1000')
        self.oscilloscope.write(':WAVEFORM:FORMAT ASCII')
        self.initUI()
        self.current_channel = 'CHANnel1'
        self.inverse_time = self.inverse_time_dict()
        self.inverse_voltage = self.inverse_voltage_dict()
        self.voltage_scale=None
        self.time_scale=None
        self.check_20M()
        self.query_coupling()
        self.query_current_scales()
        self.timer = QTimer(self)
        self.timer1 = QTimer(self)
        self.timer.timeout.connect(self.check_scale_change)
        self.timer.timeout.connect(self.check_coupling_change)
        self.timer.timeout.connect(self._20_M_control)
        self.timer.timeout.connect(self.update_frequency)
        self.timer.timeout.connect(self.update_vpp)
        self.timer1.timeout.connect(self.update_waveform)
        self.timer.start(300)
        self.timer1.start(600)

    def initUI(self):
        self.setWindowTitle('示波器波形显示软件')
        self.resize(1920, 1080)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        left_panel = QVBoxLayout()
        main_layout.addLayout(left_panel)
        
        Auto_button = QPushButton('Autoset')
        Auto_button.setStyleSheet("font-size: 40px;")
        Auto_button.clicked.connect(self.autoset)
        left_panel.addWidget(Auto_button)

        channel_label = QLabel('通道:')
        channel_label.setStyleSheet("font-size: 40px;")
        left_panel.addWidget(channel_label)
        self.channel_selector = QComboBox()
        self.channel_selector.addItems(['CHANnel1', 'CHANnel2', 'CHANnel3', 'CHANnel4'])
        self.channel_selector.currentTextChanged.connect(self.change_channel)
        self.channel_selector.setStyleSheet("font-size: 40px;")
        left_panel.addWidget(self.channel_selector)

        coupling_label = QLabel('耦合方式:')
        coupling_label.setStyleSheet("font-size: 40px;")
        left_panel.addWidget(coupling_label)
        self.coupling_selector = QComboBox()
        self.coupling_selector.addItems(['AC', 'DC', 'GND'])
        self.coupling_selector.currentTextChanged.connect(self.change_coupling)
        self.coupling_selector.setStyleSheet("font-size: 40px;")
        left_panel.addWidget(self.coupling_selector)

        _20M_label = QLabel('20M限制:')
        _20M_label.setStyleSheet("font-size: 40px;")
        left_panel.addWidget(_20M_label)
        self.toggle_button = ToggleButton("OFF")
        left_panel.addWidget(self.toggle_button)

        time_scale_label = QLabel('时间刻度:')
        time_scale_label.setStyleSheet("font-size: 40px;")
        left_panel.addWidget(time_scale_label)

        self.time_scale_selector = QComboBox()
        self.time_scale_selector.addItems(['2ns', '5ns', '10ns', '50ns', '100ns', '200ns', '500ns','1us','2us', '5us', '10us', '50us', '100us', '200us', '500us','1ms','2ms', '5ms', '10ms', '50ms', '100ms', '200ms', '500ms','1s','2s', '5s', '10s', '50s', '100s', '200s', '500s'])
        self.time_scale_selector.currentTextChanged.connect(self.update_time_scale)
        self.time_scale_selector.setStyleSheet("font-size: 40px;")
        left_panel.addWidget(self.time_scale_selector)

        voltage_scale_label = QLabel('电压刻度:')
        voltage_scale_label.setStyleSheet("font-size: 40px;")
        left_panel.addWidget(voltage_scale_label)

        self.voltage_scale_selector = QComboBox()
        self.voltage_scale_selector.addItems(['200uv', '500uv', '1mv', '2mv', '5mv', '10mv', '20mv', '50mv', '100mv', '200mv', '500mv', '1v', '2v', '5v', '10v'])
        self.voltage_scale_selector.currentTextChanged.connect(self.update_voltage_scale)
        self.voltage_scale_selector.setStyleSheet("font-size: 40px;")
        left_panel.addWidget(self.voltage_scale_selector)

        self.vpp_label = QLabel('峰峰值: N/A')
        self.vpp_label.setStyleSheet("font-size: 40px;")
        left_panel.addWidget(self.vpp_label)

        self.frequency_label = QLabel('频率: N/A')
        self.frequency_label.setStyleSheet("font-size: 40px;")
        left_panel.addWidget(self.frequency_label)

        Quit_button = QPushButton('退出')
        Quit_button.setStyleSheet("font-size: 40px;")
        Quit_button.clicked.connect(self.quit)
        left_panel.addWidget(Quit_button)

        center_panel = QVBoxLayout()
        main_layout.addLayout(center_panel, 1)
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        center_panel.addWidget(self.canvas)

        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QGuiApplication.screens()[0].geometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def prompt_for_device_address(self):
        devices = self.rm.list_resources()
        if devices:
            device_address, ok = QInputDialog.getItem(self, '选择设备', '请选择示波器的设备地址:', devices, 0, False)
            if ok and device_address:
                self.connect_to_oscilloscope(device_address)
            else:
                sys.exit(1)
        else:
            QMessageBox.warning(self, '无设备', '未检测到任何VISA设备。请确保示波器已连接。')
            sys.exit(1)

    def connect_to_oscilloscope(self, device_address):
        try:
            self.oscilloscope = self.rm.open_resource(device_address)
            self.oscilloscope.timeout = 5000  # Increase timeout to 5000 ms
        except pyvisa.errors.VisaIOError:
            QMessageBox.warning(self, '连接错误', '无法连接到示波器，请检查设备地址是否正确。')
            self.prompt_for_device_address()

    def query_coupling(self):
        try:
            self.coupling = self.oscilloscope.query(f':{self.current_channel}:COUPling?')
            self.coupling_selector.setCurrentText(self.coupling.strip())
        except Exception as e:
            print(f"设置示波器当前耦合方式时报错: {e}")

    def query_current_scales(self):
        try:
            self.time_scale = float(self.oscilloscope.query(':TIMebase:MAIN:SCALe?'))
            self.time_scale_selector.setCurrentText(self.inverse_time[self.time_scale])
            self.voltage_scale = float(self.oscilloscope.query(f':{self.current_channel}:SCALE?'))
            self.voltage_scale_selector.setCurrentText(self.inverse_voltage[self.voltage_scale])
        except Exception as e:
            print(f"设置示波器当前刻度时报错: {e}")

    def check_scale_change(self):
        try:
            new_time_scale = float(self.oscilloscope.query(':TIMebase:MAIN:SCALe?'))
            new_voltage_scale = float(self.oscilloscope.query(f':{self.current_channel}:SCALE?'))
            if new_time_scale != self.time_scale or new_voltage_scale != self.voltage_scale:
                self.query_current_scales()
        except Exception as e:
            print(f"检查刻度变化时报错: {e}")

    def check_coupling_change(self):
        try:
            new_coupling=self.oscilloscope.query(f':{self.current_channel}:COUPling?')
            if new_coupling!=self.coupling:
                self.query_coupling()
        except Exception as e:
            print(f"检查耦合方式变化时报错: {e}")

    def check_20M(self):
        if self.oscilloscope.query(f':{self.current_channel}:BWLimit?') == '20M':
            self.toggle_button.setChecked(True)
        else:
            self.toggle_button.setChecked(False)

    def _20_M_control(self):
        if self.toggle_button.isChecked():
            self.oscilloscope.write(f':{self.current_channel}:BWLimit 20M')
            time.sleep(0.5)
        elif self.toggle_button.isChecked() == False:
            self.oscilloscope.write(f':{self.current_channel}:BWLimit OFF')
            time.sleep(0.5)
        else:
            pass

    def change_coupling(self, coupling):
        self.coupling = coupling
        if  self.oscilloscope.query(f':{self.current_channel}:COUPling?').strip != self.coupling:
            self.oscilloscope.write(f':{self.current_channel}:COUPling {self.coupling}')
            time.sleep(0.1)
        else:
            pass
    
    def update_time_scale(self, value):
        time_scale_dict = self.time_dict()
        self.time_scale = time_scale_dict[value]
        self.oscilloscope.write(f':TIMebase:MAIN:SCALe {self.time_scale}')
        self.update_waveform()

    def update_voltage_scale(self, value):
        voltage_scale_dict = self.voltage_dict()
        self.voltage_scale = voltage_scale_dict[value]
        self.oscilloscope.write(f':{self.current_channel}:SCALe {self.voltage_scale}')
        self.update_waveform()

    def change_channel(self, channel):
        self.current_channel = channel
        if self.oscilloscope.query(f':{self.current_channel}:DISPlay?') == False:
            self.timer.stop()
            self.oscilloscope.write(f':{self.current_channel}:DISPlay ON')
            time.sleep(1)
            self.timer.start(1000)
        else:
            pass

    def update_waveform(self):
        try:
            if self.voltage_scale is None or self.time_scale is None:
                self.query_current_scales()  # Ensure scales are set

            self.oscilloscope.write(f':WAVEFORM:SOURCE {self.current_channel}')
            data = self.oscilloscope.query(':WAVEFORM:DATA?')
            data = np.array(data.split(','), dtype=float)

            num_points = len(data)
            time_divisions = 10
            time_per_division = self.time_scale
            time_axis = np.linspace(0, time_divisions * time_per_division, num_points)

            max_voltage = max(data)
            min_voltage = min(data)
            voltage_center = (max_voltage + min_voltage) / 2
            voltage_range = max(abs(max_voltage+0.2), abs(min_voltage+0.2))

            self.ax.clear()
            self.ax.plot(time_axis, data)
            self.ax.set_title('示波器波形', fontsize=36)
            self.ax.set_xlabel('时间 (s)', fontsize=30)
            self.ax.set_ylabel('电压 (V)', fontsize=30)
            self.ax.set_xlim(0, time_divisions * time_per_division)
            self.ax.set_ylim(voltage_center - voltage_range, voltage_center + voltage_range)
            self.ax.grid(True)

            self.canvas.draw()
        except Exception as e:
            print(f"绘图时报错: {e}")

    def update_vpp(self):
        try:
            vpp1 = self.oscilloscope.query(f':MEASure:ITEM? VPP,{self.current_channel}')
            vpp = float(vpp1)
            if vpp>1 and vpp<10:
                self.vpp_label.setText(f'峰峰值:\n{vpp:.2f}V')
            elif vpp<1 and vpp>1e-3:
                self.vpp_label.setText(f'峰峰值:\n{vpp*1e3:.2f}mV')
            elif vpp<1e-3 and vpp>1e-6:
                self.vpp_label.setText(f'峰峰值:\n{vpp*1e6:.2f}uV')
            else:
                self.vpp_label.setText(f'峰峰值:\n N/A')
        except Exception as e:
            print(f"更新峰峰值时报错: {e}")
            self.vpp_label.setText('峰峰值:\n N/A')


    def update_frequency(self):
        try:
            frequency1 = self.oscilloscope.query(f':MEASure:ITEM? FREQuency,{self.current_channel}')
            frequency = float(frequency1)
            if frequency < 1e3:
                self.frequency_label.setText(f'频率:\n{frequency:.2f} Hz')
            elif frequency < 1e6 and frequency >= 1e3:
                self.frequency_label.setText(f'频率:\n{frequency / 1e3:.2f} kHz')
            elif frequency < 1e9 and frequency >= 1e6:
                self.frequency_label.setText(f'频率:\n{frequency / 1e6:.2f} MHz')
            elif frequency < 1e12 and frequency >= 1e9:
                self.frequency_label.setText(f'频率:\n{frequency / 1e9:.2f} GHz')
            else:
                self.frequency_label.setText(f'频率:\n N/A')
        except Exception as e:
            print(f"更新频率时报错: {e}")
            self.frequency_label.setText('频率: N/A')

    def autoset(self):
        self.timer.stop()
        self.timer1.stop()
        time.sleep(0.2)
        self.oscilloscope.write(':AUToset')
        time.sleep(1.5)
        self.timer.start(300)
        self.timer1.start(600)

    def quit(self):
        self.oscilloscope.close()
        self.close()
    
    def time_dict(self):
        return {
            '2ns': 2e-9, '5ns': 5e-9, '10ns': 10e-9, '20ns': 20e-9, '50ns': 50e-9, '100ns': 100e-9, '200ns': 200e-9, '500ns': 500e-9,
            '1us': 1e-6, '2us': 2e-6, '5us': 5e-6, '10us': 10e-6, '20us': 20e-6, '50us': 50e-6, '100us': 100e-6, '200us': 200e-6, '500us': 500e-6,
            '1ms': 1e-3, '2ms': 2e-3, '5ms': 5e-3, '10ms': 10e-3, '20ms': 20e-3, '50ms': 50e-3, '100ms': 100e-3, '200ms': 200e-3, '500ms': 500e-3,
            '1s': 1, '2s': 2, '5s': 5, '10s': 10, '20s': 20, '50s': 50, '100s': 100, '200s': 200, '500s': 500
        }

    def voltage_dict(self):
        return {
            '200uv': 200e-6, '500uv': 500e-6, '1mv': 1e-3, '2mv': 2e-3, '5mv': 5e-3, '10mv': 10e-3, '20mv': 20e-3, '50mv': 50e-3,
            '100mv': 100e-3, '200mv': 200e-3, '500mv': 500e-3, '1v': 1, '2v': 2, '5v': 5, '10v': 10
        }

    def inverse_time_dict(self):
        return dict(zip(self.time_dict().values(), self.time_dict().keys()))

    def inverse_voltage_dict(self):
        return dict(zip(self.voltage_dict().values(), self.voltage_dict().keys()))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = OscilloscopeApp()
    sys.exit(app.exec())
