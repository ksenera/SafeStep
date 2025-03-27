import signal
from thread_workers import THREAD_KILL, initialize_all, handleCamera, handleTOF, handleAudioFeedback, handleVibrationalFeedback
import threading
import asyncio


def cleanup_processes(signum, frame):
    THREAD_KILL.set()


def main():
    signal.signal(signal.SIGTSTP, cleanup_processes)

    initialize_all()

    t1 = threading.Thread(target=handleAudioFeedback)
    t2 = threading.Thread(target=handleTOF)
    t3 = threading.Thread(target=asyncio.run, args=((handleVibrationalFeedback()),))

    t1.start()
    t2.start()
    t3.start()

    # Wait for threads to finish running
    t1.join()
    t2.join()
    t3.join()

        
if __name__ == "__main__":
    main()
    # signal.signal(signal.SIGTSTP, cleanup_processes)
    # initialize_all()
    # handleCamera()
    # handleFeedback()

