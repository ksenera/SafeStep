# Import Mediapipe
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Required Peripheral Libraries
import cv2
import numpy as np
import time
import config

# Initialize the camera object
from picamera2 import Picamera2, Preview
import thread_workers 

# config

picam2 = None
camera_config = None
detector = None

"""
    Only initializes PiCamera2 and configures it. This is only called once here as it will
    loop in handleCamera() in thread_workers.py
"""
def camera_init():

    global picam2, camera_config
    picam2 = Picamera2()
    picam2.preview_configuration.main.size=(254,254)
    camera_config = picam2.create_still_configuration({"size": (320,320)})

    picam2.configure(camera_config)
    picam2.start()


"""
    Detection Model initializer that should create the MediaPipe ObjectDetector instance of 
    EfficientDet. Again only called once here. 
"""
def detection_model_init():
    global detector
    #Initialize inference options for the Mediapipe object
    base_options = python.BaseOptions(model_asset_path = config.model_name)
    options = vision.ObjectDetectorOptions(base_options=base_options,
                                        score_threshold=0.5)

    detector = vision.ObjectDetector.create_from_options(options)

"""
    Camera is on but this new function only captures single frame from the camera as thread
    workers will handle the rest of the camera operations. 
"""
def capture_frame():
    global picam2
    # add a check for if the camera is initialized after
    # if thread_workers.THREAD_KILL.is_set():
    #     return True
    
    frame = picam2.capture_array()
    return frame


"""
    Object detection runs on frame already captures and returns the detection results.
"""
def detect_object(frame):
    global detector 
    #image = cv2.rotate(image, cv2.ROTATE_180)
    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    #rgb_frame = cv2.resize(rgb_frame,(640,640))
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB, 
        data=rgb_image
    )
    result = detector.detect(mp_image)
    if result is None:
        return []
    return result.detections 

"""
    On the frame detect boundary boxes and labels are drawn.
    Returns a list of dicts with classfication info
"""
def draw_boxes(frame, detections):
    h, w, _ = frame.shape
    detected_objects = []

    for detection in detections:
        if not detection.categories:
            continue

        category = detection.categories[0]
        classification = category.category_name
        score = category.score

        bbox = detection.bounding_box
        x_min = bbox.origin_x
        y_min = bbox.origin_y
        width = bbox.width
        height = bbox.height

        start_point = (x_min, y_min)
        stop_point = (x_min + width, y_min + height)
        cv2.rectangle(frame, start_point, stop_point, (0, 255, 0), 2)    
        cv2.putText(frame, category.category_name.upper(), (start_point[0] + 10, start_point[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # centroid computed here:
        centroid_x = x_min + width // 2
        centroid_y = y_min + height // 2

        # save into dict for when thread_workers needs it 
        detected_objects.append({
            "label": classification,
            "score": score,
            "centroid": (centroid_x, centroid_y)
        })

    return detected_objects

"""
    show annotated frame and handle q to quit in OpenCV window.  
"""
def show_frame(frame):
    # check here if OpenCV windows hangs critial check
    if thread_workers.THREAD_KILL.is_set():
        return True
    
    cv2.imshow("livestream", frame)
    key = cv2.waitKey(1) & 0xFF

    if cv2.getWindowProperty("livestream", cv2.WND_PROP_VISIBLE) < 1:
        return True
    
    return key == ord('q')

"""
    close camera
"""
def close_camera():
    global picam2
    if picam2:
        try: 
            picam2.stop()
            picam2.close()
        finally:
            picam2 = None
    cv2.destroyAllWindows()

