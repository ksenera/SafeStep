from Sensor import initialize_all_sensors
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


"""
    This function is the main loop that runs on a task to constantly send 
    a vibration to a specific device

    Parameters: vibrator_gpio - the gpio pin number of the vibrator being plused
                timespan - the timespan in seconds that the vibrator should be turned on for
"""
def vibrator_loop(vibrator_gpio: int, timespan: int) -> None:
    while True:
        timed_vibrator_pulse(timespan=timespan, gpio_pin1=vibrator_gpio)
        sleep(timespan)


"""
    This class acts like a c struct and is used as the value in the task dictionary
    which helps keep track of running tasks

    Constructor: task - the task being ran
                 distance - the distance at the time of the task being ran
"""
class ThreadInfo:
    def __init__(self, task, distance):
        self.task = task
        self.distance = distance


"""
    This function determines the delay to use between sending pulses to vibrators

    Parameters: distance - the distance reading from the tof sensor
"""
def determine_delay(distance: int) -> int | None:
    scaling = 2.5
    if distance < OUTER_RANGE_MM:
        value = distance / OUTER_RANGE_MM
        return (value * scaling)

    return None


"""
    This function handles creating and cancelling task loops that send vibrations to the
    vibrational devices depending on the readings of the tof sensors

    Parameters: vibrator_gpio - the pin number of the vibrator being turned on
                distance - the distance read from the tof sensor
"""
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

