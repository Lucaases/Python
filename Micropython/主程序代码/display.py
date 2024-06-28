import lvgl as lv
import time
from espidf import VSPI_HOST
from ili9XXX import ili9341
from ft6x36 import ft6x36
import machine

# 定义显示屏的宽度和高度
WIDTH = 240
HEIGHT = 320

def init_display():
    # 初始化ILI9341显示屏
    disp = ili9341(miso=19, mosi=23, clk=18, cs=5, dc=4, rst=2, power=14, backlight=-1, backlight_on=0, power_on=0, rot=0x80, spihost=VSPI_HOST, mhz=60, factor=16, hybrid=True, width=WIDTH, height=HEIGHT,
                   invert=False, double_buffer=True, half_duplex=False, initialize=True)
    return disp

def init_touch():
    # 初始化触摸IC的复位引脚
    rst = machine.Pin(32, machine.Pin.OUT)
    
    def reset_touch_ic():
        # 拉低复位引脚，延迟一段时间后再拉高
        rst.value(0)
        time.sleep(0.1)
        rst.value(1)
    
    reset_touch_ic()
    # 初始化触摸IC
    touch = ft6x36(sda=16, scl=17, width=WIDTH, height=HEIGHT, inv_x=True, inv_y=True)
    int_pin = machine.Pin(33, machine.Pin.IN, machine.Pin.PULL_UP)
    
    def touch_isr(pin):
        # 触摸中断服务函数，处理触摸数据
        touch_data = lv.indev_data_t()
        touch.callback(None, touch_data)
        print(f"Touch data: {touch_data.point.x}, {touch_data.point.y}, {touch_data.state}")

    # 设置中断触发和中断处理函数
    int_pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=touch_isr)
    return touch
