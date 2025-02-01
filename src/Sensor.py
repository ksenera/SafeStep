import VL53L1X

tof = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
tof.open()

tof.start_ranging(1)

while True:
    distance_in_mm = tof.get_distance()
    print(f"Distance: {distance_in_mm} mm")

tof.stop_ranging()