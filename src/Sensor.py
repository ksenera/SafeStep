import VL53L1X

# The I2C bus for external devices connected to the pi
I2C_BUS = 1

"""
    Opens the sensor up for communication and begins ranging

    Parameters: sensor_address - The address of the sensor (ex. 0x29)
                ranging_mode - The ranging mode as a string ('SHORT', 'MEDIUM', or 'LONG')
"""
def initialize_sensor(sensor_address: int, ranging_mode: str) -> VL53L1X:
    mode = {
        "SHORT": 1,
        "MEDIUM": 2,
        "LONG": 3
    }

    if mode.get(ranging_mode) is None:
        raise Exception("Unknown ranging mode")

    tof = VL53L1X.VL53L1X(i2c_bus=I2C_BUS, i2c_address=sensor_address)
    tof.open()
    tof.start_ranging(mode.get(ranging_mode))

    return tof