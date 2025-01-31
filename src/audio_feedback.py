import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import mixer

mixer.init()

"""
    Description: Takes an audio file then plays the audio and returns 
        the channel the audio is played on

    Parameters: audioFile - The path to the audio file
                infiniteLoop - A boolean representing if the audio should infinitely loop
"""
def playAudioFile(audioFile: str, infiniteLoop: bool = False) -> mixer.Channel:
    loop = -1 if infiniteLoop else 0

    sound = mixer.Sound(audioFile)
    channel = sound.play(loop)

    return channel
