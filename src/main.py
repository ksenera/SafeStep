from Sensor import initialize_all_sensors, shutdown_all_sensors
from vibration_feedback import timed_vibrator_pulse, initializeOutputDevices, shutDownOutputDevices
import signal
from multiprocessing import Process
from time import sleep
import warnings
from VL53L1X import VL53L1xDistanceMode
from gpiozero import DigitalOutputDevice


warnings.simplefilter("ignore")

# 3 meters
OUTER_RANGE_MM = 3000
# Anything below inner range will be used to 
# send fastest vibrational pulse
INNER_RANGE_MM = 500
VIBRATOR_PINS = [
    18,
    24,
    25
]
task_dict = {}



"""
    This function determines the most relevant vibrator to use depending on
    which sensor is detecting an object

    Parameters: sensor_index - the index position of the sensor in the sensor list
                sensor_count - the number of sensors in the list
"""
def determine_vibrator(sensor_index: int, sensor_count: int, digital_devices: list[DigitalOutputDevice]) -> DigitalOutputDevice:
    # Determine which vibrator should be used
    value = (sensor_index + 1) / sensor_count

    device_count = len(digital_devices)
    device_index = round(device_count * value) - 1

    return digital_devices[device_index]


"""
    This function is the main loop that runs on a task to constantly send 
    a vibration to a specific device

    Parameters: vibrator_gpio - the gpio pin number of the vibrator being plused
                timespan - the timespan in seconds that the vibrator should be turned on for
"""
def vibrator_loop(device: DigitalOutputDevice, timespan: int) -> None:
    while True:
        timed_vibrator_pulse(timespan=timespan / 2, deviceList = [device])
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
def handle_vibrational_pulsing(digital_device: DigitalOutputDevice, distance):
    info = task_dict.get(digital_device.pin)
    new_delay = determine_delay(distance)

    # Check for prexisting task
    if info is not None:
        # Determine if new distance requires different vibrational timing
        if determine_delay(info.distance) != new_delay:
            info.task.terminate()
            if new_delay is not None:
                #info.task = threading.Thread(target=vibrator_loop, args=[vibrator_gpio, new_delay])
                info.task = Process(target=vibrator_loop, args=[digital_device, new_delay])
                info.task.start()
            else:
                task_dict.pop(digital_device.pin)
    else:
        if new_delay is not None:
            # Create new task
            #task = threading.Thread(target=vibrator_loop, args=[vibrator_gpio, new_delay])
            task = Process(target=vibrator_loop, args=[digital_device, new_delay])
            new_info = ThreadInfo(task, distance)
            new_info.task.start()
            task_dict[digital_device.pin] = new_info


def cleanup_processes():
    for key, value in task_dict:
        value.task.terminate()

    # shutDownOutputDevices()
    # shutdown_all_sensors()

    exit()


if __name__ == "__main__":
    sensor_list = initialize_all_sensors(VL53L1xDistanceMode.LONG)
    device_list = initializeOutputDevices(VIBRATOR_PINS)

    signal.signal(signal.SIGINT, cleanup_processes)

    while True:
        for index, sensor in enumerate(sensor_list):
            distance = sensor.get_distance()
            print(f'Sensor[{index}]: {distance}mm')
            digital_device = determine_vibrator(index, len(sensor_list), device_list)

            # Determine how long a vibrator should be pulsed for
            handle_vibrational_pulsing(digital_device, distance)
            
