from main import MASTERBOOLEAN
from vibration_feedback import timed_vibrator_pulse
from main import speak
import RPi.GPIO as GPIO

MASTERLIST = []
# 3 meters
OUTER_RANGE_MM = 3000
# Anything below inner range will be used to 
# send fastest vibrational pulse
INNER_RANGE_MM = 500
SENSOR_LIST = []
DEVICE_LIST = []


def determine_delay(distance: int) -> int | None:
    scaling = 2.5
    if distance < OUTER_RANGE_MM:
        value = distance / OUTER_RANGE_MM
        return (value * scaling)

    return None

def determine_vibrator_index(sensor_index: int, sensor_count: int, digital_devices: list) -> int:
    # Determine which vibrator should be used
    value = (sensor_index + 1) / sensor_count

    device_count = len(digital_devices)
    device_index = round(device_count * value) - 1

    return device_index

def handleFeedback():
    while MASTERBOOLEAN:
        for index, device in enumerate(DEVICE_LIST):
            Pin_On = GPIO.input(device.pin)
            if not Pin_On and MASTERLIST[index] > 0:
                timed_vibrator_pulse(MASTERLIST[index], [device])
        speak()


def handleTOF():
    previous_distance = []
    # during regular operations we check agaisn't the previous distance 
    #  and only update the dealy when the distance difference is +- 100 mm
    #  for this reason we initialize the previous distance list with large 
    #  negative numbers so it evaluates to true
    for i in range(SENSOR_LIST):
        previous_distance[i] = -1000

    while MASTERBOOLEAN:
        for index, sensor in enumerate(SENSOR_LIST):
            if MASTERBOOLEAN is False:
                break

            distance = sensor.get_distance()
            # if distance is less than zero we assume it's a bad reading
            if distance < 0:
                continue

            print(f'Sensor[{index}]: {distance}mm')

            # I'm not sure how this needs to change just yet to make things work with audio code
            # sensor_distance_queue.put(distance)
            
            device_index = determine_vibrator_index(index, len(SENSOR_LIST), DEVICE_LIST)
            delay = determine_delay(distance)

            if distance > previous_distance[index] + 100 or distance < previous_distance[index] - 100:
                MASTERLIST[device_index] = delay
