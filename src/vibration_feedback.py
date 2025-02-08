"""
* File: vibration_feedback.py
* Project: DMDforVI
* First version: 2025 - 01 - 30
* Description: This files holds the necessary functionality to send signals to the vibration device
"""
from gpiozero import DigitalOutputDevice
import time

gpio_pin_right = 18
gpio_pin_left = 17
gpio_pin_middle = 16

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
    while i < 5:
        device1.on()
        device2.on()
        device3.on()
        time.sleep(1)
        device1.off()
        device2.off()
        device3.off()
        time.sleep(3)


"""
* Function    : one_vibrator_pulse
* Description : Send the pulse signal to one motor
* Parameters  : gpio_pin1 : holds one of the pins the signal is sent to, timespan : allows you to set the time is seconds for the delay
* Returns     : NULL
"""

def one_vibrator_pulse (gpio_pin1, timespan):
    device1 = DigitalOutputDevice(gpio_pin1)

    device1.on()

    time.sleep(timespan)

    device1.off()


"""
* Function    : two_vibrator_pulse
* Description : Send the pulse signal to two different motors
* Parameters  : gpio_pin1 : holds one of the pins the signal is sent to, gpio_pin2 : holds one of the pins the signal is sent to, timespan : allows you to set the time is seconds for the delay
* Returns     : NULL
"""

def two_vibrator_pulse(gpio_pin1 , gpio_pin2, timespan):
    device1 = DigitalOutputDevice(gpio_pin1)
    device2 = DigitalOutputDevice(gpio_pin2)

    device1.on()
    device2.on()

    time.sleep(timespan)

    device1.off()
    device2.off()


"""
* Function    : three_vibrator_pulse
* Description : Send the pulse signal to 3 different motors
* Parameters  : gpio_pin1 : holds one of the pins the signal is sent to, gpio_pin2 : holds one of the pins the signal is sent too, gpio_pin3 : holds one of the pins the signal is sent too, allows you to set the time is seconds for the delay
* Returns     : NULL
"""

def three_vibrator_pulse(gpio_pin1 , gpio_pin2, gpio_pin3, timespan):
    device1 = DigitalOutputDevice(gpio_pin1)
    device2 = DigitalOutputDevice(gpio_pin2)
    device3 = DigitalOutputDevice(gpio_pin3)

    device1.on()
    device2.on()
    device3.on()

    time.sleep(timespan)

    device1.off()
    device2.off()
    device3.off()