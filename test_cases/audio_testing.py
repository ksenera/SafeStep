import os
import sys
import time
import signal
import multiprocessing

def restart(pid):
    """Wait a moment, terminate the main process, and restart it."""
    time.sleep(1)
    os.kill(pid, signal.SIGTERM)  # Terminate the process
    time.sleep(1)
    os.execv(sys.executable, ['python'] + sys.argv)  # Restart the program

def main():
    """Start a process that will restart this script."""
    pid = os.getpid()
    restartProcess = multiprocessing.Process(target=restart, args=(pid,))  # Corrected tuple
    restartProcess.start()

    # Simulate a main loop
    try:
        while True:
            print(f"Main process running (PID: {pid})")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down gracefully.")

if __name__ == '__main__':
    main()
