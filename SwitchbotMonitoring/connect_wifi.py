def do_connect():
    import network

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("connecting to network...")
        wlan.connect("SSID", "password")
        while not wlan.isconnected():
            pass
    print(
        "network config:", wlan.ifconfig()
    )  # IPアドレス、ネットマスク、ゲートウェイ、DNS


if __name__ == "__main__":
    do_connect()
