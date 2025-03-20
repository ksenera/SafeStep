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

def detect_object(detected_category_queue=None, sensor_distance_queue=None):
    #Initialize inference options for the Mediapipe object
    base_options = python.BaseOptions(model_asset_path = 'efficientdet.tflite')
    options = vision.ObjectDetectorOptions(base_options=base_options,
                                        score_threshold=0.5)

    detector = vision.ObjectDetector.create_from_options(options)

    #Initialize Variables
    #last_time = 0
    #inference_time = 0
    target = 'person'
    while True:
        #Take an image and format it
        image = picam2.capture_array()
        #image = cv2.rotate(image, cv2.ROTATE_180)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
        #rgb_image = cv2.resize(rgb_image,(640,640))
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
    
    
        #Perform inference and time it
        last_time = time.time()
        detection_result = detector.detect(mp_image)
        inference_time = time.time() - last_time
        
        # retrieve distances from sensor
        sensor_distance = None
        if sensor_distance_queue is not None and not sensor_distance_queue.empty():
            sensor_distance = sensor_distance_queue.get()

        pressedKey = cv2.waitKey(30) & 0xFF

        #Parse through detections
        for detection in detection_result.detections:
            category = detection.categories[0]
            classification = category.category_name

            #If the classification matches the target class
            if(classification == target):
                print(str(round(category.score,2)))
                bbox = detection.bounding_box
                detected = 1
                width = bbox.width
                height = bbox.height
                centroidx = bbox.origin_x + (width/2)
                centroidy = bbox.origin_y + (height/2)
                deviationx = centroidx - 240
                deviationy = centroidy - 320
            
                start_point = (bbox.origin_x, bbox.origin_y)
                stop_point = (bbox.origin_x + width, bbox.origin_y + height)
                
                cv2.rectangle(rgb_image, start_point, stop_point, (0, 255, 0), 2)
                
                cv2.putText(rgb_image, category.category_name.upper(), (start_point[0] + 10, start_point[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                if sensor_distance is not None and sensor_distance <= 3000:
                    if detected_category_queue is not None:
                        detected_category_queue.put({
                            "classification": classification,
                            "centroid": (centroidx, centroidy),
                            "distance": sensor_distance
                        })
                
                #print(category.category_name, ", with prob: ", str(round(category.score,2))
                #    , "and centroid: ", str(centroidx),",",str(centroidy))
                #print('deviation from center: ', str(deviationx), ",", str(deviationy))
        
        cv2.imshow('livestream', rgb_image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        #print("Inference Time: ", str(time.time()-last_time))
        #print('--------------------------------------------')