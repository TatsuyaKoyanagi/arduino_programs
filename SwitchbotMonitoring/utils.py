import urequests
import ujson
import time
import uhashlib
import ubinascii

# Base URL for the Switch-Bot API
BASE_URL = "https://api.switch-bot.com"

# Replace these with your actual token and secret
TOKEN = "a924fa8c7b9116973b2f3c846a511d506cece78e4b2c0693c5593272fa773692a0a1ec3851f1335b10c8a70f199b1289"
SECRET = "8fb22b45c0ddd39c0b76d6d09a20a14b"

def hmac_sha256(key, message):
    """
    Manually implement HMAC-SHA256.

    Args:
        key (bytes): The secret key.
        message (bytes): The message to hash.

    Returns:
        bytes: The HMAC-SHA256 digest.
    """
    block_size = 64  # Block size for SHA256

    if len(key) > block_size:
        key = uhashlib.sha256(key).digest()
    if len(key) < block_size:
        key = key + b'\x00' * (block_size - len(key))

    o_key_pad = bytes([b ^ 0x5c for b in key])
    i_key_pad = bytes([b ^ 0x36 for b in key])

    inner_hash = uhashlib.sha256(i_key_pad + message).digest()
    hmac_result = uhashlib.sha256(o_key_pad + inner_hash).digest()

    return hmac_result

def make_sign(token: str, secret: str):
    """
    Generates the HMAC SHA256 signature required for authentication.

    Args:
        token (str): Your API token.
        secret (str): Your API secret.

    Returns:
        tuple: A tuple containing the signature, timestamp, and nonce.
    """
    nonce = ""  # You can generate a random nonce if required
    t = int(time.time() * 1000)  # Current timestamp in milliseconds
    string_to_sign = f"{token}{t}{nonce}".encode('utf-8')
    secret_bytes = secret.encode('utf-8')

    # Create HMAC SHA256 signature manually
    hmac_digest = hmac_sha256(secret_bytes, string_to_sign)
    signature = ubinascii.b2a_base64(hmac_digest).rstrip(b'\n').decode('utf-8')

    return signature, str(t), nonce

def make_request_header(token: str, secret: str) -> dict:
    """
    Constructs the headers required for API requests.

    Args:
        token (str): Your API token.
        secret (str): Your API secret.

    Returns:
        dict: A dictionary of headers.
    """
    sign, t, nonce = make_sign(token, secret)
    headers = {
        "Authorization": token,
        "sign": sign,
        "t": t,
        "nonce": nonce
    }
    return headers

def get_device_list(deviceListJson="deviceList.json"):
    """
    Retrieves the list of devices from the Switch-Bot API and saves it to a JSON file.

    Args:
        deviceListJson (str): The filename to save the device list.
    """
    headers = make_request_header(TOKEN, SECRET)
    devices_url = f"{BASE_URL}/v1.1/devices"

    try:
        response = urequests.get(devices_url, headers=headers)
        if response.status_code == 200:
            print("Device List Retrieved Successfully:")
            print(response.text)
            device_list = ujson.loads(response.text)

            # Save the device list to a JSON file
            with open(deviceListJson, 'w') as f:
                f.write(ujson.dumps(device_list, ensure_ascii=False, indent=2))
        else:
            print(f"Error {response.status_code}: {response.text}")
        response.close()
    except Exception as e:
        print("Request error:", e)

def get_lock_status(deviceId: str):
    headers = make_request_header(TOKEN, SECRET)
    status_url = f"{BASE_URL}/v1.1/devices/{deviceId}/status"

    try:
        response = urequests.get(status_url, headers=headers)
        if response.status_code == 200:
            status = ujson.loads(response.text)
            return status
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print("Request error:", e)
        return None

def print_json(deviceListJson="deviceList.json"):
    """
    Reads and prints the device list from a JSON file.

    Args:
        deviceListJson (str): The filename of the device list.
    """
    try:
        with open(deviceListJson, 'r') as f:
            device_list = ujson.load(f)
            print("Device List:")
            print(ujson.dumps(device_list["body"]["deviceList"], ensure_ascii=False, indent=2))
    except Exception as e:
        print("Error reading JSON:", e)

if __name__ == "__main__":
    # Uncomment the following line to retrieve and save the device list
    # get_device_list()

    # Replace "CF3C03B1250E" with your actual device ID
    device_id = "CF3C03B1250E"
    status = get_lock_status(device_id)

    if status:
        print("Lock Status:")
        print(ujson.dumps(status, ensure_ascii=False, indent=2))
