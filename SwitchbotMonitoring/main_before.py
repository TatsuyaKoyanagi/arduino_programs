import network
import ntptime
import time
import urequests
import ujson
import uhashlib
import ubinascii
from machine import Pin
import urandom

# --- Configuration ---
SSID = 'SagaUdeLab'           # Wi-FiのSSIDを入力
PASSWORD = 'CPE33zV4Zv'   # Wi-Fiのパスワードを入力

LED_PIN = 2                  # LEDを接続したGPIOピン番号（例：GPIO2）
BLINK_INTERVAL = 0.5         # 点滅の間隔（秒）
CHECK_INTERVAL = 60          # ロック状態をチェックする間隔（秒）

# SwitchBot APIの設定
BASE_URL = "https://api.switch-bot.com"
TOKEN = "a924fa8c7b9116973b2f3c846a511d506cece78e4b2c0693c5593272fa773692a0a1ec3851f1335b10c8a70f199b1289"
SECRET = "8fb22b45c0ddd39c0b76d6d09a20a14b"

DEVICE_ID = "CF3C03B1250E"  # 実際のデバイスIDに置き換えてください

# --- LEDの初期化 ---
led = Pin(LED_PIN, Pin.OUT)
led.value(0)  # 初期状態はLEDオフ

# --- Wi-Fi接続関数 ---
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            print('.', end='')
            time.sleep(1)
    print('\nNetwork connected:', wlan.ifconfig())

# --- 時刻設定関数 ---
def set_time():
    try:
        print("Synchronizing time with NTP...")
        ntptime.settime()
        t = time.localtime()
        print("Time set to:", t)
    except Exception as e:
        print("Failed to set time:", e)

# --- nonce生成関数 ---
def generate_nonce(length=16):
    """ランダムな nonce を生成します。デフォルトでは16バイト（32文字の16進数）です。"""
    return ''.join(['{:02x}'.format(urandom.getrandbits(8)) for _ in range(length)])

# --- HMAC-SHA256実装 ---
def hmac_sha256(key, message):
    block_size = 64  # SHA256のブロックサイズ

    if len(key) > block_size:
        key = uhashlib.sha256(key).digest()
    if len(key) < block_size:
        key = key + b'\x00' * (block_size - len(key))

    o_key_pad = bytes([b ^ 0x5c for b in key])
    i_key_pad = bytes([b ^ 0x36 for b in key])

    inner_hash = uhashlib.sha256(i_key_pad + message).digest()
    hmac_result = uhashlib.sha256(o_key_pad + inner_hash).digest()

    return hmac_result

# --- サイン生成関数 ---
def make_sign(token: str, secret: str):
    nonce = generate_nonce()
    t = int(time.time() * 1000)  # 現在のタイムスタンプ（ミリ秒）
    string_to_sign = f"{token}{t}{nonce}".encode('utf-8')
    secret_bytes = secret.encode('utf-8')

    # HMAC SHA256サインを手動で作成
    hmac_digest = hmac_sha256(secret_bytes, string_to_sign)
    signature = ubinascii.b2a_base64(hmac_digest).rstrip(b'\n').decode('utf-8')

    # デバッグ情報
    print(f"Timestamp (t): {t}")
    print(f"Nonce: {nonce}")
    print(f"Signature: {signature}")

    return signature, str(t), nonce

# --- リクエストヘッダー作成関数 ---
def make_request_header(token: str, secret: str) -> dict:
    sign, t, nonce = make_sign(token, secret)
    headers = {
        "Authorization": token,
        "sign": sign,
        "t": t,
        "nonce": nonce
    }
    return headers

# --- デバイスリスト取得関数（必要に応じて使用） ---
def get_device_list(deviceListJson="deviceList.json"):
    headers = make_request_header(TOKEN, SECRET)
    devices_url = f"{BASE_URL}/v1.1/devices"

    try:
        print("Fetching device list...")
        response = urequests.get(devices_url, headers=headers)
        print("Response Status Code:", response.status_code)
        if response.status_code == 200:
            print("Device List Retrieved Successfully:")
            print(response.text)
            device_list = ujson.loads(response.text)

            # デバイスリストをJSONファイルに保存
            with open(deviceListJson, 'w') as f:
                f.write(ujson.dumps(device_list, ensure_ascii=False, indent=2))
            print(f"Device list saved to {deviceListJson}")
        else:
            print(f"Error {response.status_code}: {response.text}")
        response.close()
    except Exception as e:
        print("Request error:", e)

# --- ロック状態取得関数 ---
def get_lock_status(deviceId: str):
    headers = make_request_header(TOKEN, SECRET)
    status_url = f"{BASE_URL}/v1.1/devices/{deviceId}/status"

    try:
        print(f"Fetching lock status for device {deviceId}...")
        response = urequests.get(status_url, headers=headers)
        print("Response Status Code:", response.status_code)
        if response.status_code == 200:
            status = ujson.loads(response.text)
            return status
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print("Request error:", e)
        return None

# --- メインループ ---
def main():
    # Wi-Fi接続
    connect_wifi(SSID, PASSWORD)

    # 時刻同期
    set_time()

    last_check = 0
    is_locked = False

    while True:
        current_time = time.time()
        if current_time - last_check >= CHECK_INTERVAL:
            status = get_lock_status(DEVICE_ID)
            last_check = current_time

            if status and "body" in status and "lockState" in status["body"]:
                lock_state = status["body"]["lockState"]
                print(f"Lock State: {lock_state}")

                if lock_state == "locked":
                    is_locked = True
                elif lock_state == "unlocked":
                    is_locked = False
                else:
                    print("Unknown lock state:", lock_state)
            else:
                print("Invalid status response:", status)

        if is_locked:
            # LEDを点滅
            led.on()
            time.sleep(BLINK_INTERVAL)
            led.off()
            time.sleep(BLINK_INTERVAL)
        else:
            # LEDを消灯
            led.off()
            time.sleep(1)  # チェック間隔に影響しないように少し待機

# --- スクリプトの実行 ---
if __name__ == "__main__":
    main()
