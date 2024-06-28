import lvgl as lv
from machine import Pin,reset
import modulators
import utime
import urandom
import gc
import gas_index_algorithm
from timesync import sync_ntp


click_interval = 2000 #点击间隔1s
last_click_time = 0

def create_gui(ad, sensor1,sensor2,RTC,timesync=None):
    global mode
    mode = True
    global shape
    shape=Pin(25,Pin.OUT)
    global voc_algorithm
    voc_algorithm = gas_index_algorithm.VocGasIndexAlgorithm()
    global nox_algorithm 
    nox_algorithm = gas_index_algorithm.NoxGasIndexAlgorithm()
    # 创建主屏幕对象
    scr = lv.obj()
    tabview = lv.tabview(scr, lv.DIR.TOP, 35)
    tab1 = tabview.add_tab("Signal Generator")
    tab2 = tabview.add_tab("Sensors")
    # 创建频率标签和编辑框
    freq_label = lv.label(tab1)
    freq_label.set_text("Frequency:")
    freq_label.align(lv.ALIGN.TOP_LEFT, 0, 0)
    freq_value = lv.textarea(tab1)
    freq_value.set_text("1000")
    freq_value.set_width(60)
    freq_value.set_height(35)
    freq_value.align_to(freq_label, lv.ALIGN.OUT_RIGHT_MID, 10, 0)
    freq_unit = lv.dropdown(tab1)
    freq_unit.set_options("\n".join(["Hz", "KHz","MHz"]))
    freq_unit.set_width(60)
    freq_unit.align_to(freq_value, lv.ALIGN.OUT_RIGHT_MID, 0, 0)

    # 创建屏幕键盘并初始隐藏
    kb = lv.keyboard(tab1)
    kb.set_textarea(freq_value)
    kb.align(lv.ALIGN.BOTTOM_MID, 0, 0)
    kb.set_mode(lv.keyboard.MODE.NUMBER)
    kb.add_flag(lv.obj.FLAG.HIDDEN)

    # 创建信号形状选择框
    shape_label = lv.label(tab1)
    shape_label.set_text("Signal Shape:")
    shape_label.align_to(freq_label, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 20)
    shape_dropdown = lv.dropdown(tab1)
    shape_dropdown.set_options("\n".join(["Sine", "Square"]))
    shape_dropdown.set_width(100)
    shape_dropdown.set_height(35)
    shape_dropdown.align_to(shape_label, lv.ALIGN.OUT_RIGHT_MID, 10, 0)

    # 显示当前频率和信号形状的标签
    current_freq_label = lv.label(tab1)
    current_freq_label.set_text("Current Frequency: 1 kHz")
    current_freq_label.align_to(shape_label, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)
    current_shape_label = lv.label(tab1)
    current_freq_label.set_width(150)
    current_shape_label.set_text("Current Shape: Sine")
    current_shape_label.align_to(current_freq_label, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)

    # 显示当前温度,湿度,VOC,NOX的标签
    temperature_label = lv.label(tab2)
    temperature_label.set_width(200)
    temperature_label.set_text("Temperature:N/A ")
    temperature_label.align(lv.ALIGN.TOP_LEFT, 0, 0)
    humidity_label = lv.label(tab2)
    humidity_label.set_width(200)
    humidity_label.set_text("Humidity:N/A ")
    humidity_label.align_to(temperature_label, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)
    voc_label = lv.label(tab2)
    voc_label.set_width(200)
    voc_label.set_text("VOC:N/A ")
    voc_label.align_to(humidity_label,lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)
    nox_label = lv.label(tab2)
    nox_label.set_width(200)
    nox_label.set_text("NOX:N/A ")
    nox_label.align_to(voc_label, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)
    RTC_temperature_label = lv.label(tab2)
    RTC_temperature_label.set_width(240)
    RTC_temperature_label.set_text("DS3231 RTC Chip's Temperature:N/A")
    RTC_temperature_label.align_to(nox_label,lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)

    # 显示当前日期时间的标签
    time_label = lv.label(tab2)
    time_label.set_width(200)
    time_label.set_text("Date:N/A  \nTime: N/A")
    time_label.align_to(RTC_temperature_label, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 0)
    
    # 调制
    modulation_label1 = lv.label(tab1)
    modulation_label1.set_text("Modulation:")
    modulation_label1.align(lv.ALIGN.TOP_LEFT,0, 0)
    modulation_dropdown = lv.dropdown(tab1)
    modulation_dropdown.set_options("\n".join(["close","Frequency(FM)", "Phase(PM)"]))
    modulation_dropdown.set_width(150)
    modulation_dropdown.set_height(35)
    modulation_dropdown.align_to(modulation_label1, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)
    modulation_label2=lv.label(tab1)
    modulation_label2.set_text("Carrier Freq:")
    modulation_label2.align_to(modulation_dropdown, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)
#     modulation_freq=lv.textarea(tab1)
#     modulation_freq.set_text("1000")
#     modulation_freq.set_width(60)
#     modulation_freq.set_height(35)
#     modulation_freq.align_to(modulation_label2, lv.ALIGN.OUT_RIGHT_MID, 10, 0)
    current_carrier_freq_labal=lv.label(tab1)
    current_carrier_freq_labal.set_text("Current Carrier Freq:N/A")
    current_carrier_freq_labal.align_to(modulation_label2, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)
    modulation_label1.add_flag(lv.obj.FLAG.HIDDEN)
    modulation_label2.add_flag(lv.obj.FLAG.HIDDEN)
#     modulation_freq.add_flag(lv.obj.FLAG.HIDDEN)
    modulation_dropdown.add_flag(lv.obj.FLAG.HIDDEN)
    current_carrier_freq_labal.add_flag(lv.obj.FLAG.HIDDEN)
    
#     kb1 = lv.keyboard(tab1)
#     kb1.set_textarea(modulation_freq)
#     kb1.align(lv.ALIGN.BOTTOM_MID, 0, 0)
#     kb1.set_mode(lv.keyboard.MODE.NUMBER)
#     kb1.add_flag(lv.obj.FLAG.HIDDEN)
     
    # 切换按钮
    toggle_btn = lv.btn(tab1)
    toggle_btn.set_size(140, 35)
    toggle_btn.align_to(current_shape_label, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)
    toggle_btn.add_flag(lv.obj.FLAG.CHECKABLE)
    toggle_btn.add_state(lv.STATE.CHECKED)
    label_btn0 = lv.label(toggle_btn)
    label_btn0.set_text("Modulation")

    # 关闭DDS
    shutdown_button = lv.btn(tab1)
    label_btn1=lv.label(shutdown_button)
    label_btn1.set_text("Shutdown DDS")
    shutdown_button.set_size(140, 35)
    shutdown_button.align_to(toggle_btn,lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)
    
    # 开启DDS
    turnon_button = lv.btn(tab1)
    label_btn2=lv.label(turnon_button)
    label_btn2.set_text("Turn on DDS")
    label_btn2.center()
    turnon_button.set_size(140, 35)
    turnon_button.center()
    turnon_button.add_flag(lv.obj.FLAG.HIDDEN)
    
    # 重启
    reset_button = lv.btn(tab1)
    label_btn5=lv.label(reset_button)
    label_btn5.set_text("Reset")
    reset_button.set_size(100, 35)
    reset_button.align_to(shutdown_button,lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)
    
    #时间同步
    timesync_button = lv.btn(tab2)
    label_btn3=lv.label(timesync_button)
    label_btn3.set_text("Time Sync")
    timesync_button.set_size(100, 35)
    timesync_button.align_to(time_label,lv.ALIGN.OUT_BOTTOM_LEFT, 0, 20)
    
    #SGP41校准
    calibration_button = lv.btn(tab2)
    label_btn4=lv.label(calibration_button)
    label_btn4.set_text("SGP41 Calibration")
    calibration_button.set_size(160, 35)
    calibration_button.align_to(timesync_button,lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)
    
    # 事件处理函数：更新频率标签
#     def freq_event_handler(event):
#         ta = event.get_target()
#         freq = ta.get_text()
#         unit = freq_unit.get_selected()
#         option = " "*10
#         freq_unit.get_selected_str(option, len(option))
#         if unit==0:
#             freq_value_num = int(freq)
#         elif unit==1:
#             freq_value_num = int(freq)*1000
#         elif unit==2:
#             freq_value_num = int(freq)*1000000
#         else:
#             pass
#         current_freq_label.set_text(f"Current Frequency: {freq_value_num} {option.strip()}")

    # 事件处理函数：更新信号形状标签
    def shape_event_handler(event):
        dd = event.get_target()
        shape = " " * 10
        dd.get_selected_str(shape, len(shape))
        current_shape_label.set_text(f"Current Shape: {shape}")

    # 定时器回调函数：更新温湿度标签
    def update_sht31(timer):
        temp, humi = sensor1.get_temp_humi()
        temperature_label.set_text(f"Temperature: {temp:.4f}°C")
        humidity_label.set_text(f"Humidity: {humi:.4f}%")

    # 定时器回调函数：更新日期和时间标签
    def update_datetime(timer):
        RTC._OSF_reset()
        datetime=RTC.datetime()
        year, month, day, weekday, hours, minutes, seconds, subseconds = datetime
        week = {7: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
        time_label.set_text(f"Date: {year:04}/{month:02}/{day:02} \nWeekday: {week[weekday]} \nTime: {hours:02}:{minutes:02}:{seconds:02}")
        
    # 定时器回调函数：更新DS3231内部温度标签
    def update_rtc_temp(timer):
        inner_temp=RTC.read_inner_temperature()
        RTC_temperature_label.set_text(f"DS3231 RTC Chip's Temp:{inner_temp}°C")

    # 定时器回调函数：更新voc,nox指数标签
    def update_voc_nox(timer):       
        temp, humi = sensor1.get_temp_humi()
        voc,nox = sensor2.measure_raw_humidity_env(humi,temp)
        voc_index=voc_algorithm.process(voc)
        nox_index=nox_algorithm.process(nox)
        voc_label.set_text(f"VOC Index: {voc_index:.2f}")
        nox_label.set_text(f"NOx Index: {nox_index:.2f}")
        
    # 校准SGP41气体传感器
    def calibration_event_handler(event):
        voc_algorithm = gas_index_algorithm.VocGasIndexAlgorithm()
        nox_algorithm = gas_index_algorithm.NoxGasIndexAlgorithm()
        
    # 事件处理函数：显示键盘
    def show_keyboard_event_handler(event):
        kb.set_textarea(freq_value)
        kb.clear_flag(lv.obj.FLAG.HIDDEN)
        kb.move_foreground()

    # 事件处理函数：隐藏键盘
    def hide_keyboard_event_handler(event):
        kb.add_flag(lv.obj.FLAG.HIDDEN)

    # 键盘输入处理函数
    def kb_event_handler(event):
        kb = event.get_target()
        if event.get_code() == lv.EVENT.READY:
            if mode==True:
                freq=float(freq_value.get_text())
                index=shape_dropdown.get_selected()
                unit=freq_unit.get_selected()
                try:
                    if unit==0:
                        freq_value_num = float(freq)
                    elif unit==1:
                        freq_value_num = float(freq)*1e3
                    elif unit==2:
                        freq_value_num = float(freq)*1e6
                    else:
                        pass
                    if index==0 and (freq_value_num < 20 or freq_value_num > 4e7):
                        raise ValueError
                    elif index==1 and (freq_value_num < 20 or freq_value_num > 1e6):
                        raise ValueError
                    if freq_value_num<1e3:
                        current_freq_label.set_text(f"Current Frequency:{freq_value_num}Hz")
                    elif freq_value_num<1e6 and freq_value_num>=1e3:
                        current_freq_label.set_text(f"Current Frequency:{freq_value_num/1e3}KHz")
                    elif freq_value_num<4e7 and freq_value_num>=1e6:
                        current_freq_label.set_text(f"Current Frequency:{freq_value_num/1e6}MHz")
                    else:
                        pass
                    kb.add_flag(lv.obj.FLAG.HIDDEN)
                    if index==0:
                        shape.value(0)
                    elif index==1:
                        shape.value(1)
                    else:
                        pass
                    ad.set_frequency(freq_value_num)
                    ad.enable_output(True)
                except ValueError:
                    if index==0:
                        show_error_window("Invalid frequency. Please enter a correct number!(For Sine,Maximum:40MHz,Minimum:20Hz.")
                    elif index==1:
                        show_error_window("Invalid frequency. Please enter a correct number!(For Square,Maximum:1MHz,Minimum:20Hz.")
            else:
                freq=float(freq_value.get_text())
                index=modulation_dropdown.get_selected()
                unit=freq_unit.get_selected()
                try:
                    if unit==0:
                        freq_value_num = float(freq)
                    elif unit==1:
                        freq_value_num = float(freq)*1e3
                    elif unit==2:
                        freq_value_num = float(freq)*1e6
                    else:
                        pass
                    if freq_value_num < 20 or freq_value_num > 3e7:
                        raise ValueError
                    if freq_value_num<1e3:
                        current_carrier_freq_labal.set_text(f"Current Frequency:{freq_value_num}Hz")
                    elif freq_value_num<1e6 and freq_value_num>=1e3:
                        current_carrier_freq_labal.set_text(f"Current Frequency:{freq_value_num/1e3}KHz")
                    elif freq_value_num<4e7 and freq_value_num>=1e6:
                        current_carrier_freq_labal.set_text(f"Current Frequency:{freq_value_num/1e6}MHz")
                    else:
                        pass
                    kb.add_flag(lv.obj.FLAG.HIDDEN)
                    modulation(index,freq_value_num)
                except ValueError:
                    show_error_window("Invalid frequency. Please enter a correct number!(Maximum:30MHz,Minimum:20Hz.")

                    
                    
#     def kb1_event_handler(event):
#         kb1 = event.get_target()
# 

    # 显示错误弹窗
    def show_error_window(message):
        mbox = lv.msgbox(lv.scr_act(), "Error", message, ["OK"], True)
        mbox.add_event_cb(lambda e: mbox.delete(), lv.EVENT.VALUE_CHANGED, None)
        mbox.set_width(200)
        mbox.center()
        
    # 弹窗
    def show_window(message):
        mbox = lv.msgbox(lv.scr_act(), "Message", message, ["OK"], True)
        mbox.add_event_cb(lambda e: mbox.delete(), lv.EVENT.VALUE_CHANGED, None)
        mbox.set_width(200)
        mbox.center()
        
    # 调制选择函数
    def modulation(index,freq_value_num):    
        if index==1:
            ad.reset()
            fm=modulators.FM(ad,freq = freq_value_num)
            fm.send_sequence(analog_sequence_gen())
        elif index==2:
            ad.reset()
            pm=modulators.PM(ad,freq = freq_value_num)
            pm.send_sequence(analog_sequence_gen())
        else:
            pass
    
    def modulation_event_handler(event):
        mo=event.get_target()
        if mo.get_selected()==0:
            freq_unit.add_flag(lv.obj.FLAG.HIDDEN)
            freq_value.add_flag(lv.obj.FLAG.HIDDEN)
            modulation_label2.add_flag(lv.obj.FLAG.HIDDEN)
            current_carrier_freq_labal.add_flag(lv.obj.FLAG.HIDDEN)
        else:
            freq_unit.clear_flag(lv.obj.FLAG.HIDDEN)
            freq_value.clear_flag(lv.obj.FLAG.HIDDEN)
            modulation_label2.clear_flag(lv.obj.FLAG.HIDDEN)
            current_carrier_freq_labal.clear_flag(lv.obj.FLAG.HIDDEN)
            
        
    def analog_sequence_gen():
        samples_size = 200
        duration = 0.5
        symbols = [round(urandom.uniform(-1, 1), 5) for _ in range(samples_size)]
        analog_sequence = [(symbol, duration) for symbol in symbols]
        del symbols
        gc.collect()
        return analog_sequence
        

    # 切换按钮函数
    def toggle_event_handler(event):
        dd = event.get_target()
        if event.get_code()==lv.EVENT.CLICKED:
            if dd.has_state(lv.STATE.CHECKED):
                mode = True
                label_btn0.set_text("Modulation")
                freq_value.clear_flag(lv.obj.FLAG.HIDDEN)
                freq_unit.clear_flag(lv.obj.FLAG.HIDDEN)
                modulation_label1.add_flag(lv.obj.FLAG.HIDDEN)
                modulation_label2.add_flag(lv.obj.FLAG.HIDDEN)
                modulation_dropdown.add_flag(lv.obj.FLAG.HIDDEN)
#                 modulation_freq.add_flag(lv.obj.FLAG.HIDDEN)
                current_carrier_freq_labal.add_flag(lv.obj.FLAG.HIDDEN)
                freq_label.clear_flag(lv.obj.FLAG.HIDDEN)
                shape_label.clear_flag(lv.obj.FLAG.HIDDEN)
                shape_dropdown.clear_flag(lv.obj.FLAG.HIDDEN)
                current_freq_label.clear_flag(lv.obj.FLAG.HIDDEN)
                current_shape_label.clear_flag(lv.obj.FLAG.HIDDEN)
                freq_value.align_to(freq_label, lv.ALIGN.OUT_RIGHT_MID, 10, 0)
                freq_unit.align_to(freq_value, lv.ALIGN.OUT_RIGHT_MID, 0, 0)
                toggle_btn.align_to(current_shape_label, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)
                ad.reset()
                ad.set_frequency(1000)
                ad.enable_output(True)                  
            else:
                mode = False
                label_btn0.set_text("Signal Gen")
                freq_label.add_flag(lv.obj.FLAG.HIDDEN)
                shape_label.add_flag(lv.obj.FLAG.HIDDEN)
                shape_dropdown.add_flag(lv.obj.FLAG.HIDDEN)
                current_freq_label.add_flag(lv.obj.FLAG.HIDDEN)
                current_shape_label.add_flag(lv.obj.FLAG.HIDDEN)
                freq_value.add_flag(lv.obj.FLAG.HIDDEN)
                freq_unit.add_flag(lv.obj.FLAG.HIDDEN)
                freq_value.align_to(modulation_label2, lv.ALIGN.OUT_RIGHT_MID, 10, 0)
                freq_unit.align_to(freq_value, lv.ALIGN.OUT_RIGHT_MID, 0, 0)
                toggle_btn.align_to(current_carrier_freq_labal, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)
                modulation_label1.clear_flag(lv.obj.FLAG.HIDDEN)
                modulation_dropdown.clear_flag(lv.obj.FLAG.HIDDEN)
#                 modulation_freq.clear_flag(lv.obj.FLAG.HIDDEN)
                current_carrier_freq_labal.add_flag(lv.obj.FLAG.HIDDEN)
                ad.reset()
                ad.enable_output(False)
            utime.sleep_ms(200)
    
    # 关闭DDS处理函数 
    def shutdown_event_handler(event):
        ad._power_down()
        shutdown_button.add_flag(lv.obj.FLAG.HIDDEN)
        turnon_button.clear_flag(lv.obj.FLAG.HIDDEN)
        toggle_btn.add_flag(lv.obj.FLAG.HIDDEN)
        if toggle_btn.has_state(lv.STATE.CHECKED):
            freq_label.add_flag(lv.obj.FLAG.HIDDEN)
            freq_value.add_flag(lv.obj.FLAG.HIDDEN)
            shape_label.add_flag(lv.obj.FLAG.HIDDEN)
            shape_dropdown.add_flag(lv.obj.FLAG.HIDDEN)
            current_freq_label.add_flag(lv.obj.FLAG.HIDDEN)
            current_shape_label.add_flag(lv.obj.FLAG.HIDDEN)
            freq_unit.add_flag(lv.obj.FLAG.HIDDEN)
        else:
            modulation_label1.add_flag(lv.obj.FLAG.HIDDEN)
            modulation_label2.add_flag(lv.obj.FLAG.HIDDEN)
            modulation_dropdown.add_flag(lv.obj.FLAG.HIDDEN)
            freq_value.add_flag(lv.obj.FLAG.HIDDEN)
            freq_unit.add_flag(lv.obj.FLAG.HIDDEN)
            current_carrier_freq_labal.add_flag(lv.obj.FLAG.HIDDEN)
        
        
    # 开启DDS处理函数
    def turnon_event_handler(event):
        index=shape_dropdown.get_selected()
        ad.reset()
        if index==0:
            shape.value(0)
        elif index==1:
            shape.value(1)
        else:
            pass
        ad.set_frequency(1000)
        ad.enable_output(True)
        shutdown_button.clear_flag(lv.obj.FLAG.HIDDEN)
        turnon_button.add_flag(lv.obj.FLAG.HIDDEN)
        toggle_btn.clear_flag(lv.obj.FLAG.HIDDEN)
        if toggle_btn.has_state(lv.STATE.CHECKED):
            freq_label.clear_flag(lv.obj.FLAG.HIDDEN)
            shape_label.clear_flag(lv.obj.FLAG.HIDDEN)
            freq_value.align_to(freq_label, lv.ALIGN.OUT_RIGHT_MID, 10, 0)
            freq_unit.align_to(freq_value, lv.ALIGN.OUT_RIGHT_MID, 0, 0)
            shape_dropdown.clear_flag(lv.obj.FLAG.HIDDEN)
            current_freq_label.clear_flag(lv.obj.FLAG.HIDDEN)
            current_shape_label.clear_flag(lv.obj.FLAG.HIDDEN)
            freq_unit.clear_flag(lv.obj.FLAG.HIDDEN)
        else:
            modulation_label1.clear_flag(lv.obj.FLAG.HIDDEN)
            modulation_label2.clear_flag(lv.obj.FLAG.HIDDEN)
            freq_value.align_to(modulation_label2, lv.ALIGN.OUT_RIGHT_MID, 10, 0)
            freq_unit.align_to(freq_value, lv.ALIGN.OUT_RIGHT_MID, 0, 0)
            freq_value.clear_flag(lv.obj.FLAG.HIDDEN)
            modulation_dropdown.clear_flag(lv.obj.FLAG.HIDDEN)
            freq_unit.clear_flag(lv.obj.FLAG.HIDDEN)
            current_carrier_freq_labal.clear_flag(lv.obj.FLAG.HIDDEN)
        
     
    # 重启函数
    def reset_event_handler(event):
        ad._power_down()
        reset()
    
    # 时间同步函数
    def timesync_event_handler(event):
        time=sync_ntp()
        if time == 1:
            show_window("Successfully sync time!")
        elif time == 2:
            show_error_window("Failed to sync time.")
        elif time == 3:
            show_error_window("Failed to connect to wifi!Can not sync time!")
        else:
            show_error_window("Specific Wifi not found!Can not sync time!")
        
    
    # 绑定事件处理函数
    shape_dropdown.add_event_cb(shape_event_handler, lv.EVENT.VALUE_CHANGED, None)
    freq_value.add_event_cb(show_keyboard_event_handler, lv.EVENT.CLICKED, None)
#     modulation_freq.add_event_cb(show_keyboard_event_handler, lv.EVENT.CLICKED, None)
    tab1.add_event_cb(hide_keyboard_event_handler, lv.EVENT.CLICKED, None)
    modulation_dropdown.add_event_cb(modulation_event_handler, lv.EVENT.VALUE_CHANGED, None)
    kb.add_event_cb(kb_event_handler, lv.EVENT.READY, None)
#     kb1.add_event_cb(kb1_event_handler, lv.EVENT.READY, None)
    shutdown_button.add_event_cb(shutdown_event_handler, lv.EVENT.CLICKED, None)
    turnon_button.add_event_cb(turnon_event_handler, lv.EVENT.CLICKED, None)
    timesync_button.add_event_cb(timesync_event_handler, lv.EVENT.CLICKED, None)
    calibration_button.add_event_cb(calibration_event_handler, lv.EVENT.CLICKED, None)
    reset_button.add_event_cb(reset_event_handler, lv.EVENT.CLICKED, None)
    toggle_btn.add_event_cb(toggle_event_handler, lv.EVENT.CLICKED, None)
    #显示屏幕
    lv.scr_load(scr)
    if timesync == 1:
        show_window("Successfully sync time!")
    elif timesync == 2:
        show_error_window("Failed to sync time.")
    elif timesync == 3:
        show_error_window("Failed to connect to wifi!Can not sync time!")
    elif timesync == 4:
        show_error_window("Specific Wifi not found!Can not sync time!")
    else:
        pass
    
    # 创建定时器更新温湿度和日期时间
    lv.timer_create(update_sht31, 2000, None)
    lv.timer_create(update_voc_nox, 3000, None)
    lv.timer_create(update_datetime, 1000, None)
    lv.timer_create(update_rtc_temp, 15246, None)
    
