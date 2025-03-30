import signal
from thread_workers import THREAD_KILL, handleCamera
from Camera import camera_init, detection_model_init, close_camera



def cleanup_processes(signum, frame):
    THREAD_KILL.set()
    close_camera()
    


def main():
    signal.signal(signal.SIGINT, cleanup_processes)
    signal.signal(signal.SIGTERM, cleanup_processes)

    try: 
        camera_init()
        detection_model_init()
        handleCamera()
    finally:
        close_camera()

        
if __name__ == "__main__":
    main()