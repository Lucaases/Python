import sys
from pyvisa import ResourceManager, errors
from numpy import array, linspace, sin, pi,abs,concatenate,fromstring,isfinite,float64
from matplotlib.pyplot import subplots,close
from matplotlib.ticker import FuncFormatter
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QDialogButtonBox, QPushButton, QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QComboBox, QMessageBox, QDialog, QRadioButton, QLineEdit, QSpinBox
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QGuiApplication, QIcon , QDoubleValidator
from time import sleep
from scipy.signal import butter,filtfilt
from scipy.signal.windows import hann
from scipy.fft import fft, fftfreq
from tkinter import Tk,filedialog
from pandas import DataFrame
from os import path
from gc import collect

#采用from ... import ... 方式,可减小exe的大小

#Python可以非常好的模块化,但是我这坏习惯改不了总是喜欢一次在一个文件里全写完,以前C++,C还有头文件和源文件,现在python一个文件就写完了

def resource_path(relative_path):#使用Auto-py-to-exe(PyInstaller)打包时,获取资源路径
    base_path = getattr(sys, '_MEIPASS', path.dirname(path.abspath(__file__)))
    return path.join(base_path, relative_path)

class InputDialog(QDialog):#初始选择VISA地址的对话框
    def __init__(self, rm, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon(resource_path("OIG3.jpg")))
        self.rm = rm
        self.devices = list(self.rm.list_resources())
        self.setWindowTitle('选择设备')
        self.setMinimumSize(500, 300)  # 设置对话框的最小大小
        self.layout1 = QVBoxLayout(self)
        self.label = QLabel('请选择示波器的设备地址:')
        self.label.setStyleSheet("font-size: 30px;")
        self.layout1.addWidget(self.label)
        self.combo_box = QComboBox()
        self.combo_box.setMinimumSize(350, 60)
        self.combo_box.setStyleSheet("font-size: 30px;")
        if len(self.devices) == 0:
            self.devices.append('TEST(模拟模式,纯看界面)')
        self.combo_box.addItems(self.devices)
        self.layout1.addWidget(self.combo_box)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout1.addWidget(self.button_box)

    def get_selected_device(self):
        return self.combo_box.currentText()


class _20MButton(QPushButton):#20M限制按钮,因为初始化时让UI同步示波器上的设置,所以需要绑定状态
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.clicked.connect(self.toggle_color)

    def toggle_color(self):
        if self.isChecked():
            self.setStyleSheet("QPushButton {font-size: 35px;background-color: green;}")
            self.setText("ON")
        else:
            self.setStyleSheet("QPushButton {font-size: 35px;background-color: red;}")
            self.setText("OFF")

class filter_choose(QDialog):#滤波器选择对话框
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('选择窗口')
        self.setMinimumSize(390, 600)
        self.setWindowIcon(QIcon(resource_path("OIG3.jpg")))
        self.radio_button1 = QRadioButton('低通')
        self.radio_button2 = QRadioButton('高通')
        self.radio_button3 = QRadioButton('带通')
        self.radio_button4 = QRadioButton('带阻')
        self.radio_button5 = QRadioButton('关闭')
        self.radio_button1.setStyleSheet("font-size: 30px;")
        self.radio_button2.setStyleSheet("font-size: 30px;")
        self.radio_button3.setStyleSheet("font-size: 30px;")
        self.radio_button4.setStyleSheet("font-size: 30px;")
        self.radio_button5.setStyleSheet("font-size: 30px;")
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.w1_label = QLabel("截止频率w1:")
        self.w1_input = QLineEdit()
        self.w1_input.setValidator(QDoubleValidator(0,4e7,2))  # 设置只能输入数字
        self.w2_label = QLabel("截止频率w2:")
        self.w2_input = QLineEdit()
        self.w2_input.setValidator(QDoubleValidator(0,4e7,2))  # 设置只能输入数字
        self.tip_label = QLabel("提示:可以科学计数法表示(如1e6代表1M)\n截止频率w2必须大于截止频率w1")
        self.order_label = QLabel("阶数:")
        self.order_input = QSpinBox()
        self.w1_label.setStyleSheet("font-size: 20px;")
        self.w1_input.setStyleSheet("font-size: 20px;")
        self.w2_label.setStyleSheet("font-size: 20px;")
        self.w2_input.setStyleSheet("font-size: 20px;")
        self.tip_label.setStyleSheet("font-size: 20px;")
        self.order_label.setStyleSheet("font-size: 20px;")
        self.order_input.setStyleSheet("font-size: 20px;")
        self.order_input.setRange(1, 10)  # 设置阶数范围
        self.w1_label.hide()
        self.w1_input.hide()
        self.w2_label.hide()
        self.w2_input.hide()
        self.tip_label.hide()
        self.order_label.hide()
        self.order_input.hide()

        layout = QVBoxLayout()
        layout.addWidget(self.radio_button1)
        layout.addWidget(self.radio_button2)
        layout.addWidget(self.radio_button3)
        layout.addWidget(self.radio_button4)
        layout.addWidget(self.radio_button5)
        layout.addWidget(self.w1_label)
        layout.addWidget(self.w1_input)
        layout.addWidget(self.w2_label)
        layout.addWidget(self.w2_input)
        layout.addWidget(self.tip_label)
        layout.addWidget(self.order_label)
        layout.addWidget(self.order_input)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

        self.radio_button1.toggled.connect(self.show_inputs)
        self.radio_button2.toggled.connect(self.show_inputs)
        self.radio_button3.toggled.connect(self.show_inputs)
        self.radio_button4.toggled.connect(self.show_inputs)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
    
    def show_inputs(self):
        if self.radio_button1.isChecked() or self.radio_button2.isChecked() :
            self.w1_label.show()
            self.w1_input.show()
            self.w2_label.hide()
            self.w2_input.hide()
            self.order_label.show()
            self.order_input.show()
            self.tip_label.setText("提示:可以科学计数法表示(如1e6代表1M)")
            self.tip_label.show()
        elif self.radio_button3.isChecked() or self.radio_button4.isChecked():
            self.w1_label.show()
            self.w1_input.show()
            self.w2_label.show()
            self.w2_input.show()
            self.tip_label.show()
            self.order_label.show()
            self.order_input.show()
        else:
            self.w1_label.hide()
            self.w1_input.hide()
            self.w2_label.hide()
            self.w2_input.hide()
            self.tip_label.hide()
            self.order_label.hide()
            self.order_input.hide()

class FFTDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon(resource_path("OIG3.jpg")))
        self.setWindowTitle("FFT频谱图")
        self.setMinimumSize(1600, 900)
        layout = QVBoxLayout()
        self.figure, self.ax = subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.save_button = QPushButton("保存频谱图数据(CSV)")
        self.save_button.setStyleSheet("font-size: 20px;")
        self.close_button = QPushButton("关闭")
        self.close_button.setStyleSheet("font-size: 20px;")
        self.close_button.clicked.connect(self.close)
        self.save_button.clicked.connect(self.save)
        layout.addWidget(self.save_button)
        layout.addWidget(self.close_button)
        self.setLayout(layout)
        self.lef_mouse_pressed = False  # 鼠标左键是否按下
        self.connect_event()

    def save(self):#保存波形数据(CSV文件)
        self.save_button.setDisabled(True)
        root = Tk()
        root.withdraw()
        x_data=self.ax.lines[0].get_xdata()
        y_data=self.ax.lines[0].get_ydata()
        y_data_formatted = [f'{y:.6f}' for y in y_data]
        x_data_formatted = [f'{x:.6f}' for x in x_data]
        data = DataFrame({'Frequency': x_data_formatted, 'Magnitude': y_data_formatted})
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],)
        if file_path:
            data.to_csv(file_path, index=False)
            self.save_button.setEnabled(True)
        else:
            QMessageBox.warning(self, '警告', '未选择文件路径。')

    def hpfilter(self,frequency,sample_frequency,order,data):#高通滤波器
        Wc=frequency
        Wn = Wc / (sample_frequency*0.5)
        if 0<Wn<1:
            b, a = butter(order, Wn, btype='highpass')
            filter_data = filtfilt(b, a, data)
            return filter_data
        else:
            return None

    def lpfilter(self,frequency,sample_frequency,order,data):#低通滤波器
        Wc=frequency
        Wn = Wc / (sample_frequency*0.5)
        if 0<Wn<1:
            b, a = butter(order, Wn, btype='lowpass')
            filter_data = filtfilt(b, a,data)
            return filter_data
        else:
            return None

    def bpfilter(self,frequency1,frequency2,sample_frequency,order,data):#带通滤波器
        low = frequency1 / (sample_frequency*0.5)
        high = frequency2 / (sample_frequency*0.5)
        if 0<low<1 and 0<high<1:
            b, a = butter(order, [low, high], btype='bandpass')
            filter_data = filtfilt(b, a,data)
            return filter_data
        else:
            return None
        
    def bsfilter(self,frequency1,frequency2,sample_frequency,order,data):#带阻滤波器
        low = frequency1 / (sample_frequency*0.5)
        high = frequency2 / (sample_frequency*0.5)
        if 0<low<1 and 0<high<1:
            b, a = butter(order, [low, high], btype='bandstop')
            filter_data = filtfilt(b, a,data)
            return filter_data
        else:
            return None
        
    def on_scroll(self,event):#鼠标滚轮缩放
        if self.ax is not None:
            x_min, x_max = self.ax.get_xlim()
            x_delta = (x_max - x_min) / 10		# 控制缩放X轴的比例
            y_min, y_max = self.ax.get_ylim()
            y_delta = (y_max - y_min) / 10		# 控制缩放X轴的比例
            if event.button == "up":
                self.ax.set(xlim=(x_min + x_delta, x_max - x_delta))
                self.ax.set(ylim=(y_min + y_delta, y_max - y_delta))
            elif event.button == "down":
                self.ax.set(xlim=(x_min - x_delta, x_max + x_delta))
                self.ax.set(ylim=(y_min - y_delta, y_max + y_delta))
        self.figure.canvas.draw_idle()

    def on_button_press(self, event):#鼠标按下
        if event.inaxes is not None:  # 判断是否在坐标轴内
            if event.button == 1:
                self.lef_mouse_pressed = True
                self.pre_x = event.xdata
                self.pre_y = event.ydata

    def on_button_release(self, event):#鼠标释放
        self.lef_mouse_pressed = False
        
    def on_mouse_move(self, event):#鼠标移动
        if event.inaxes is not None and event.button == 1:
            if self.lef_mouse_pressed:	#鼠标左键按下时才计算
                x_delta = event.xdata - self.pre_x
                y_delta = event.ydata - self.pre_y
                # 获取当前原点和最大点的4个位置
                x_min, x_max = self.ax.get_xlim()
                y_min, y_max = self.ax.get_ylim()
                # 控制一次移动鼠标拖动的距离
                x_min = x_min - x_delta
                x_max = x_max - x_delta
                y_min = y_min - y_delta
                y_max = y_max - y_delta
                self.ax.set_xlim(x_min, x_max)
                self.ax.set_ylim(y_min, y_max)
                self.figure.canvas.draw_idle()
    
    def connect_event(self):
        self.figure.canvas.mpl_connect("scroll_event", self.on_scroll)
        self.figure.canvas.mpl_connect("button_press_event", self.on_button_press)
        self.figure.canvas.mpl_connect("button_release_event", self.on_button_release)
        self.figure.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)

class OscilloscopeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.rm = ResourceManager()
        self.simulate = False #模拟模式标记
        self.prompt_for_device_address()
        self.simulation_time = 0 
        self.update_time=500 #波形更新时间(ms)
        self.update_time_simulate=1000 #模拟模式下波形更新时间(ms)
        self.frequency=0 #波形频率
        self.filter_w1=0 #滤波器截止频率1
        self.filter_w2=0 #滤波器截止频率2
        self.filter_order=0 #滤波器阶数
        self.filter_lp=False #低通滤波是否打开标记
        self.filter_hp=False #高通滤波是否打开标记
        self.filter_bp=False #带通滤波是否打开标记
        self.filter_bs=False #带阻滤波是否打开标记
        if not self.simulate:  #如果不是模拟模式,初始化示波器
            self.init_oscilloscope()
        self.initUI()
        self.running = True #示波器是否在运行标记
        self.data=None #得到的波形数据
        self.filter_data=None #滤波后的波形数据
        self.current_channel = 'CHANnel1'#默认channel
        self.inverse_time = self.inverse_time_dict()
        self.inverse_voltage = self.inverse_voltage_dict()
        self.voltage_scale = None
        self.time_scale = None
        if not self.simulate:  #如果不是模拟模式,查询设置
            self.check_20M()
        else:
            self.simulate_disable()
        self.query_coupling()
        self.query_current_scales()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_UI)
        if not self.simulate:
            self.timer.start(self.update_time)
        else:
            self.timer.start(self.update_time_simulate)

    def init_oscilloscope(self):#初始化示波器
        self.oscilloscope.write(':Run')#确保示波器在运行
        if self.oscilloscope.query(':CHANnel1:DISPlay?')==False:#检查示波器通道1(默认通道)是否打开
            self.oscilloscope.write(':CHANnel1:DISPlay ON')
        self.oscilloscope.write(':AUToset:PEAK ON')#确保峰峰优先打开
        self.oscilloscope.write(':AUToset:OPENch ON')#确保只AUTOSET已打开通道
        self.oscilloscope.write(':AUToset:OVERlap ON')#确保重叠显示打开
        self.oscilloscope.write(':AUToset:KEEPcoup ON')#确保耦合保持打开
        self.oscilloscope.write(':WAVeform:MODE NORMal')#NORMal方式得到波形数据，读取屏幕显示的波形数据
        self.oscilloscope.write(':WAVeform:FORMAT ASCii')#设置返回格式,ASCII表示以科学计数形式返回各波形点的实际电压值，各电压值之间以逗号分隔。
        self.oscilloscope.write(':ACQuire:MDEPth AUTO')#设置存储深度为自动
        self.sample_frequency=float(self.oscilloscope.query(':ACQuire:SRATe?'))#得到示波器采样频率

    def initUI(self):#初始化UI
        self.setWindowIcon(QIcon(resource_path("OIG3.jpg")))
        self.setWindowTitle('示波器波形显示软件')
        self.resize(1280, 720)
        self.original_width = 1280
        self.original_height = 720

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.left_panel = QVBoxLayout()
        self.main_layout.addLayout(self.left_panel)

        self.closed_label = QLabel('通道已关闭')
        self.closed_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.left_panel.addWidget(self.closed_label)
        self.closed_label.hide()

        self.save_button = QPushButton('保存当前波形(CSV)')
        self.save_button.clicked.connect(self.save)
        self.left_panel.addWidget(self.save_button)
        self.save_button.setDisabled(True)

        self.Auto_button = QPushButton('Autoset')
        self.Auto_button.clicked.connect(self.autoset)
        self.left_panel.addWidget(self.Auto_button)

        self.run_stop_button = QPushButton('Stop')
        self.run_stop_button.clicked.connect(self.run_stop)
        self.left_panel.addWidget(self.run_stop_button)

        self.filter_button = QPushButton('软件滤波')
        self.filter_button.clicked.connect(self.filter_software)
        self.left_panel.addWidget(self.filter_button)

        self.fft_button = QPushButton('软件FFT')
        self.fft_button.clicked.connect(self.FFT_software)
        self.left_panel.addWidget(self.fft_button)

        self.channel_label = QLabel('通道:')
        self.left_panel.addWidget(self.channel_label)
        self.channel_selector = QComboBox()
        self.channel_selector.addItems(['CHANnel1', 'CHANnel2', 'CHANnel3', 'CHANnel4'])
        self.channel_selector.currentTextChanged.connect(self.change_channel)
        self.left_panel.addWidget(self.channel_selector)

        self.close_channel_button = QPushButton('关闭通道')
        self.close_channel_button.clicked.connect(self.close_channel)
        self.left_panel.addWidget(self.close_channel_button)

        self.open_channel_button = QPushButton('打开通道')
        self.open_channel_button.clicked.connect(self.open_channal)
        self.left_panel.addWidget(self.open_channel_button)

        self.coupling_label = QLabel('耦合方式:')
        self.left_panel.addWidget(self.coupling_label)
        self.coupling_selector = QComboBox()
        self.coupling_selector.addItems(['AC', 'DC', 'GND'])
        self.coupling_selector.currentTextChanged.connect(self.change_coupling)
        self.left_panel.addWidget(self.coupling_selector)

        self.pts_label = QLabel('存储深度:')
        self.left_panel.addWidget(self.pts_label)
        self.pts_selector = QComboBox()
        self.pts_selector.addItems(['AUTO','1k','10k','100k','1M','10M','25M','50M'])
        self.pts_selector.currentTextChanged.connect(self.change_pts)
        self.left_panel.addWidget(self.pts_selector)

        self._20M_label = QLabel('20M限制:')
        self.left_panel.addWidget(self._20M_label)
        self.toggle_button = _20MButton("OFF")
        self.toggle_button.clicked.connect(self._20_M_control)
        self.left_panel.addWidget(self.toggle_button)

        self.time_scale_label = QLabel('时间刻度:')
        self.left_panel.addWidget(self.time_scale_label)
        self.time_scale_selector = QComboBox()
        self.time_scale_selector.addItems(['2ns', '5ns', '10ns','20ns', '50ns', '100ns', '200ns', '500ns', '1μs', '2μs', '5μs', '10μs','20μs','50μs', '100μs', '200μs', '500μs', '1ms', '2ms', '5ms', '10ms','20ms','50ms', '100ms', '200ms', '500ms', '1s', '2s', '5s', '10s','20s','50s', '100s', '200s', '500s'])
        self.time_scale_selector.currentTextChanged.connect(self.update_time_scale)
        self.left_panel.addWidget(self.time_scale_selector)

        self.voltage_scale_label = QLabel('电压刻度:')
        self.left_panel.addWidget(self.voltage_scale_label)

        self.voltage_scale_selector = QComboBox()
        self.voltage_scale_selector.addItems(['200μv', '500μv', '1mv', '2mv', '5mv', '10mv', '20mv', '50mv', '100mv', '200mv', '500mv', '1v', '2v', '5v', '10v'])
        self.voltage_scale_selector.currentTextChanged.connect(self.update_voltage_scale)
        self.left_panel.addWidget(self.voltage_scale_selector)

        self.vpp_label = QLabel('峰峰值: N/A')
        self.left_panel.addWidget(self.vpp_label)

        self.frequency_label = QLabel('频率: N/A')
        self.left_panel.addWidget(self.frequency_label)

        self.Quit_button = QPushButton('退出')
        self.Quit_button.clicked.connect(self.close)
        self.left_panel.addWidget(self.Quit_button)

        self.center_panel = QVBoxLayout()
        self.main_layout.addLayout(self.center_panel, 1)
        self.figure, self.ax = subplots()
        self.canvas = FigureCanvas(self.figure)
        self.center_panel.addWidget(self.canvas)

        self.lef_mouse_pressed = False  # 鼠标左键是否按下
        self.center()
        self.show()

        # 初始化窗口大小
        self.update_stylesheets()

    def resizeEvent(self, event):#重写resizeEvent,使UI自适应
        super().resizeEvent(event)
        self.update_stylesheets()

    def update_stylesheets(self):#根据窗口大小更新UI字体大小
        scale_w = min(float(self.width() / self.original_width),1.65)
        scale_h = min(float(self.height() / self.original_height),1.60)
        self.font_size_scale = min(scale_w,scale_h)

        self.channel_label.setStyleSheet(f"font-size: {int(20 * self.font_size_scale)}px;")
        self.coupling_label.setStyleSheet(f"font-size: {int(20 * self.font_size_scale)}px;")
        self.pts_label.setStyleSheet(f"font-size: {int(20 * self.font_size_scale)}px;")
        self._20M_label.setStyleSheet(f"font-size: {int(20 * self.font_size_scale)}px;")
        self.time_scale_label.setStyleSheet(f"font-size: {int(20 * self.font_size_scale)}px;")
        self.voltage_scale_label.setStyleSheet(f"font-size: {int(20 * self.font_size_scale)}px;")
        self.closed_label.setStyleSheet(f"font-size: {int(30 * self.font_size_scale)}px;")
        self.save_button.setStyleSheet(f"font-size: {int(20 * self.font_size_scale)}px;")
        self.Auto_button.setStyleSheet(f"font-size: {int(25 * self.font_size_scale)}px;")
        self.run_stop_button.setStyleSheet(f"QPushButton {{background-color: green; font-size: {int(20 * self.font_size_scale)}px;}}")
        self.filter_button.setStyleSheet(f"QPushButton {{background-color: red; font-size: {int(20 * self.font_size_scale)}px;}}")
        self.fft_button.setStyleSheet(f"font-size: {int(20 * self.font_size_scale)}px;")
        self.channel_selector.setStyleSheet(f"font-size: {int(25 * self.font_size_scale)}px;")
        self.close_channel_button.setStyleSheet(f"font-size: {int(20 * self.font_size_scale)}px;")
        self.open_channel_button.setStyleSheet(f"font-size: {int(20 * self.font_size_scale)}px;")
        self.coupling_selector.setStyleSheet(f"font-size: {int(25 * self.font_size_scale)}px;")
        self.pts_selector.setStyleSheet(f"font-size: {int(25 * self.font_size_scale)}px;")
        self.toggle_button.setStyleSheet(f"QPushButton {{font-size: {int(20 * self.font_size_scale)}px; background-color: red;}}")
        self.time_scale_selector.setStyleSheet(f"font-size: {int(25 * self.font_size_scale)}px;")
        self.voltage_scale_selector.setStyleSheet(f"font-size: {int(25 * self.font_size_scale)}px;")
        self.vpp_label.setStyleSheet(f"font-size: {int(25 * self.font_size_scale)}px;")
        self.frequency_label.setStyleSheet(f"font-size: {int(25 * self.font_size_scale)}px;")
        self.Quit_button.setStyleSheet(f"font-size: {int(20 * self.font_size_scale)}px;")

    def center(self):#使UI置于屏幕中央
        qr = self.frameGeometry()
        cp = QGuiApplication.screens()[0].geometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def on_scroll(self,event):#鼠标滚轮缩放
        if self.ax is not None:
            x_min, x_max = self.ax.get_xlim()
            x_delta = (x_max - x_min) / 10		# 控制缩放X轴的比例
            y_min, y_max = self.ax.get_ylim()
            y_delta = (y_max - y_min) / 10		# 控制缩放X轴的比例
            if y_max - y_min>1e-9:
                if event.button == "up":
                    self.ax.set(xlim=(x_min + x_delta, x_max - x_delta))
                    self.ax.set(ylim=(y_min + y_delta, y_max - y_delta))
                elif event.button == "down":
                    self.ax.set(xlim=(x_min - x_delta, x_max + x_delta))
                    self.ax.set(ylim=(y_min - y_delta, y_max + y_delta))
            else:
                pass
        self.figure.canvas.draw_idle()

    def on_button_press(self, event):#鼠标按下
        if event.inaxes is not None:  # 判断是否在坐标轴内
            if event.button == 1:
                self.lef_mouse_pressed = True
                self.pre_x = event.xdata
                self.pre_y = event.ydata

    def on_button_release(self, event):#鼠标释放
        self.lef_mouse_pressed = False
        
    def on_mouse_move(self, event):#鼠标移动
        if event.inaxes is not None and event.button == 1:
            if self.lef_mouse_pressed:	#鼠标左键按下时才计算
                x_delta = event.xdata - self.pre_x
                y_delta = event.ydata - self.pre_y
                # 获取当前原点和最大点的4个位置
                x_min, x_max = self.ax.get_xlim()
                y_min, y_max = self.ax.get_ylim()
                # 控制一次移动鼠标拖动的距离
                x_min = x_min - x_delta
                x_max = x_max - x_delta
                y_min = y_min - y_delta
                y_max = y_max - y_delta
                self.ax.set_xlim(x_min, x_max)
                self.ax.set_ylim(y_min, y_max)
                self.figure.canvas.draw_idle()
    
    def connect_event(self):
        self.figure.canvas.mpl_connect("scroll_event", self.on_scroll)
        self.figure.canvas.mpl_connect("button_press_event", self.on_button_press)
        self.figure.canvas.mpl_connect("button_release_event", self.on_button_release)
        self.figure.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)

    def simulate_disable(self):#测试模式可能有bug,除电压刻度和时间刻度可以调整,其他控件默认关闭
        self.Auto_button.setDisabled(True)
        self.run_stop_button.setDisabled(True)
        self.save_button.setDisabled(True)
        self.filter_button.setDisabled(True)
        self.coupling_selector.setDisabled(True)
        self.toggle_button.setDisabled(True)
        self.channel_selector.setDisabled(True)
        self.open_channel_button.setDisabled(True)
        self.close_channel_button.setDisabled(True)
        self.fft_button.setDisabled(True)
        self.pts_selector.setDisabled(True)

    def show_controls(self):#(关闭后打开channel)显示控件
        self.coupling_selector.show()
        self.time_scale_selector.show()
        self.voltage_scale_selector.show()
        self.toggle_button.show()
        self.vpp_label.show()
        self.frequency_label.show()
        self.close_channel_button.show()
        self.Quit_button.show()
        self.run_stop_button.show()
        self.Auto_button.show()
        self.closed_label.hide()
        self.save_button.show()
        self.filter_button.show()
        self.pts_selector.show()
        self.fft_button.show()

    def hide_controls(self):#(关闭channel)隐藏控件
        self.coupling_selector.hide()
        self.time_scale_selector.hide()
        self.voltage_scale_selector.hide()
        self.toggle_button.hide()
        self.vpp_label.hide()
        self.frequency_label.hide()
        self.close_channel_button.hide()
        self.run_stop_button.hide()
        self.Auto_button.hide()
        self.closed_label.show()
        self.save_button.hide()
        self.filter_button.hide()
        self.pts_selector.hide()
        self.fft_button.hide()

    def prompt_for_device_address(self):#VISA寻址
        try:
            inputdialog=InputDialog(self.rm)
            devices=list(inputdialog.devices)
            if devices:
                result = inputdialog.exec()
                device_address = inputdialog.get_selected_device()
                if result == QDialog.DialogCode.Accepted and device_address != 'TEST(模拟模式,纯看界面)':
                    self.connect_to_oscilloscope(device_address)
                elif result == QDialog.DialogCode.Accepted and device_address == 'TEST(模拟模式,纯看界面)':
                    self.simulate = True
                else:
                    sys.exit(1)
            else:
                QMessageBox.warning(self, '无设备', '未检测到任何VISA设备。请确保示波器已连接。')
                sys.exit(1)
        finally:
            del inputdialog
            collect()

    def connect_to_oscilloscope(self, device_address):#连接到示波器
        try:
            self.oscilloscope = self.rm.open_resource(device_address)
            self.oscilloscope.timeout = 5000
        except errors.VisaIOError:
            QMessageBox.warning(self, '连接错误', '无法连接到示波器，请检查设备地址是否正确。')
            self.prompt_for_device_address()

    def _20_M_control(self):#切换20M限制打开/关闭
        if self.running and not self.simulate:
            if self.toggle_button.isChecked():
                self.oscilloscope.write(f':{self.current_channel}:BWLimit 20M')
                sleep(0.1)
            elif self.toggle_button.isChecked() == False:
                self.oscilloscope.write(f':{self.current_channel}:BWLimit OFF')
                sleep(0.1)
            else:
                pass
        else:
            self.toggle_button.setChecked(False)
            pass

    def query_coupling(self):#初始化让UI同步示波器的耦合方式
        if not self.simulate:
            try:
                self.coupling = self.oscilloscope.query(f':{self.current_channel}:COUPling?').strip()
                self.coupling_selector.setCurrentText(self.coupling)
            except Exception as e:
                print(f"设置示波器当前耦合方式时报错: {e}")
        else:
            self.coupling_selector.setCurrentText('AC')  # 模拟模式下默认AC耦合

    def query_current_scales(self):#初始化让UI同步示波器的电压刻度和时间刻度
        if self.simulate:
            self.time_scale = 1e-3  # 模拟模式下默认时间刻度
            self.voltage_scale = 0.1  # 模拟模式下默认电压刻度
            self.time_scale_selector.setCurrentText(self.inverse_time[self.time_scale])
            self.voltage_scale_selector.setCurrentText(self.inverse_voltage[self.voltage_scale])
        else:
            try:
                self.time_scale = float(self.oscilloscope.query(':TIMebase:MAIN:SCALe?'))
                self.time_scale_selector.setCurrentText(self.inverse_time[self.time_scale])
                self.voltage_scale = float(self.oscilloscope.query(f':{self.current_channel}:SCALE?'))
                self.voltage_scale_selector.setCurrentText(self.inverse_voltage[self.voltage_scale])
            except Exception as e:
                print(f"设置示波器当前刻度时报错: {e}")

    def check_sample_frequency(self):#检查示波器采样频率
        try:
            new_sample_frequency = float(self.oscilloscope.query(':ACQuire:SRATe?'))
            if new_sample_frequency != self.sample_frequency:
                self.sample_frequency = new_sample_frequency
        except Exception as e:
            print(f"更新采样频率时报错: {e}")
        
    def check_scale_change(self):#检查刻度变化
        try:
            new_time_scale = float(self.oscilloscope.query(':TIMebase:MAIN:SCALe?'))
            new_voltage_scale = float(self.oscilloscope.query(f':{self.current_channel}:SCALE?'))
            if new_time_scale != self.time_scale:
                self.time_scale_selector.setCurrentText(self.inverse_time[new_time_scale])
                self.time_scale = new_time_scale
            if new_voltage_scale != self.voltage_scale:
                self.voltage_scale_selector.setCurrentText(self.inverse_voltage[new_voltage_scale])
                self.voltage_scale = new_voltage_scale
        except Exception as e:
            print(f"更新刻度时报错: {e}")

    def check_20M(self):#检查20M限制是否打开
        try:
            _20M_status = self.oscilloscope.query(f':{self.current_channel}:BWLimit?').strip()
            self.toggle_button.setChecked(_20M_status == '20M')
            self.toggle_button.toggle_color()
        except Exception as e:
            print(f"设置20M限制时报错: {e}")

    def change_channel(self, text):#切换通道
        if self.running:
            self.current_channel = text
            self.timer.stop()
            sleep(0.1)
            try:
                if self.oscilloscope.query(f':{self.current_channel}:DISPlay?')==False:
                    self.oscilloscope.write(f':{self.current_channel}:DISPlay ON')
                    self.running = True
                    self.oscilloscope.write(f':WAVEFORM:SOURCE {self.current_channel}')
                    self.check_20M()
                    self.query_coupling()
                    self.query_current_scales()
                    self.show_controls()
                    self.timer.start(self.update_time)
                else:
                    self.running = True
                    self.oscilloscope.write(f':WAVEFORM:SOURCE {self.current_channel}')
                    self.check_20M()
                    self.query_coupling()
                    self.query_current_scales()
                    self.timer.start(self.update_time)
            except Exception as e:
                print(f"切换通道时报错: {e}")
        else:
            self.current_channel = text
            if self.oscilloscope.query(f':{self.current_channel}:DISPlay?')==False:
                self.oscilloscope.write(f':{self.current_channel}:DISPlay ON')
                self.running = True
                self.check_20M()
                self.query_coupling()
                self.query_current_scales()
                self.show_controls()
                self.timer.start(self.update_time)
                self.show_controls()
            else:
                self.running = True
                self.check_20M()
                self.query_coupling()
                self.query_current_scales()
                self.timer.start(self.update_time)
                self.show_controls()

    def open_channal(self):#打开通道
        if not self.running:
            try:
                self.oscilloscope.write(f':{self.current_channel}:DISPlay ON')
                self.running = True
                self.check_20M()
                self.query_coupling()
                self.query_current_scales()
                self.show_controls()
                self.timer.start(self.update_time)
            except Exception as e:
                print(f"打开通道时报错: {e}")
        else:
            pass

    def close_channel(self):#关闭通道
        if self.running:
            try:
                self.oscilloscope.write(f':{self.current_channel}:DISPlay OFF')
                self.running = False
                self.timer.stop()
                self.ax.clear()
                self.canvas.draw()
                self.hide_controls()
            except Exception as e:
                print(f"关闭通道时报错: {e}")
        else:
            pass

    def change_pts(self,text):#改变存储深度
        if self.running:
            try:
                self.oscilloscope.write(f':ACQuire:MDEPth {text}')
            except Exception as e:
                print(f"改变存储深度时报错: {e}")

    def update_voltage_scale(self, text):#更新电压刻度
        if self.running and not self.simulate:
            try:
                self.voltage_scale = self.voltage_scale_dict()[text]
                self.oscilloscope.write(f':{self.current_channel}:SCALE {self.voltage_scale}')
            except Exception as e:
                print(f"更新电压刻度时报错: {e}")
        elif self.running and self.simulate:
            self.voltage_scale = self.voltage_scale_dict()[text]
        else:
            pass

    def update_time_scale(self, text):#更新时间刻度
        if self.running and not self.simulate:
            try:
                self.time_scale = self.time_scale_dict()[text]
                self.oscilloscope.write(f':TIMebase:MAIN:SCALe {self.time_scale}')
            except Exception as e:
                print(f"更新时间刻度时报错: {e}")
        elif self.running and self.simulate:
            self.time_scale = self.time_scale_dict()[text]
        else:
            pass
        
    def change_coupling(self, text):#更改耦合方式
        if self.running:
            try:
                self.oscilloscope.write(f':{self.current_channel}:COUPling {text}')
            except Exception as e:
                print(f"更新耦合方式时报错: {e}")
        else:
            pass

    def update_UI(self):#更新界面
        if self.running and not self.simulate:
            self.check_sample_frequency()
            self.check_scale_change()
            self.query_waveform_data()
            collect()
        elif self.running and self.simulate:
            self.query_waveform_data()
        else:
            pass

    def query_waveform_data(self):#查询波形数据
        if self.running and not self.simulate:
            try:
                vpp=float(self.oscilloscope.query(f':MEASure:ITEM? VPP,{self.current_channel}'))
                if vpp>1 and vpp<10:
                    self.vpp_label.setText(f'峰峰值:\n{vpp:.2f}V')
                elif vpp<1 and vpp>1e-3:
                    self.vpp_label.setText(f'峰峰值:\n{vpp*1e3:.2f}mV')
                elif vpp<1e-3 and vpp>1e-6:
                    self.vpp_label.setText(f'峰峰值:\n{vpp*1e6:.2f}uV')
                else:
                    self.vpp_label.setText(f'峰峰值:\n N/A')
                self.frequency=float(self.oscilloscope.query(f':MEASure:ITEM? FREQuency,{self.current_channel}'))
                self.frequency_label.setText(f'频率:\n{self.convert_frequency(self.frequency)}')
                self.update_waveform()
            except Exception as e:
                print(f"更新波形数据时报错: {e}")
        elif self.running and self.simulate:
            self.frequency_label.setText(f'频率:\n 1KHz')
            self.vpp_label.setText(f'峰峰值:\n 1.00V')
            self.update_waveform()
        else:
            pass

    def hpfilter(self,time_axis):#高通滤波器
        Wc=self.filter_w1
        Wn = Wc / ((self.sample_frequency/10)*0.5)
        if 0<Wn<1:
            b, a = butter(self.filter_order, Wn, btype='highpass')
            self.filter_data = filtfilt(b, a, self.data)
            self.ax.plot(time_axis,self.filter_data)
        else:
            self.filter_button.setText("软件滤波")
            self.filter_button.setStyleSheet("QPushButton {background-color: red;font-size: 35px;}")
            QMessageBox.warning(self, '错误', '关键频率 Wn 必须在 0 和 1 之间，无法生成数字滤波器。')
            self.filter_hp=False

    def lpfilter(self,time_axis):#低通滤波器
        Wc=self.filter_w1
        Wn = Wc / ((self.sample_frequency/10)*0.5)
        if 0<Wn<1:
            b, a = butter(self.filter_order, Wn, btype='lowpass')
            self.filter_data = filtfilt(b, a, self.data)
            self.ax.plot(time_axis, self.filter_data)
        else:
            self.filter_button.setText("软件滤波")
            self.filter_button.setStyleSheet("QPushButton {background-color: red;font-size: 35px;}")
            QMessageBox.warning(self, '错误', '关键频率 Wn 必须在 0 和 1 之间，无法生成数字滤波器。')
            self.filter_lp=False

    def bpfilter(self,time_axis):#带通滤波器
        low = self.filter_w1 / ((self.sample_frequency/10)*0.5)
        high = self.filter_w2 / ((self.sample_frequency/10)*0.5)
        if 0<low<1 and 0<high<1:
            b, a = butter(self.filter_order, [low, high], btype='bandpass')
            self.filter_data = filtfilt(b, a, self.data)
            self.ax.plot(time_axis, self.filter_data)
        else:
            self.filter_button.setText("软件滤波")
            self.filter_button.setStyleSheet("QPushButton {background-color: red;font-size: 35px;}")
            QMessageBox.warning(self, '错误', '关键频率 Wn 必须在 0 和 1 之间，无法生成数字滤波器。')
            self.filter_bp=False

    def bsfilter(self,time_axis):#带通滤波器
        low = self.filter_w1 / ((self.sample_frequency/10)*0.5)
        high = self.filter_w2 / ((self.sample_frequency/10)*0.5)
        if 0<low<1 and 0<high<1:
            b, a = butter(self.filter_order, [low, high], btype='bandstop')
            self.filter_data = filtfilt(b, a, self.data)
            self.ax.plot(time_axis, self.filter_data)
        else:
            self.filter_button.setText("软件滤波")
            self.filter_button.setStyleSheet("QPushButton {background-color: red;font-size: 35px;}")
            QMessageBox.warning(self, '错误', '关键频率 Wn 必须在 0 和 1 之间，无法生成数字滤波器。')
            self.filter_bp=False

    def voltage_formatter(self, x, pos):#y轴坐标格式设置
        if self.voltage_scale >= 1:
            return f'{x:.2f}V'
        elif self.voltage_scale >= 0.001 and self.voltage_scale <= 1:
            return f'{x * 1000:.2f}mV'
        else:
            return f'{x * 1e6:.2f}μV'
        
    def time_formatter(self, x, pos):#x轴坐标格式设置
        if self.time_scale >= 1:
            return f'{x:.2f}s'
        elif self.time_scale >= 0.001 and self.time_scale <= 1:
            return f'{x * 1000:.2f}ms'
        elif self.time_scale >= 1e-6 and self.time_scale <= 1e-3:
            return f'{x * 1e6:.2f}μs'
        else:
            return f'{x * 1e9:.2f}ns'
        
    def convert_frequency(self,freq):#频率格式转换
        if freq < 1e3:
            return f'{freq:.2f}Hz'
        elif freq < 1e6 and freq >= 1e3:
            return f'{freq/1e3:.2f}kHz'
        elif freq < 1e9 and freq >= 1e6:
            return f'{freq/1e6:.2f}MHz'
        else:
            return 'N/A'
    
    def update_waveform(self):#更新波形
        if self.running:
            try:
                if not self.simulate:
                    time_per_division = self.time_scale
                    voltage_per_division = self.voltage_scale
                    raw_data = self.oscilloscope.query(':WAVeform:DATA?').strip()
                    self.data = array([float(x) for x in raw_data.split(',') if x], dtype=float64)
                    num_points = len(self.data)
                    time_axis = linspace(-10 * time_per_division, 10 * time_per_division, num_points)
                else:
                    num_points = 1000
                    self.simulation_time += 0.2  # 更新模拟时间
                    vpp=1
                    voltage_per_division = self.voltage_scale if self.voltage_scale else 0.1
                    time_per_division = self.time_scale if self.time_scale else 0.001
                    time_axis = linspace(-10 * time_per_division, 10 * time_per_division, num_points)
                    frequency = 1000
                    amplitude = vpp/2  # 根据峰峰值调整振幅
                    self.data = amplitude * sin(2 * pi * frequency * time_axis + self.simulation_time)# 生成正弦波数据
                self.ax.clear()
                if self.filter_lp:
                    self.lpfilter(time_axis)
                    self.ax.set_title(f'示波器波形(经过Wc为{self.convert_frequency(self.filter_w1)}的低通滤波器)', fontsize=int(15*self.font_size_scale))
                elif self.filter_hp:
                    self.hpfilter(time_axis)
                    self.ax.set_title(f'示波器波形(经过Wc为{self.convert_frequency(self.filter_w1)}的高通滤波器)', fontsize=int(15*self.font_size_scale))
                elif self.filter_bp:
                    self.bpfilter(time_axis)
                    self.ax.set_title(f'示波器波形(经过W1为{self.convert_frequency(self.filter_w1)},W2为{self.convert_frequency(self.filter_w2)}的带通滤波器)', fontsize=int(15*self.font_size_scale))
                elif self.filter_bs:
                    self.bsfilter(time_axis)
                    self.ax.set_title(f'示波器波形(经过W1为{self.convert_frequency(self.filter_w1)},W2为{self.convert_frequency(self.filter_w2)}的带阻滤波器)', fontsize=int(15*self.font_size_scale))
                elif not self.filter_lp and not self.filter_hp and not self.filter_bp and not self.filter_bs:
                    self.ax.plot(time_axis, self.data)
                    self.ax.set_title('示波器波形', fontsize=int(18*self.font_size_scale))
                else:
                    pass
                
                self.ax.tick_params(axis='both', which='major', labelsize=int(12*self.font_size_scale))
                self.ax.tick_params(axis='both', which='minor', labelsize=int(5*self.font_size_scale))
                self.ax.set_xlabel('时间', fontsize=int(15*self.font_size_scale))
                self.ax.set_ylabel('电压', fontsize=int(15*self.font_size_scale))
                #self.ax.xaxis.set_major_locator(MultipleLocator(2*time_per_division))
                #self.ax.yaxis.set_major_locator(MultipleLocator(voltage_per_division))
                self.ax.yaxis.set_major_formatter(FuncFormatter(self.voltage_formatter))
                self.ax.xaxis.set_major_formatter(FuncFormatter(self.time_formatter))
                self.ax.set_xlim(-10 * time_per_division, 10 * time_per_division)
                self.ax.set_ylim(-3 * voltage_per_division, 3 * voltage_per_division)
                self.ax.grid(True)
                self.canvas.draw()
            except Exception as e:
                print(f"更新波形时报错: {e}")
        else:
            pass

    def run_stop(self):#示波器开始/停止
        if self.running and not self.simulate:
            self.run_stop_button.setDisabled(True)
            self.connect_event()
            self.run_stop_button.setText('Run')
            self.run_stop_button.setStyleSheet("QPushButton {font-size: 35px;background-color: red;}")
            self.timer.stop()
            self.running = False
            self.save_button.setEnabled(True)
            self.pts_selector.setDisabled(True)
            self.voltage_scale_selector.setDisabled(True)
            self.time_scale_selector.setDisabled(True)
            self.coupling_selector.setDisabled(True)
            self.toggle_button.setDisabled(True)
            self.channel_selector.setDisabled(True)
            self.open_channel_button.setDisabled(True)
            self.Auto_button.setDisabled(True)
            self.close_channel_button.setDisabled(True)
            self.oscilloscope.write(':STOP')
            sleep(0.1)
            self.run_stop_button.setEnabled(True)
            collect()
        elif not self.running and not self.simulate:
            collect()
            self.run_stop_button.setDisabled(True)
            self.run_stop_button.setText('Stop')
            self.run_stop_button.setStyleSheet("QPushButton {font-size: 35px;background-color: green;}")
            self.oscilloscope.write(':RUN')
            sleep(0.1)
            self.timer.start(self.update_time)
            self.running = True
            self.save_button.setDisabled(True)
            self.pts_selector.setEnabled(True)
            self.voltage_scale_selector.setEnabled(True)
            self.time_scale_selector.setEnabled(True)
            self.coupling_selector.setEnabled(True)
            self.toggle_button.setEnabled(True)
            self.channel_selector.setEnabled(True)
            self.open_channel_button.setEnabled(True)
            self.Auto_button.setEnabled(True)
            self.close_channel_button.setEnabled(True)
            self.run_stop_button.setEnabled(True)
        elif self.running and self.simulate:
            self.run_stop_button.setDisabled(True)
            self.run_stop_button.setText('Run')
            self.run_stop_button.setStyleSheet("QPushButton {font-size: 35px;background-color: red;}")
            self.timer.stop()
            self.running = False
            self.run_stop_button.setEnabled(True)
            collect()
        elif not self.running and self.simulate:
            collect()
            self.run_stop_button.setDisabled(True)
            self.run_stop_button.setText('Stop')
            self.run_stop_button.setStyleSheet("QPushButton {font-size: 35px;background-color: green;}")
            self.timer.start(self.update_time_simulate)
            self.running = True
            self.run_stop_button.setEnabled(True)
        else:
            pass

    def save(self):#保存波形数据(CSV文件)
        if not self.running:
            self.save_button.setDisabled(True)
            root = Tk()
            root.withdraw()
            x_data=self.ax.lines[0].get_xdata()
            y_data=self.ax.lines[0].get_ydata()
            y_data_formatted = [f'{y:.6f}' for y in y_data]
            x_data_formatted = [f'{x:.6f}' for x in x_data]
            data=DataFrame({'Time':x_data_formatted,'Voltage':y_data_formatted})
            file_path = filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],)
            if file_path:
                 data.to_csv(file_path, index=False)
                 self.save_button.setEnabled(True)
            else:
                QMessageBox.warning(self, '警告', '未选择文件路径。')
            
        else:
            pass

    def autoset(self):#示波器自动设置
        if self.running:
            self.Auto_button.setDisabled(True)
            self.timer.stop()
            self.oscilloscope.write(':AUToset')
            sleep(3)
            self.check_20M()
            self.query_coupling()
            self.query_current_scales()
            self.timer.start(self.update_time)
            self.Auto_button.setEnabled(True)
        else:
            pass

    def process_waveform_data(self, raw_data, chunk_size=1000000):#为FFT处理波形数据,由于要读取示波器内存中的波形,数据量很大,需要分块处理提高效率
        data_list = []
        raw_length = len(raw_data)
        for i in range(0, raw_length, chunk_size):
            chunk = raw_data[i:min(i + chunk_size, raw_length)]
            if chunk[-1] == ',':
                chunk = chunk[:-1]
            data_array = fromstring(chunk, sep=',', dtype=float64)
            data_array = data_array[isfinite(data_array)]
            data_list.append(data_array)
        return concatenate(data_list)
    
    def FFT_software(self):#软件FFT(scipy)
        if self.running:
            self.timer.stop()
            self.oscilloscope.write(':STOP')
            self.oscilloscope.write(':WAVeform:MODE RAW')
        else:
            self.oscilloscope.write(':WAVeform:MODE RAW')
        raw_data = self.oscilloscope.query(':WAVeform:DATA?')
        sleep(0.2)
        data2 = self.process_waveform_data(raw_data, chunk_size=800000)
        sleep(0.3)
        if self.running:
            self.oscilloscope.write(':WAVeform:MODE NORMal')
            self.oscilloscope.write(':RUN')
            self.timer.start(self.update_time)
        else:
            self.oscilloscope.write(':WAVeform:MODE NORMal')
        FFT_dialog = FFTDialog()
        if self.filter_lp:
            FFT_dialog.ax.set_title(f'幅度频谱图(经过Wc为{self.convert_frequency(self.filter_w1)}的低通滤波器)', fontsize=25)
            data3=FFT_dialog.lpfilter(self.filter_w1,self.sample_frequency,self.filter_order,data2)
        elif self.filter_hp:
            FFT_dialog.ax.set_title(f'幅度频谱图(经过Wc为{self.convert_frequency(self.filter_w1)}的高通滤波器)', fontsize=25)
            data3=FFT_dialog.hpfilter(self.filter_w1,self.sample_frequency,self.filter_order,data2)
        elif self.filter_bp:
            FFT_dialog.ax.set_title(f'幅度频谱图(经过W1为{self.convert_frequency(self.filter_w1)},W2为{self.convert_frequency(self.filter_w2)}的带通滤波器)', fontsize=25)
            data3=FFT_dialog.bpfilter(self.filter_w1,self.filter_w2,self.sample_frequency,self.filter_order,data2)
        elif self.filter_bs:
            FFT_dialog.ax.set_title(f'幅度频谱图(经过W1为{self.convert_frequency(self.filter_w1)},W2为{self.convert_frequency(self.filter_w2)}的带阻滤波器)', fontsize=25)
            data3=FFT_dialog.bsfilter(self.filter_w1,self.filter_w2,self.sample_frequency,self.filter_order,data2)
        elif not self.filter_bp and not self.filter_lp and not self.filter_hp and not self.filter_bs:
            FFT_dialog.ax.set_title('幅度频谱图', fontsize=25)
            data3=data2
        else:
            pass
        if type(data3)!=None:
            window = hann(len(data3))
            windowed_waveform = data3 * window
            fft_data=fft(windowed_waveform)
            frequency=fftfreq(len(windowed_waveform),d=1/self.sample_frequency)
            mag=abs(fft_data/len(windowed_waveform))
            p_mag=mag[:len(windowed_waveform)//2]
            p_frequency=frequency[:frequency.size//2]
            FFT_dialog.ax.plot(p_frequency/1e6,p_mag)
            FFT_dialog.ax.set_xlim(0,40)
            FFT_dialog.ax.tick_params(axis='both', which='major', labelsize=12)
            FFT_dialog.ax.tick_params(axis='both', which='minor', labelsize=5)
            FFT_dialog.ax.set_xlabel('频率(MHz)', fontsize=20)
            FFT_dialog.ax.set_ylabel('幅度', fontsize=20)
            FFT_dialog.ax.grid(True)
            FFT_dialog.canvas.draw()
            FFT_dialog.exec()
        else:
            QMessageBox.warning(self, '错误', '滤波器参数设置错误。')
        close(FFT_dialog.figure)
        FFT_dialog.close()
        del raw_data, data2, data3, FFT_dialog, window, windowed_waveform, fft_data, frequency, mag, p_mag, p_frequency
        collect()


#    def FFT_hardware(self):#示波器硬件FFT(耗费资源,暂时不用)
#       if self.running and not self.simulate:
#            if self.oscilloscope.query(':MATH1:DISPlay?') == False:
#                self.oscilloscope.write(':MATH1:DISPlay ON')
#                sleep(0.1)
#            self.oscilloscope.write(':MATH1:OPERator FFT')
#            self.oscilloscope.write(':MATH1:FFT:UNIT VRMS')

    def filter_software(self):#软件滤波
        dialog = filter_choose(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.radio_button1.isChecked():
                if len(dialog.w1_input.text())==0:
                    QMessageBox.warning(self, '错误', '请输入截止频率。')
                else:
                    self.filter_w1=float(dialog.w1_input.text())
                    self.filter_w2=0
                    self.filter_order=dialog.order_input.value()
                    self.filter_lp=True
                    self.filter_hp=False
                    self.filter_bp=False
                    self.filter_bs=False
                    self.filter_button.setText("低通滤波")
                    self.filter_button.setStyleSheet("QPushButton {background-color: green;font-size: 35px;}")
            elif dialog.radio_button2.isChecked():
                if len(dialog.w1_input.text())==0:
                    QMessageBox.warning(self, '错误', '请输入截止频率。')
                else:
                    self.filter_w1=float(dialog.w1_input.text())
                    self.filter_w2=0
                    self.filter_order=dialog.order_input.value()
                    self.filter_hp=True
                    self.filter_lp=False
                    self.filter_bp=False
                    self.filter_bs=False
                    self.filter_button.setText("高通滤波")
                    self.filter_button.setStyleSheet("QPushButton {background-color: green;font-size: 35px;}")
            elif dialog.radio_button3.isChecked():
                if len(dialog.w1_input.text())==0 or len(dialog.w2_input.text())==0:
                    QMessageBox.warning(self, '错误', '请输入截止频率。')
                else:
                    self.filter_w1=float(dialog.w1_input.text())
                    self.filter_w2=float(dialog.w2_input.text())
                    if self.filter_w1 > self.filter_w2:
                        QMessageBox.warning(self, '错误', '截止频率要在0 和 40MHz 之间,且w1必须大于w2。')
                        self.filter_w1=0
                        self.filter_w2=0
                    else:
                        self.filter_order=dialog.order_input.value()
                        self.filter_bp=True
                        self.filter_lp=False
                        self.filter_hp=False
                        self.filter_bs=False
                        self.filter_button.setText("带通滤波")
                        self.filter_button.setStyleSheet("QPushButton {background-color: green;font-size: 35px;}")
            elif dialog.radio_button4.isChecked():
                if len(dialog.w1_input.text())==0 or len(dialog.w2_input.text())==0:
                    QMessageBox.warning(self, '错误', '请输入截止频率。')
                else:
                    self.filter_w1=float(dialog.w1_input.text())
                    self.filter_w2=float(dialog.w2_input.text())
                    if self.filter_w1 > self.filter_w2:
                        QMessageBox.warning(self, '错误', '截止频率要在0 和 40MHz 之间,且w1必须大于w2。')
                        self.filter_w1=0
                        self.filter_w2=0
                    else:
                        self.filter_order=dialog.order_input.value()
                        self.filter_lp=False
                        self.filter_hp=False
                        self.filter_bp=False
                        self.filter_bs=True
                        self.filter_button.setText("带阻滤波")
                        self.filter_button.setStyleSheet("QPushButton {background-color: green;font-size: 35px;}")
            else:
                self.filter_lp=False
                self.filter_hp=False
                self.filter_bp=False
                self.filter_bs=False
                self.filter_button.setText("软件滤波")
                self.filter_button.setStyleSheet("QPushButton {background-color: red;font-size: 35px;}")
                
    def closeEvent(self,event):#退出
        if self.running and not self.simulate:
            self.oscilloscope.write(':RUN')
            event.accept()
        elif not self.running and not self.simulate:
            self.oscilloscope.write(':RUN')
            event.accept()
        elif self.running and self.simulate:
            event.accept()
        else:
            event.ignore()


    def voltage_scale_dict(self):#示波器电压刻度-电压值
        return {
            '200μv': 0.0002,
            '500μv': 0.0005,
            '1mv': 0.001,
            '2mv': 0.002,
            '5mv': 0.005,
            '10mv': 0.01,
            '20mv': 0.02,
            '50mv': 0.05,
            '100mv': 0.1,
            '200mv': 0.2,
            '500mv': 0.5,
            '1v': 1.0,
            '2v': 2.0,
            '5v': 5.0,
            '10v': 10.0
        }

    def time_scale_dict(self):#示波器时间刻度-时间值
        return {
            '2ns': 2e-9, '5ns': 5e-9, '10ns': 10e-9, '20ns': 20e-9, '50ns': 50e-9, '100ns': 100e-9, '200ns': 200e-9, '500ns': 500e-9,
            '1μs': 1e-6, '2μs': 2e-6, '5μs': 5e-6, '10μs': 10e-6, '20μs': 20e-6, '50μs': 50e-6, '100μs': 100e-6, '200μs': 200e-6, '500μs': 500e-6,
            '1ms': 1e-3, '2ms': 2e-3, '5ms': 5e-3, '10ms': 10e-3, '20ms': 20e-3, '50ms': 50e-3, '100ms': 100e-3, '200ms': 200e-3, '500ms': 500e-3,
            '1s': 1, '2s': 2, '5s': 5, '10s': 10, '20s': 20, '50s': 50, '100s': 100, '200s': 200, '500s': 500
        }

    def inverse_voltage_dict(self):#示波器电压值-电压刻度
        return {v: k for k, v in self.voltage_scale_dict().items()}

    def inverse_time_dict(self):#示波器时间值-时间刻度
        return {v: k for k, v in self.time_scale_dict().items()}




#主程序代码
app = QApplication(sys.argv)
window = OscilloscopeApp()
sys.exit(app.exec())
