import serial
from time import sleep

default_uart = serial.Serial("/dev/serial0")

print(default_uart.is_open)

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
        data = data.decode()
        data = data.split(",")

    return data

if __name__ == "__main__":
    while True:
        text = readUARTMsg()
        if text is not None:
            print(text)
        sleep(0.001)