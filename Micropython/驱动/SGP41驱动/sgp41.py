import machine
import utime
import struct

class SGP41:
    MEASUREMENT_RAW_humidity_default = b'\x26\x19\x80\x00\xA2\x66\x66\x93'
    MEASUREMENT_RAW_humidity_env = 0x2619
    HEATER_OFF = 0x3615
    SELF_TEST = 0x280E
    CRC_POLYNOMIAL = 0x31
    CRC_INIT = 0xFF

    def __init__(self, i2c, addr=0x59):
        self.i2c = i2c
        self.addr = addr
        if addr not in i2c.scan():
            raise Exception("SGP41 not found at address 0x{:02x}".format(addr))

    def send_command(self, command):
        self.i2c.writeto(self.addr,struct.pack('>H',command))
        
    def read_data(self, length):
        data = self.i2c.readfrom(self.addr, length)
        return data

    def measure_raw_humidity_default(self):
         self.i2c.writeto(self.addr, self.MEASUREMENT_RAW_humidity_default)
         utime.sleep_ms(50)  # 根据数据手册调整等待时间
         data = self.read_data(6)  # 6个字节的数据 (2x2 bytes + 2 CRC bytes)
         if self.check_crc(data[:3]) and self.check_crc(data[3:]):
            etoh_raw = struct.unpack('>H', data[:2])[0]
            nox_raw = struct.unpack('>H', data[3:5])[0]
            return etoh_raw, nox_raw
         else:
            print("CRC check failed for measurement data")
            return None
    
    def measure_raw_humidity_env(self, humidity=50, temperature=25):
        hum = int(humidity * 65535 / 100)
        temp = int((temperature + 45) * 65535 / 175)
        hum_bytes = struct.pack(">H", hum)
        temp_bytes = struct.pack(">H", temp)
        hum_crc = self.calculate_crc(hum_bytes)
        temp_crc = self.calculate_crc(temp_bytes)
        command = struct.pack(">HBBBBBB", self.MEASUREMENT_RAW_humidity_env,hum_bytes[0],hum_bytes[1],hum_crc,temp_bytes[0],temp_bytes[1],temp_crc)
        self.i2c.writeto(self.addr, command)
        utime.sleep_ms(50)  # 根据数据手册调整等待时间
        data = self.read_data(6) 
        if self.check_crc(data[:3]) and self.check_crc(data[3:]):#2 bytes + 1 CRC
            voc_raw = struct.unpack('>H', data[:2])[0]
            nox_raw = struct.unpack('>H', data[3:5])[0]
            return voc_raw, nox_raw
        else:
            print("CRC check failed for measurement data")
            return None
        
    
    def heater_off(self):
        self.send_command(self.HEATER_OFF)
    
    def calculate_crc(self, data):
        crc = self.CRC_INIT
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ self.CRC_POLYNOMIAL
                else:
                    crc <<= 1
            crc &= 0xFF
        return crc

    def check_crc(self, data):
        calculated_crc = self.calculate_crc(data[:2])
        #print("Expected CRC:", calculated_crc)
        #print("Received CRC:", data[2])
        return calculated_crc == data[2]

    def measure_test(self):
        self.send_command(self.SELF_TEST)
        utime.sleep_ms(350)
        data = self.read_data(3)
        if self.check_crc(data) and data[1]==0:
            # 输出每个字节的数据
            print("Byte 1:", data[0])
            print("Byte 2:", data[1])
            print("Byte 3 (CRC):", data[2])
            print("Sensor self test passes without errors!")
        else:
            print("CRC check failed")




