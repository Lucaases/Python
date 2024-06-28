import lvgl as lv
import utime
import sensor
import ad9850_dds
import display
import gui
# from timesync import sync_ntp

# 初始化LVGL库
lv.init()
# 初始化传感器、DDS和显示模块
sensor1,sensor2,RTC = sensor.init_sensor("ALL")
ad = ad9850_dds.init_ad9850()
disp = display.init_display()
touch = display.init_touch()
#同步时间
#time=sync_ntp()
# 创建GUI界面
gui.create_gui(ad, sensor1,sensor2,RTC)
#gui.create_gui(ad, sensor1,sensor2,RTC,time)
# 主循环处理LVGL任务
while True:
    lv.task_handler()
    utime.sleep_ms(5)
 
 