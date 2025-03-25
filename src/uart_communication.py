import serial

default_uart = serial.Serial("/dev/serial0", timeout=1)

def sendUARTMsg(message: str, uart: serial.Serial = default_uart):
    # Add the newline as a signal for the end of message
    msg = message + "\n"
    # Encode message and send
    uart.write(msg.encode())
    

def readUARTMsg(uart: serial.Serial = default_uart) -> str | None:
    if uart.readable():
        received = uart.readline().decode()
        if received == "":
            return None
        return received
    
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