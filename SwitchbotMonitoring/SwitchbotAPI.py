import time
import hashlib
import hmac
import base64
import ujson

import urequests

import machine
import utime


import network_connection

network_connection.do_connect()

# open token
token = "-"  # copy and paste from the SwitchBot app V6.14 or later
# secret key
secret = "-"  # copy and paste from the SwitchBot app V6.14 or later


def get_auth_header(token, secret):
    nonce = ""  # 空欄のままで良いらしい
    t = int(
        round((time.time() + 946684800) * 1000)
    )  # 後述 基準の時刻がホストPCとESP32で異なるため30年分の秒数を足す
    string_to_sign = "{}{}{}".format(token, t, nonce)

    string_to_sign = bytes(string_to_sign, "utf-8")
    secret = bytes(secret, "utf-8")

    sign = base64.b64encode(
        hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).digest()
    )
    """
    print ('Authorization: {}'.format(token))
    print ('t: {}'.format(t))
    print ('sign: {}'.format(str(sign, 'utf-8')))
    print ('nonce: {}'.format(nonce))
    """
    header = {}
    header["Authorization"] = token
    header["sign"] = str(sign, "utf-8")
    header["t"] = str(t)
    header["nonce"] = nonce
    return header


host_domain = "https://api.switch-bot.com"
ver = "/v1.1"


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
        return None


header = get_auth_header(token, secret)
device_list = get_device_list(header)
# print(device_list)


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


def Ltika(room, state):
    led = machine.Pin(room, machine.Pin.OUT)
    if state == 0:
        led.value(0)
    else:
        led.value(1)


def monitoring():
    Room1 = get_lock_status("-")  # 1号室
    Room2 = get_lock_status("-")  # 2号室
    Room6 = get_lock_status("-")  # 6号室
    if Room1 == "unlocked":
        Ltika(40, 1)
        print("Room1 is Unlocked")
    else:
        Ltika(40, 0)
        print("Room1 is Locked")


if __name__ == "__main__":
    header = get_auth_header(token, secret)
    # device_list = get_device_list(header)
    while True:
        monitoring()
        utime.sleep_ms(10)
