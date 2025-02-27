import VL53L1X
import adafruit_tca9548a
import board

# The I2C bus number for external devices connected to the pi
I2C_BUS = 1
# ToF Sensor
VL53L1X_DEFAULT_ADDRESS = 0x29
# I2C Multiplexer
TCA9548A_ADDRESS = 0x70

"""
    Opens the sensor up for communication and begins ranging

    Parameters: sensor_address - The address of the sensor (ex. 0x29)
                ranging_mode - The ranging mode to start in
"""
def initialize_sensor(bus: int = I2C_BUS,
                      sensor_address: int = VL53L1X_DEFAULT_ADDRESS, 
                      ranging_mode: VL53L1X.VL53L1xDistanceMode = VL53L1X.VL53L1xDistanceMode.MEDIUM, 
                      multiplexer_address: int = 0, 
                      multiplexer_channel: int = 255) -> VL53L1X.VL53L1X:
    sensor = VL53L1X.VL53L1X(i2c_bus=I2C_BUS, 
                             i2c_address=sensor_address, 
                             tca9548a_addr=multiplexer_address, 
                             tca9548a_num=multiplexer_channel)
    sensor.open()
    sensor.start_ranging(ranging_mode)

    return sensor


"""
    Handles closing sensor connection

    Parameters: sensor - The VL53L1X object of the sensor being shutdown
"""
def shutdown_sensor(sensor: VL53L1X.VL53L1X):
    sensor.close()


"""
    Handles initializing all sensors from the multiplexer then returns a list of initialized sensors,
    list is ordered by channel number of the multiplexer

    Parameters: ranging_mode - the ranging mode the sensor will be started in
"""
def initialize_all_sensors(ranging_mode: VL53L1X.VL53L1xDistanceMode = VL53L1X.VL53L1xDistanceMode.MEDIUM) -> list[VL53L1X.VL53L1X]:
    i2c = board.I2C()
    tca = adafruit_tca9548a.TCA9548A(i2c)

    sensor_list = []
    num_channels = 8

    # Initialize all sensors on multiplexer
    for channel in range(num_channels):
        lock_acquired = tca[channel].try_lock()
        
        # Scan channel to check for multiple addresses
        scan_list = tca[channel].scan() if lock_acquired else []

        if lock_acquired and len(scan_list) > 1:
            try:
                # Get current device address on channel
                current_address = scan_list[0]

                # Initialize sensor using address assigned to channel
                sensor = initialize_sensor(sensor_address=current_address,
                                           ranging_mode=ranging_mode,
                                           multiplexer_address=TCA9548A_ADDRESS,
                                           multiplexer_channel=channel)
                
                # Adjust addresses of sensors to communicate back on
                # 0x30 through 0x38 are safe addresses for this project
                address = 0x30 + (channel * 2)
                sensor.change_address(address)
                sensor.close()
                sensor_list.append(sensor)
            finally:
                tca[channel].unlock()
        elif lock_acquired:
            # If there isn't a device on that channel release the lock
            tca[channel].unlock()

    for sensor in sensor_list:
        sensor.open()
        sensor.start_ranging()
        
    return sensor_list


"""
    Handles shutting down all sensors in the sensor list

    Parameters: sensor_list - the list containing initliazed sensor objects
"""
def shutdown_all_sensors(sensor_list: list[VL53L1X.VL53L1X]):
    for item in sensor_list:
        shutdown_sensor(item)

