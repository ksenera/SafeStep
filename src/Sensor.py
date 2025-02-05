import VL53L1X

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
