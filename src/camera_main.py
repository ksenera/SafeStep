import signal
from thread_workers import THREAD_KILL, handleCamera
from Camera import camera_init, detection_model_init, close_camera
import sys


def cleanup_processes(signum, frame):
    THREAD_KILL.set()
    close_camera()
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, cleanup_processes)
    signal.signal(signal.SIGTERM, cleanup_processes)

    try: 
        camera_init()
        detection_model_init()
        handleCamera()
    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        close_camera()

        
if __name__ == "__main__":
    main()