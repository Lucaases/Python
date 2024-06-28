import machine
import sht31
import sgp41
import ds3231

def init_sensor(choice):
    # 初始化I2C接口
    i2c = machine.SoftI2C(scl=machine.Pin(22), sda=machine.Pin(21),freq=400000)
    if choice == "ALL":
        # 初始化SHT31传感器
        sensor1 = sht31.SHT31(i2c, addr=0x44)
        # 初始化SGP41传感器
        sensor2 = sgp41.SGP41(i2c, addr=0x59)
        # 初始化DS1307实时时钟
        RTC = ds3231.DS3231(i2c, addr=0x68)
        return sensor1,sensor2,RTC
    if choice == "Sensor":
        # 初始化SHT31传感器
        sensor1 = sht31.SHT31(i2c, addr=0x44)
        # 初始化SGP41传感器
        sensor2 = sgp41.SGP41(i2c, addr=0x59)
        return sensor1,sensor2
    elif choice == "RTC":
        RTC = ds3231.DS3231(i2c, addr=0x68)
        return RTC
    else:
        return None 
    
