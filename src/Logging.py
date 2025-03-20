import os
import sys
import time
import signal
import multiprocessing
import subprocess

def restart(pid):
    time.sleep(1)
    os.kill(pid, signal.SIGTERM)
    time.sleep(1)
    #os.execv(sys.executable, ['python'] + sys.argv)
    os.execv("C:\\Windows\\System32\\cmd.exe", ["cmd.exe", "/c", "start", "python", sys.argv[0]])
    #subprocess.Popen(["start", "cmd", "/k", sys.executable, "Logging.py"], shell=True)


def main():
    pid = os.getpid()
    restartProcess = multiprocessing.Process(target=restart, args=(pid,))
    restartProcess.start()
    print(f"(PID: {pid})")
    time.sleep(1)

if __name__ == '__main__':
    main()
