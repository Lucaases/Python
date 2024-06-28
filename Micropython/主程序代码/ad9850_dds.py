import peripherals
from shift_register import ShiftRegister
import ad9850

def init_ad9850():
    # 初始化AD9850所需的GPIO引脚
    _ss = peripherals.Pin.get_uPy_pin(26, output=True)
    _clk = peripherals.Pin.get_uPy_pin(14, output=True)
    _data = peripherals.Pin.get_uPy_pin(13, output=True)
    # 使用移位寄存器创建SPI总线
    _spi = ShiftRegister(stb_pin=_ss, clk_pin=_clk, data_pin=_data, lsbfirst=True, polarity=1)
    bus = peripherals.SPI(_spi, _ss)
    _reset = peripherals.Pin.get_uPy_pin(27, output=True)
    # 初始化AD9850
    ad = ad9850.AD9850(bus=bus, pin_reset=_reset)
    # 设置初始频率为1kHz
    ad.reset()
    ad.set_frequency(1000)
    ad.enable_output(True)
    return ad


    