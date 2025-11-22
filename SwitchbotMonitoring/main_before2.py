import time
import hashlib
import hmac
import base64
import ujson
 
import urequests

import machine
import neopixel
import utime
from machine import Pin

import network_connection
network_connection.do_connect()

import neopixel
import machine
import time

from skScanSW import ScanSW

machine.Pin(17, machine.Pin.OUT)
np = neopixel.NeoPixel(machine.Pin(17), 4)

SW_PIN_1 = 19
SW_PIN_2 = 20

sw1 = Pin(SW_PIN_1, Pin.IN, Pin.PULL_UP)
sw2 = Pin(SW_PIN_2, Pin.IN, Pin.PULL_UP)

#sw1=ScanSW(Pin,SW_PIN_1)
#sw2=ScanSW(Pin,SW_PIN_2)

LED1=machine.Pin(39, machine.Pin.OUT)
LED2=machine.Pin(40, machine.Pin.OUT)

room1ID="F1A66FC67D14"
room2ID="FB2C6BB4C8C2"

# open token
token = 'a924fa8c7b9116973b2f3c846a511d506cece78e4b2c0693c5593272fa773692a0a1ec3851f1335b10c8a70f199b1289'
# secret key
secret = '8fb22b45c0ddd39c0b76d6d09a20a14b' 

host_domain = "https://api.switch-bot.com"
ver = "/v1.1"

last_callback_time=0

#Interval_MS = 200  # 100ミリ秒

def get_auth_header(token, secret):
    nonce = ''
    t = int(round((time.time() + 946684800) * 1000)) 
    string_to_sign = '{}{}{}'.format(token, t, nonce)
    string_to_sign = bytes(string_to_sign, 'utf-8')
    secret = bytes(secret, 'utf-8')

    sign = base64.b64encode(hmac.new(secret, msg=string_to_sign, 
    digestmod=hashlib.sha256).digest())
    """
    print ('Authorization: {}'.format(token))
    print ('t: {}'.format(t))
    print ('sign: {}'.format(str(sign, 'utf-8')))
    print ('nonce: {}'.format(nonce))
    """
    header={}
    header["Authorization"] = token
    header["sign"] = str(sign, 'utf-8')
    header["t"] = str(t)
    header["nonce"] = nonce
    return header

def get_device_list(header):
    response = urequests.get(host_domain + ver + "/devices", headers=header)
    return_json = response.json()
    if return_json["message"] == "success":
        print("取得成功")
        return return_json["body"]
    elif return_json["message"] == "Unauthorized":
        print("認証エラー")
        return None
    else:
        print("エラー")
        Ltika(2,1)
        utime.sleep_ms(10)
        Ltika(2,0)
        return None

header = get_auth_header(token, secret)
device_list = get_device_list(header)

def get_lock_status(deviceId: str):
    devices_url = host_domain + "/v1.1/devices/" + deviceId + "/status"
    try:
        response = urequests.get(devices_url, headers=header)
        if response.status_code == 200:
            data = response.json()
            response.close()
            return data["body"]["lockState"]
        else:
            print("Error: HTTP status code", response.status_code)
            response.close()
            return None
    except Exception as e:
        print("Response error:", e)
        return None

def demo():
    for i in range(6):
        np[i]=(128,0,0)
    np.write()
    time.sleep(2)
    for i in range(6,10):
        np[i]=(0,0,0)
    np.write()
    time.sleep(2)
    
def monitoring():
    Room1=get_lock_status(room1ID) #1号室
    Room2=get_lock_status(room2ID) #2号室
    if Room2=="unlocked":
        LED2.on()
        """
        np[3]=(0,128,0)
        np[2]=(0,0,0)
        np.write()
        """
        print("Room2 is Unlocked")
    else:
        LED2.off()
        """
        np[2]=(128,0,0)
        np[3]=(0,0,0)
        np.write()
        """
        print("Room2 is Locked")
    if Room1=="unlocked":
        LED1.on()
        """
        np[1]=(0,128,0)
        np[0]=(0,0,0)
        np.write()
        """
        print("Room1 is Unlocked")
    else:
        LED1.off()
        """
        np[0]=(128,0,0)
        np[1]=(0,0,0)
        np.write()
        """
        print("Room1 is Locked")

def Lock(deviceID):
    header = get_auth_header(token, secret)
    devices_url = host_domain + ver +"/devices/" + deviceID + "/commands"
    data={
            "commandType": "command",
            "command": "lock",
            "parameter": "default",
        }
    try:
        # ロック
        res = urequests.post(devices_url, headers=header, json=data)
        print(res.text)
    except Exception as e:
        print("error:",e)
        
def Unlock(deviceID):
    header = get_auth_header(token, secret)
    devices_url = host_domain + ver +"/devices/" + deviceID + "/commands"
    data={
            "commandType": "command",
            "command": "unlock",
            "parameter": "default",
        }
    try:
        # アンロック
        res = urequests.post(devices_url, headers=header, json=data)
        print(res.text)
    except Exception as e:
        print("error:",e)
        
def callback(pin):
    global last_callback_time
    current_time = time.ticks_ms()
    if current_time>last_callback_time+500:
        # --- ここから本処理 ---
        if pin is sw1:  
            room1 = get_lock_status(room1ID)
            if room1 == "locked":
                Unlock(room1ID)
                LED1.on()
            else:
                Lock(room1ID)
                LED1.off()

        elif pin is sw2:
            room2 = get_lock_status(room2ID)
            if room2 == "locked":
                Unlock(room2ID)
                LED2.on()
            else:
                Lock(room2ID)
                LED2.off()
        # --- ここまで本処理 ---
        # デバウンス時間を満たしたので更新
        last_callback_time = current_time
        
sw1.irq(trigger=Pin.IRQ_FALLING,handler=callback)
sw2.irq(trigger=Pin.IRQ_FALLING,handler=callback)

if __name__== "__main__":
    header = get_auth_header(token, secret)
    last_callback_time = time.ticks_ms()
    for i in range(4):
        np[i]=(0,0,128)
        np.write()
        time.sleep_ms(50)
        np[i]=(0,0,0)
        np.write()
    while True:
        monitoring()
        utime.sleep(20)