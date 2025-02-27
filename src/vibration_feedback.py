"""
* File: vibration_feedback.py
* Project: DMDforVI
* First version: 2025 - 01 - 30
* Description: This files holds the necessary functionality to send signals to the vibration device
"""
from gpiozero import DigitalOutputDevice
import time


defaultPinList = [18, 24, 25]

"""
* Function    : startup_pulse
* Description : Send the pulse signal for startup feedback
* Parameters  : gpio_pin : holds the gpio pin where the signal is sent which is connected to the motor
* Returns     : NULL
"""
def startup_pulse(gpio_pin1, gpio_pin2, gpio_pin3):
    device1 = DigitalOutputDevice(gpio_pin1)
    device2 = DigitalOutputDevice(gpio_pin2)
    device3 = DigitalOutputDevice(gpio_pin3)
    i = 0

    #sends a pulse of 1 second on and 1 second off 5 times can be changed depending on th pulse length we want
    while i < 5:
        device1.on()
        device2.on()
        device3.on()
        time.sleep(1)
        device1.off()
        device2.off()
        device3.off()
        time.sleep(1)
        i += 1

"""
* Function    : sleep_pulse
* Description : Send the pulse signal for sleep feedback
* Parameters  : gpio_pin : holds the gpio pin where the signal is sent which is connected to the motor
* Returns     : NULL
"""

def sleep_pulse(gpio_pin1, gpio_pin2, gpio_pin3):
    device1 = DigitalOutputDevice(gpio_pin1)
    device2 = DigitalOutputDevice(gpio_pin2)
    device3 = DigitalOutputDevice(gpio_pin3)

    device1.on()
    device2.on()
    device3.on()

    time.sleep(5)

    device1.off()
    device2.off()
    device3.off()


"""
* Function    : error_pulse
* Description : Send the pulse signal for error feedback
* Parameters  : gpio_pin : holds the gpio pin where the signal is sent which is connected to the motor
* Returns     : NULL
"""

def error_pulse(gpio_pin1, gpio_pin2, gpio_pin3):
    device1 = DigitalOutputDevice(gpio_pin1)
    device2 = DigitalOutputDevice(gpio_pin2)
    device3 = DigitalOutputDevice(gpio_pin3)
    i = 0

    # sends a pulse of 1 second on and 3 second off 5 times can be changed depending on th pulse length we want
    while i < 3:
        device1.on()
        device2.on()
        device3.on()
        time.sleep(1)
        device1.off()
        device2.off()
        device3.off()
        time.sleep(3)
        i += 1


"""
* Function    : timed_vibrator_pulse
* Description : Send a pulse signal for s given timespan to one two or all the motors
* Parameters  : timespan : Amount of time for the vibrator pulse, gpio_pin1 : one of the gpio pins connected to the motor, gpio_pin2 : one of the gpio pins connected to the motor, gpio_pin3 : one of the gpio pins connected to the motor
* Returns     : NULL
"""

def timed_vibrator_pulse (timespan: int, deviceList: list[DigitalOutputDevice]) -> None:

    for device in deviceList:
        device.on()
    
    time.sleep(timespan)

    for device in deviceList:
        device.off()




def initializeOutputDevices(pinList:list = None) -> list[DigitalOutputDevice]:
    devices = []

    if pinList is None:
        pinList = defaultPinList

    for pins in pinList:
        device = DigitalOutputDevice(pins)
        devices.append(device)

    if len(devices) == 0:
        raise Exception("Gpio Pin list empty")
    
    return devices

def shutDownOutputDevices(device_list: list[DigitalOutputDevice]) -> None:
    for device in device_list:
        device.off()
        device.close()
        
    device_list.clear()
        

if __name__ == "__main__":
    
    devicelist = initializeOutputDevices(None)

    while True:
        timed_vibrator_pulse(1, devicelist)
        time.sleep(1)
    


