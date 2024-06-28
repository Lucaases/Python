import math
import sht31
import machine
import sgp41
from sensor import init_sensor

sensor_h_t,sensor_g=init_sensor("Sensor")

def mean_std_deviation(data):
    n = len(data)
    if n < 2:
        return None, None 
    mean_value = sum(data) / n
    std_dev = math.sqrt(sum((x - mean_value) ** 2 for x in data) / (n - 1))
    return mean_value,std_dev

def voc_raw_nox_raw(algorithm_type):
    voc=[]
    nox=[]
    for _ in range(30):
        temp, humi = sensor_h_t.get_temp_humi()
        if algorithm_type == 'VOC':
            voc_raw = sensor_g.measure_raw_humidity_env(humi,temp)[0]
            voc.append(voc_raw)
        else:
            nox_raw = sensor_g.measure_raw_humidity_env(humi,temp)[1]
            nox.append(nox_raw)
    if algorithm_type == 'VOC':
        
        voc_mean,voc_std=mean_std_deviation(voc)
        return voc_mean,voc_std
    else:
        nox_mean=mean_std_deviation(nox)[0]
        return nox_mean
    
class GasIndexAlgorithm:
    INDEX_GAIN = 230.0
    SRAW_STD_BONUS_VOC = 220.0
    SRAW_STD_NOX = 2000.0

    def __init__(self, algorithm_type):
        print("Waiting for SGP41 gas sensor's initialization!Please be patient!")
        self.algorithm_type = algorithm_type
        self.mox_model_sraw_mean_voc = int(voc_raw_nox_raw('VOC')[0])
        self.mox_model_sraw_std_voc = int(voc_raw_nox_raw('VOC')[1])
        self.mox_model_sraw_mean_nox = int(voc_raw_nox_raw('NOX'))
#       self.mox_model_sraw_mean_voc = 30290
#       self.mox_model_sraw_std_voc = 65
#       self.mox_model_sraw_mean_nox = 17500

    def process(self, sraw):
        if self.algorithm_type == 'VOC':
            gas_index = self.calculate_voc_index(sraw)
        else:
            gas_index = self.calculate_nox_index(sraw)
        return max(gas_index,0)
    
    def calculate_voc_index(self, sraw):
        return (self.INDEX_GAIN * (sraw - self.mox_model_sraw_mean_voc) /
                (self.mox_model_sraw_std_voc + self.SRAW_STD_BONUS_VOC))

    def calculate_nox_index(self, sraw):
        return (self.INDEX_GAIN * (sraw - self.mox_model_sraw_mean_nox) / self.SRAW_STD_NOX)
    

class VocGasIndexAlgorithm(GasIndexAlgorithm):
    def __init__(self):
        super().__init__('VOC')

class NoxGasIndexAlgorithm(GasIndexAlgorithm):
    def __init__(self):
        super().__init__('NOX')


