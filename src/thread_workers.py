import asyncio
from vibration_feedback import timed_vibrator_pulse, initializeOutputDevices, shutDownOutputDevices
from Sensor import initialize_all_sensors, shutdown_all_sensors
from Camera import camera_init
from audio_feedback import speak
import RPi.GPIO as GPIO
from Camera import detect_object
from threading import Event

# The event object used to stop all threads
THREAD_KILL: Event = Event()

# Vibrator durations list holds the duration that a vibrator will sleep before turning off
VIBRATOR_DURATIONS = []
# 3 meters
OUTER_RANGE_MM = 3000
# Anything below inner range will be used to 
# send fastest vibrational pulse
INNER_RANGE_MM = 500
# Sensor list holds all the ToF sensor objects
SENSOR_LIST = []
# Device list holds all digital output devices
DEVICE_LIST = []


'''
    Helper functions
'''
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


'''
    Main thread functions
'''
# This function should be ran in the following way
# asyncio.run(handleFeedback())
async def handleFeedback():
    vibrator_tasks: list = [None for i in range(len(DEVICE_LIST))]
    speak_task: asyncio.Task[None] = None

    while not THREAD_KILL.is_set():
        for index, device in enumerate(DEVICE_LIST):
            if THREAD_KILL.set():
                break

            if vibrator_tasks[index] is None or vibrator_tasks[index].done() and VIBRATOR_DURATIONS[index] > 0:
                vibrator_tasks[index] = asyncio.create_task(timed_vibrator_pulse(VIBRATOR_DURATIONS[index], [device]))

        '''We need to consume some text and pass it into the speak function'''
        if speak_task is None or speak_task.done():
            speak_task = asyncio.create_task(speak()) # I NEED TEXT U FUCK

        asyncio.sleep(0.1)

    shutDownOutputDevices(DEVICE_LIST)


def handleTOF():
    previous_distance = []
    # during regular operations we check agaisn't the previous distance 
    #  and only update the dealy when the distance difference is +- 100 mm
    #  for this reason we initialize the previous distance list with large 
    #  negative numbers so it evaluates to true
    for i in range(SENSOR_LIST):
        previous_distance[i] = -1000

    while not THREAD_KILL.is_set():
        for index, sensor in enumerate(SENSOR_LIST):
            if THREAD_KILL.set():
                break

            distance = sensor.get_distance()
            # if distance is less than zero we assume it's a bad reading
            if distance < 0:
                continue

            print(f'Sensor[{index}]: {distance}mm')

            '''I'm not sure how this needs to change just yet to make things work with audio code'''
            # sensor_distance_queue.put(distance)
            
            device_index = determine_vibrator_index(index, len(SENSOR_LIST), DEVICE_LIST)
            delay = determine_delay(distance)

            if distance > previous_distance[index] + 100 or distance < previous_distance[index] - 100:
                VIBRATOR_DURATIONS[device_index] = delay

    shutdown_all_sensors(SENSOR_LIST)


def handleCamera():
    '''
    Can we just have detect object detecting 1 object then returning information here?
    From this point we can take that info and put it into the list/queue that will handle the 
    feedback in the handleFeedback function?
    '''
    results = detect_object()


def initialize_all():
    # Initialize all global variables required to run threads here
    # Initialize all devices that require it here
    SENSOR_LIST = initialize_all_sensors()
    DEVICE_LIST = initializeOutputDevices()
    '''I believe this calls another function with enters an infinite loop, we should have this changed'''
    camera_init()

    return
