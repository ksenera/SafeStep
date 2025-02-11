from Sensor import initialize_all_sensors, shutdown_all_sensors
from vibration_feedback import timed_vibrator_pulse
import threading
from time import sleep

# 3 meters
OUTER_RANGE_MM = 3000
# Anything below inner range will be used to 
# send fastest vibrational pulse
INNER_RANGE_MM = 500
VIBRATOR_PINS = [
    1,
    2,
    3
]


task_dict = {}


"""
    This function determines the most relevant vibrator to use depending on
    which sensor is detecting an object

    Parameters: sensor_index - the index position of the sensor in the sensor list
                sensor_count - the number of sensors in the list
"""
def determine_vibrator(sensor_index: int, sensor_count: int) -> int:
    # Determine which vibrator should be used
    value = (sensor_index + 1) / sensor_count

    vibrator_count = len(VIBRATOR_PINS)
    vibrator_index = round(vibrator_count * value) - 1

    return VIBRATOR_PINS[vibrator_index]


def vibrator_loop(vibrator_gpio: int, timespan: int) -> None:
    while True:
        timed_vibrator_pulse(timespan=timespan, gpio_pin1=vibrator_gpio)
        sleep(timespan)


class ThreadInfo:
    def __init__(self, task, distance):
        self.task = task
        self.distance = distance


def determine_delay(distance: int) -> int | None:
    pass


def handle_vibrational_pulsing(vibrator_gpio, distance):
    info = task_dict.get(vibrator_gpio)
    new_delay = determine_delay(distance)

    # Check for prexisting task
    if info is not None:
        # Determine if new distance requires different vibrational timing
        if determine_delay(info.distance) != new_delay:
            info.task.cancel()
            if new_delay is not None:
                info.task = threading.Thread(target=vibrator_loop, args=[vibrator_gpio, new_delay])
            else:
                task_dict.pop(vibrator_gpio)
    else:
        if new_delay is not None:
            # Create new task
            task = threading.Thread(target=vibrator_loop, args=[vibrator_gpio, new_delay])
            new_info = ThreadInfo(task, distance)
            task_dict[vibrator_gpio] = new_info


if __name__ == "__main__":
    # Project flow

    # Poll sensors

    # If distance of object is within range
        # Send vibrational feedback
    
    sensor_list = initialize_all_sensors()

    while True:
        for index, sensor in enumerate(sensor_list):
            distance = sensor.get_distance()
            if distance < OUTER_RANGE_MM:
                vibrator_gpio = determine_vibrator(index, len(sensor_list))

                # Determine how long a vibrator should be pulsed for
                handle_vibrational_pulsing(vibrator_gpio, distance)

