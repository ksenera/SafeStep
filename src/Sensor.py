import VL53L1X
import adafruit_tca9548a
import board

# The I2C bus for external devices connected to the pi
I2C_BUS = 1


"""
    Opens the sensor up for communication and begins ranging

    Parameters: sensor_address - The address of the sensor (ex. 0x29)
                ranging_mode - The ranging mode to start in
"""
def initialize_sensor(sensor_address: int, 
                      ranging_mode: VL53L1X.VL53L1xDistanceMode = VL53L1X.VL53L1xDistanceMode.SHORT, 
                      multiplexer_address: int = 0, 
                      multiplexer_channel: int = 255) -> VL53L1X.VL53L1X:
    sensor = VL53L1X.VL53L1X(i2c_bus=I2C_BUS, i2c_address=sensor_address, tca9548a_addr=multiplexer_address, tca9548a_num=multiplexer_channel)
    sensor.open()
    sensor.start_ranging(ranging_mode)

    return sensor


"""
    Stops ranging before closing sensor connection

    Parameters: sensor - The VL53L1X object of the sensor being shutdown
"""
def shutdown_sensor(sensor: VL53L1X.VL53L1X):
    sensor.stop_ranging()
    sensor.close()


"""
    Handles initializing all sensors from the multiplexer then returns a list of initialized sensors,
    list is ordered by channel number of the multiplexer

    Parameters: ranging_mode - the ranging mode the sensor will be started in
"""
def initialize_all_sensors(ranging_mode: VL53L1X.VL53L1xDistanceMode = VL53L1X.VL53L1xDistanceMode.SHORT) -> list[VL53L1X.VL53L1X]:
    i2c = board.I2C(I2C_BUS)
    tca = adafruit_tca9548a.TCA9548A(i2c)

    sensor_list = []

    # Initialize all sensors on multiplexer
    for channel in range(8):
        if tca[channel].try_lock():            
            # Initialize sensor using address assigned to channel
            sensor = initialize_sensor(tca[channel], ranging_mode=ranging_mode)
            
            sensor_list.append(sensor)

    return sensor_list


"""
    Handles shutting down all sensors in the sensor list

    Parameters: sensor_list - the list containing initliazed sensor objects
"""
def shutdown_all_sensors(sensor_list: list[VL53L1X.VL53L1X]):
    for item in sensor_list:
        shutdown_sensor(item)

