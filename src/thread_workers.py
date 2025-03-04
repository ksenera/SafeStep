from main import MASTERBOOLEAN
from vibration_feedback import timed_vibrator_pulse
from main import deviceList
from main import speak
import RPi.GPIO as GPIO

MASTERLIST = []

def handleFeedback():
    while MASTERBOOLEAN:
        for index, device in enumerate(deviceList):
            Pin_On = GPIO.input(device.pin)
            if not Pin_On and MASTERLIST[index] > 0:
                timed_vibrator_pulse(MASTERLIST[index], [device])
        speak()