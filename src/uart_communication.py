import serial
from time import sleep
from datetime import timedelta, datetime
import config

default_uart = serial.Serial(config.uart_port)
default_uart.reset_input_buffer()
default_uart.reset_output_buffer()

def sendUARTMsg(message: str, uart: serial.Serial = default_uart):
    # Add the newline as a signal for the end of message
    msg = message + "\n"
    # Encode message and send
    uart.write(msg.encode())
    

def readUARTMsg(uart: serial.Serial = default_uart) -> str | None:
    try:
        if uart.readable() and uart.in_waiting > 0:
            received = uart.readline().decode().strip("\n")
            if received == "":
                return None
            return received
    except Exception as ex:
        print(ex)
        return None
    
    return None

# Data distance data is expected to be in csv format
def getDistanceData(uart: serial.Serial = default_uart) -> list | None:
    data = readUARTMsg(uart)

    if data is not None:
        data = data.split(",")
        data = [int(x) for x in data]

    return data

def parseObjMsg(message: str):
    return message.split(",")

def tmp(message: str, obj_dictionary: dict):
    current_time = datetime.now()
    # If word not in dict OR if it exists but enough seconds have passed
    if message not in obj_dictionary or current_time > (obj_dictionary[message] + timedelta(seconds=3)):
        obj_dictionary[message] = current_time

if __name__ == "__main__":
    while True:
        text = readUARTMsg()
        if text is not None:
            print(text)
        sleep(0.001)