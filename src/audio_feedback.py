import queue
from threading import Thread, Event
import time
import pyttsx3
import subprocess

engine = pyttsx3.init()
categories = ["low Furniture", "high Furniture", "doorways"]
event = Event()

AUDIO_QUEUE = queue.Queue(maxsize=1)

def pushAudioMessage(message: str):
    #while not AUDIO_QUEUE.empty():
        #AUDIO_QUEUE.get_nowait()
    AUDIO_QUEUE.put(message)

def getNextAudioMessage():
    if AUDIO_QUEUE.empty():
        return None
    return AUDIO_QUEUE.get()

def addToQueue(queue:queue.Queue):
    for i in range(1):
        for i in categories:
            queue.put(i)


def playaudio(queue: queue.Queue):
    previousText = None

    while True:
        if queue.empty():
            continue

        text = queue.get()

        if text != previousText or previousText is None:
            previousText = text

        if queue.empty():
            break


async def speak(text):
    subprocess.run(["flite", "-voice", "rms", "-t", text])
