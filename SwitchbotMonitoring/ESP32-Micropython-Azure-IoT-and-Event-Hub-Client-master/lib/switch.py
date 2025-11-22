from machine import Pin
import machine
import time

SW_PIN_1 = 19
SW_PIN_2 = 20

sw1 = Pin(SW_PIN_1, Pin.IN, Pin.PULL_UP)
sw2 = Pin(SW_PIN_2, Pin.IN, Pin.PULL_UP)
LED1=machine.Pin(39, machine.Pin.OUT)
LED2=machine.Pin(40, machine.Pin.OUT)


while True:
    if sw1.value()==0:
        LED1.on()
    else :
        LED1.off()
    if sw2.value()==0:
        LED2.on()
    else :
        LED2.off()
    time.sleep_ms(10)
