import network
import ntptime
import utime
import ds3231
import sensor
ssid = 'Max'
password = '3kxx8urps5ewtmy'
def find_wifi(wlan):
    scan_results = wlan.scan()
    for wifi_info in scan_results:
        ssid1 = wifi_info[0].decode()  # 将字节字符串解码为普通字符串
        if ssid1 == ssid:
            return True
            break
    return False

def sync_ntp():
    ds=sensor.init_sensor("RTC")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected() == True:
        wlan.disconnect()
    if find_wifi(wlan)==True:
        wlan.connect(ssid, password)
        timeout = 5
        start_time = utime.time()
        while not wlan.isconnected():
            if utime.time() - start_time > timeout:
                print("Failed to connect to WiFi within timeout.")
                return 3
            utime.sleep(1)
        
        if wlan.isconnected()==True:
            print(wlan.ifconfig())
            ntptime.NTP_DELTA = 3155644800#时区转换(UTC->UTC+8)
            ntptime.host = 'ntp1.aliyun.com'
            count=0
            for attempt in range(5):  # 尝试最多5次
                try:
                    ntptime.settime()
                    print("NTP time synced on attempt", attempt + 1)
                    current_time = utime.localtime()
                    local_time = (current_time[0], current_time[1], current_time[2],
                                  current_time[3], current_time[4], current_time[5],
                                  current_time[6])
                    print("Local time:", local_time)
                    ds.datetime(local_time)
                    print("DS1307 time set to:", ds.datetime())
                    wlan.active(False)
                    return 1
                    break
                except OSError as e:
                    count+=1
                    print(f'Failed to sync time on attempt {attempt + 1}:', e)
                    utime.sleep(1)
            if count==5:
                print("Failed to sync time after 5 attempts.")
                wlan.active(False)
                return 2
        else:
            print("Failed to connect to wifi!Can not sync time!")
            return 3
    else:
        print("Specific Wifi not found!Can not sync time!")
        return 4
