import asyncio
from vibration_feedback import timed_vibrator_pulse, initializeOutputDevices, shutDownOutputDevices
from Sensor import initialize_all_sensors, shutdown_all_sensors
from audio_feedback import speak
import RPi.GPIO as GPIO
from time import time, sleep
import uart_communication as ucomm

from Camera import (
    camera_init,
    detection_model_init,
    capture_frame,
    detect_object,
    draw_boxes,
    show_frame,
    close_camera
)

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

# list to store more recent distance for each sensor
SENSOR_DISTANCE = []

# also ref detector from camera.py
detector = None

'''
    Helper functions
'''
"""
    Takes a distance measurement in mm, performs a calculation, then returns the integer 
    representing the time second delay used between vibrational pulses.
"""
def determine_delay(distance: int) -> int:
    scaling = 2.5
    if distance < OUTER_RANGE_MM:
        value = distance / OUTER_RANGE_MM
        return (value * scaling)

    return 0


"""
    Determines which vibrator index to use based on a ranging sensor position
"""
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
"""
    Handles all feedback operations. Currently this is an audio feedback opertaion
    as well as pulsing of vibrational sensors.
"""
# async def handleFeedback():
#     vibrator_tasks: list = [None for i in range(len(DEVICE_LIST))]
#     speak_task: asyncio.Task[None] = None

#     while not THREAD_KILL.is_set():
#         if len(SENSOR_DISTANCE) > 0:
#             print(SENSOR_DISTANCE)

#         for index, device in enumerate(DEVICE_LIST):
#             if THREAD_KILL.is_set():
#                 break

#             if vibrator_tasks[index] is None or vibrator_tasks[index].done() and VIBRATOR_DURATIONS[index] > 0:
#                 vibrator_tasks[index] = asyncio.create_task(timed_vibrator_pulse(VIBRATOR_DURATIONS[index], [device]))

#         '''We need to consume some text and pass it into the speak function DONE'''
#         '''Pulls whatever is on the queue in audio_feedback.py'''
#         if speak_task is None or speak_task.done():
#             # tts = getNextAudioMessage()
#             tts = ucomm.readUARTMsg()
#             if tts:
#                 speak_task = asyncio.create_task(speak(tts))

#         await asyncio.sleep(0.1)

#     shutDownOutputDevices(DEVICE_LIST)
    
    
async def handleVibrationalFeedback():
    vibrator_tasks: list = [None for _ in range(len(DEVICE_LIST))]

    while not THREAD_KILL.is_set():
        for index, device in enumerate(DEVICE_LIST):
            if THREAD_KILL.is_set():
                break

            if (vibrator_tasks[index] is None or vibrator_tasks[index].done()) and VIBRATOR_DURATIONS[index] > 0.0:
                vibrator_tasks[index] = asyncio.create_task(timed_vibrator_pulse(VIBRATOR_DURATIONS[index], [device]))
    
        await asyncio.sleep(0.1)
    
    shutDownOutputDevices(DEVICE_LIST)


def handleAudioFeedback():
    active_objects = set()  
    while not THREAD_KILL.is_set():
        msg = ucomm.readUARTMsg()
        if not msg:
            continue
            
        if msg.startswith("New:"):
            objects = msg[4:].split(',')
            for obj in objects:
                if obj not in active_objects:
                    speak(obj)
                    active_objects.add(obj)
                    
        elif msg.startswith("Removed:"):
            objects = msg[5:].split(',')
            for obj in objects:
                if obj in active_objects:
                    active_objects.remove(obj)


"""
    Handles reading distance from TOF sensor then populates a list with delays
"""
def handleTOF():

    previous_distance = []
    # during regular operations we check agaisn't the previous distance 
    #  and only update the dealy when the distance difference is +- 100 mm
    #  for this reason we initialize the previous distance list with large 
    #  negative numbers so it evaluates to true
    for i in range(len(SENSOR_LIST)):
        previous_distance.append(-1000)

    while not THREAD_KILL.is_set():
        print(SENSOR_DISTANCE)
        for index, sensor in enumerate(SENSOR_LIST):
            if THREAD_KILL.is_set():
                break

            distance = sensor.get_distance()
            
            # if distance is less than zero we assume it's a bad reading
            if distance < 0:
                continue


            # here store the latest distance for whichever sensor 
            SENSOR_DISTANCE[index] = distance

            '''I'm not sure how this needs to change just yet to make things work with audio code SEE RIGHT ABOVE'''
            # sensor_distance_queue.put(distance)
            
            device_index = determine_vibrator_index(index, len(SENSOR_LIST), DEVICE_LIST)
            delay = determine_delay(distance)

            if distance > previous_distance[index] + 100 or distance < previous_distance[index] - 100:
                VIBRATOR_DURATIONS[device_index] = delay

        msg = ",".join(str(x) for x in SENSOR_DISTANCE)
        ucomm.sendUARTMsg(msg)

        sleep(0.005)

    shutdown_all_sensors(SENSOR_LIST)


"""
    Handles presense of the objects by tracking them and then sends UART updates 
"""
def handleObjectPresence(detected_objects, previous_objects):
    # check if there are unique object classes 
    current_objects = {obj["label"].lower() for obj in detected_objects}
    # see if there are any changes to what is being detected 
    new_objects = current_objects - previous_objects
    removed_objects = previous_objects - current_objects
    
    #UART updates 
    if new_objects:
        ucomm.sendUARTMsg(f"New: {', '.join(new_objects)}")
    if removed_objects:
        ucomm.sendUARTMsg(f"Removed: {', '.join(removed_objects)}")

    return current_objects

"""
    Handles object position on camera and distance to the sensors by calculating boundaries. 
"""
def processObjectPosition(obj, local_sensor_distance, frame_width, outer_range):
    label = obj["label"]
    (cx, _) = obj["centroid"]

    third = len(local_sensor_distance) // 3
    left_boundary = frame_width / 3
    right_boundary = 2 * frame_width / 3

    # directions 
    #sensor index here isn't safe. list size could change in the future
    if cx < left_boundary:
        direction = "left"
        sensor_start = 0
        sensor_end = third * 1
    elif cx > right_boundary:
        direction = "right"
        sensor_start = third * 2
        sensor_end = third * 3
    else:
        direction = "in front"
        sensor_start = third * 1
        sensor_end = third * 2
    
    
    # Find distance related to object (guess closest)
    # dist_mm = (min(local_sensor_distance[i]) for i in range(sensor_start_range, sensor_stop_range) if local_sensor_distance[i] > 0)
    dist_mm = OUTER_RANGE_MM + 1
    for i in range(sensor_start, sensor_end):
        if local_sensor_distance[i] <= 0:
            continue
        dist_mm = min(dist_mm, local_sensor_distance[i])

    # Objects might be detected outside of the range we care about
    # continue if that is the case
    if dist_mm > outer_range:
        return None

    return f"{label} {direction} {dist_mm} mm"

"""
    Handles the object detail processing to see if it's within sensor range. It also calculates
    positioning and distance for each valid object. Sends formatted message via UART for the 
    audio and vibrational feedback.
"""
def handleObjectDetails(detected_objects, local_sensor_distance, frame, outer_range):
    if not detected_objects:
        return
    
    # check if any sensor is under 3000 mm range
    in_range = any(dist < outer_range for dist in local_sensor_distance)
    if not in_range:
        return
    
    # get the width of the frame for position calculations
    frame_width = frame.shape[1]

    # loop through all detected objects and get message 
    for obj in detected_objects:
        message = processObjectPosition(obj, local_sensor_distance, frame_width, outer_range)
        if message:
            print(message)  
            ucomm.sendUARTMsg(message)


def handleCamera():
    '''
    Can we just have detect object detecting 1 object then returning information here?
    From this point we can take that info and put it into the list/queue that will handle the 
    feedback in the handleFeedback function?
    '''
    global previous_objects 
    previous_objects = set()

    try: 
        while not THREAD_KILL.is_set():
            if THREAD_KILL.is_set():
                break

            local_sensor_distance = ucomm.getDistanceData()
            # local_sensor_distance = [123, 456, 789]
            if local_sensor_distance is None:
                continue

            # next capture a frame from the camera
            frame = capture_frame()
            if frame is None:
                continue

            # first run detection so boundary boxes can be drawn 
            detections = detect_object(frame)
            # then draw the boxes on the image
            detected_objects = draw_boxes(frame, detections)

            if THREAD_KILL.is_set():
                break
                
            if show_frame(frame) or THREAD_KILL.is_set():
                break

            previous_objects = handleObjectPresence(detected_objects, previous_objects)
            handleObjectDetails(detected_objects, local_sensor_distance, frame, OUTER_RANGE_MM)

    finally:
        close_camera()
        # # check if there are unique object classes 
        # current_objects = {obj["label"].lower() for obj in detected_objects}
        # # see if there are any changes to what is being detected 
        # new_objects = current_objects - previous_objects
        # removed_objects = previous_objects - current_objects
        
        # #UART updates 
        # if new_objects:
        #     ucomm.sendUARTMsg(f"New: {', '.join(new_objects)}")
        # if removed_objects:
        #     ucomm.sendUARTMsg(f"Removed: {', '.join(removed_objects)}")
        # previous_objects = current_objects

        # # check if any sensor is under 3000 mm range 
        # in_range = any(dist < OUTER_RANGE_MM for dist in local_sensor_distance)
        # if in_range and detected_objects:
        #     # add the left, right or center 
        #     width = frame.shape[1]
        #     left_boundary = width / 3
        #     right_boundary = 2 * width / 3

        #     for obj in detected_objects:
        #         label = obj["label"]
        #         (cx, _) = obj["centroid"]

        #         # directions 
        #         """sensor index here isn't safe. list size could change in the future"""
        #         third = len(local_sensor_distance) // 3
        #         if cx < left_boundary:
        #             direction = "left"
        #             sensor_start_range = 0
        #             sensor_stop_range = third * 1
        #         elif cx > right_boundary:
        #             direction = "right"
        #             sensor_start_range = third * 2
        #             sensor_stop_range = third * 3
        #         else:
        #             direction = "in front"
        #             sensor_start_range = third * 1
        #             sensor_stop_range = third * 2
                
                
        #         # Find distance related to object (guess closest)
        #         # dist_mm = (min(local_sensor_distance[i]) for i in range(sensor_start_range, sensor_stop_range) if local_sensor_distance[i] > 0)
        #         dist_mm = OUTER_RANGE_MM + 1
        #         for i in range(sensor_start_range, sensor_stop_range):
        #             if local_sensor_distance[i] <= 0:
        #                 continue
        #             dist_mm = min(dist_mm, local_sensor_distance[i])

        #         # Objects might be detected outside of the range we care about
        #         # continue if that is the case
        #         if dist_mm > OUTER_RANGE_MM:
        #             continue

        #         text = f"{label} {direction} {dist_mm} mm"
                # here we can add the object to the queue for audio feedback
                # pushAudioMessage(text)
                # print(text)
                # ucomm.sendUARTMsg(text)
            
    # close_camera()  


"""
    Initializes all devices preparing them for ranging and feedback operations
"""
def initialize_all():
    # Initialize all global variables required to run threads here
    # Initialize all devices that require it here
    global SENSOR_LIST
    global DEVICE_LIST
    

    SENSOR_LIST = initialize_all_sensors()
    DEVICE_LIST = initializeOutputDevices()
    '''I believe this calls another function with enters an infinite loop, we should have this changed'''
    ''' camera_init() no longer has infinite loop'''
    # camera_init()
    # detection_model_init()

    global VIBRATOR_DURATIONS
    VIBRATOR_DURATIONS = [0 for _ in range(len(DEVICE_LIST))]

    global SENSOR_DISTANCE
    SENSOR_DISTANCE = [0 for _ in range(len(SENSOR_LIST))]

    return

if __name__ == "__main__":
    camera_init()
    detection_model_init()
    handleCamera()
    # handleFeedback()
