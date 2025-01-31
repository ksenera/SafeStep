import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import time, mixer

mixer.init()

def playAudioFile(audioFile: str) -> mixer.Channel:
    sound = mixer.Sound(audioFile)
    channel = sound.play()

    return channel

if __name__ == "__main__":
    mixer.init()
    test_sound = mixer.Sound("data/audio/test.wav")
    status = test_sound.play()

    while status.get_busy():
        time.wait(100)