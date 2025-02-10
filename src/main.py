from Sensor import initialize_all_sensors, shutdown_all_sensors
from vibration_feedback import timed_vibrator_pulse

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
                # determine which sensor should be triggered
                sensor_count = len(sensor_list)
                
                # Determine which vibrator should be used
                value = (index + 1) / sensor_count
                vibrator_count = len(VIBRATOR_PINS)
                vibrator_index = round(vibrator_count * value) - 1

                timespan = 1
                timed_vibrator_pulse(timespan, VIBRATOR_PINS[vibrator_index])

