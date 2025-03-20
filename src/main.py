import os
import signal

from thread_workers import THREAD_KILL, initialize_all, handleCamera, handleTOF, handleFeedback
import threading
import asyncio
import time
import json

with open('settings.json', 'r') as file:
    config = json.load(file)


debug = config['debug']

def cleanup_processes(signum = None, frame = None):
    THREAD_KILL.set()


def error_restart(pid):
    cleanup_processes()

    time.sleep(5)

    os.kill(pid, signal.SIGTERM)


def main():
    signal.signal(signal.SIGTSTP, cleanup_processes)

    pid = os.getpid()
    initialize_all()

    t1 = threading.Thread(target=handleCamera)
    t2 = threading.Thread(target=handleTOF)
    t3 = threading.Thread(target=asyncio.run(handleFeedback))

    t1.start()
    t2.start()
    t3.start()

    # Wait for threads to finish running
    t1.join()
    t2.join()
    t3.join()

        
if __name__ == "__main__":
    main()
