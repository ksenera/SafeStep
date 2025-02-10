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
                timespan = 1
                timed_vibrator_pulse(timespan, vibrator_gpio)

