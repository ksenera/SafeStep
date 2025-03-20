# Import Mediapipe
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Required Peripheral Libraries
import cv2
import numpy as np
import time

# Initialize the camera object
from picamera2 import Picamera2, Preview

picam2 = None
detector = None

"""
    Only initializes PiCamera2 and configures it. This is only called once here as it will
    loop in handleCamera() in thread_workers.py
"""
def camera_init():

    global picam2
    picam2 = Picamera2()
    picam2.preview_configuration.main.size=(254,254)
    camera_config = picam2.create_still_configuration({"size": (600,600)})

    picam2.configure(camera_config)
    picam2.start()


"""
    Detection Model initializer that should create the MediaPipe ObjectDetector instance of 
    EfficientDet. Again only called once here. 
"""
def detection_model_init():
    #Initialize inference options for the Mediapipe object
    base_options = python.BaseOptions(model_asset_path = 'efficientdet.tflite')
    options = vision.ObjectDetectorOptions(base_options=base_options,
                                        score_threshold=0.5)

    return vision.ObjectDetector.create_from_options(options)

"""
    Camera is on but this new function only captures single frame from the camera as thread
    workers will handle the rest of the camera operations. 
"""
def capture_frame():
    global picam2
    # add a check for if the camera is initialized after
    image = picam2.capture_array()
    return image


"""
    Object detection runs on image already captures and returns the detection results.
"""
def detect_object(detector, image):
    #image = cv2.rotate(image, cv2.ROTATE_180)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    #rgb_image = cv2.resize(rgb_image,(640,640))
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
    detection_result = detector.detect(mp_image)
    return detection_result.detections

"""
    On the frame detect boundary boxes and labels are drawn.
    Returns a list of dicts with classfication info
"""
def draw_boxes(image, detections):

    if not detections:
        return []
    
    h, w, _ = image.shape
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
        cv2.rectangle(image, start_point, stop_point, (0, 255, 0), 2)    
        cv2.putText(image, category.category_name.upper(), (start_point[0] + 10, start_point[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

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
    close camera
"""
def close_camera():
    global picam2
    if picam2:
        picam2.stop()
    cv2.destroyAllWindows()

