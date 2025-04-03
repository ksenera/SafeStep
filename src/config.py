import argparse

parser = argparse.ArgumentParser(description="Livestream_toggler")
parser.add_argument("--livestream", action="store_true", default=False)
livestream = parser.parse_args().livestream


default_pin_list = [
    18,
    24,
    25
]

min_vibration_time = 0.2

max_vibration_time = 1.5

thread_delay = 0.1

model_name = "../efficientdet.tflite"

inner_range = 500

outer_range = 3000

uart_port = "/dev/ttyS0"
# in seconds
message_repeat_delay = 5