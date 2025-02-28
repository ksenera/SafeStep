from Sensor import initialize_all_sensors, shutdown_all_sensors
from vibration_feedback import timed_vibrator_pulse, initializeOutputDevices, shutDownOutputDevices
from Camera import camera_init, detect_object
import signal
import threading
from time import sleep
import warnings
from VL53L1X import VL53L1xDistanceMode
from gpiozero import DigitalOutputDevice
import sys
import queue
import subprocess 



# Filters redundent output messages from gpiozero
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
# Holds information for threads running vibrational pulsing
task_dict = {}

device_list = initializeOutputDevices(VIBRATOR_PINS)

sensor_list = initialize_all_sensors(VL53L1xDistanceMode.LONG)

MASTERBOOLEAN = True

sensor_distance_queue = queue.Queue()
detected_category_queue = queue.Queue()


"""
    This function determines the most relevant vibrator to use depending on
    which sensor is detecting an object

    Parameters: sensor_index - the index position of the sensor in the sensor list
                sensor_count - the number of sensors in the list
                digital_devices - the list containing the vibrator information
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
                event - the event associated with the thread used to signal a thread shutdown
"""
def vibrator_loop(device: DigitalOutputDevice, timespan: int, event: threading.Event) -> None:
    while not event.is_set():
        timed_vibrator_pulse(timespan=timespan / 2, deviceList = [device])
        sleep(timespan)


"""
    This class acts like a c struct and is used as the value in the task dictionary
    which helps keep track of running tasks

    Constructor: new_thread - the thread created that runs the vibrational pulsing
                 new_event - the event object used to signal an end to the thread loop
                 distance - the distance at the time of the thread being started
"""
class ThreadInfo:
    def __init__(self, new_thread: threading.Thread, new_event: threading.Event, distance):
        self.thread = new_thread
        self.event = new_event
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
    running_thread = task_dict.get(digital_device.pin)
    new_delay = determine_delay(distance)

    # Check for prexisting task
    if running_thread is not None:
        # Determine if new distance requires different vibrational timing
        if determine_delay(running_thread.distance) != new_delay:
            # Shut down the thread
            running_thread.event.set()

            if new_delay is not None:
                # Create a new thread with updated pulse duration
                new_event = threading.Event() # Reset the event before starting a new thread with the same event
                running_thread.thread = threading.Thread(target=vibrator_loop, args=[digital_device, new_delay, new_event])
                running_thread.event = new_event
                running_thread.thread.start()
            else:
                task_dict.pop(digital_device.pin)
    else:
        if new_delay is not None:
            # Create new task
            new_event = threading.Event()
            new_thread = threading.Thread(target=vibrator_loop, args=[digital_device, new_delay, new_event])
            new_info = ThreadInfo(new_thread, new_event, distance)
            new_info.thread.start()
            task_dict[digital_device.pin] = new_info

def camera_thread_method():
    camera_init(detected_category_queue, sensor_distance_queue)

def speak(text):
    subprocess.run(["flite", "-voice", "rms", "-t", text])

def cleanup_processes(signum, frame):
    global MASTERBOOLEAN
    MASTERBOOLEAN = False
    
    sleep(1)
    
    for value in task_dict.values():
        value.event.set()

    for value in task_dict.values():
        value.thread.join()

    shutDownOutputDevices(device_list)
    shutdown_all_sensors(sensor_list)
    
    #sys.exit(0)



def main():
    #sensor_list = initialize_all_sensors(VL53L1xDistanceMode.LONG)
    #device_list = initializeOutputDevices(VIBRATOR_PINS)
    global sensor_list #= list(g_sensor_list)
    global device_list #= list(g_device_list)
    global MASTERBOOLEAN

    signal.signal(signal.SIGTSTP, cleanup_processes)

    #camera thread
    camera_thread = threading.Thread(target=camera_thread_method)
    camera_thread.daemon = True
    camera_thread.start()

    while MASTERBOOLEAN:

        for index, sensor in enumerate(sensor_list):
            if MASTERBOOLEAN is False:
                break

            distance = sensor.get_distance()
            if distance < 0:
                continue

            print(f'Sensor[{index}]: {distance}mm')
            sensor_distance_queue.put(distance)
            digital_device = determine_vibrator(index, len(sensor_list), device_list)

            # Determine how long a vibrator should be pulsed for
            handle_vibrational_pulsing(digital_device, distance)

                # camera catgory queue check 
        if not detected_category_queue.empty():
            detected_objects = None
            while not detected_category_queue.empty():
                detected_objects = detected_category_queue.get()

            if detected_objects:
                category = detected_objects["classification"]
                centroidx = detected_objects["centroid"][0]
                distance = detected_objects["distance"]
                camera_width = 600 
                if centroidx < camera_width / 2:
                    position = "left"
                else:
                    position = "right"

            print(f"Detected {category} to the {position}, {distance} mm")

            audio_feedback = f"Detected {category} at {distance} mm {position}"
            speak(audio_feedback)
        

if __name__ == "__main__":
    main()
