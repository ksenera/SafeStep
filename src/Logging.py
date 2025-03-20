import os
import sys
import time
import signal
import multiprocessing
import subprocess
import psutil

def restart(pid):
    time.sleep(10)
    print(f"Killing process {pid}")
    time.sleep(2)
    os.kill(pid, signal.SIGKILL)
    # time.sleep(1)
    os.execv(f"/usr/bin/lxterminal",["lxterminal", f"--command=\"/usr/bin/bash | python3 {sys.argv[0]}\""])
    os.exec('kill -SIGKILL $BASHPID')
    #os.execv(sys.executable, ['python'] + sys.argv)
    #subprocess.Popen(["start", "cmd", "/k", sys.executable, "Logging.py"], shell=True)

def restart_program():
    """Restarts the current program, with file objects and descriptors
       cleanup
    """

    try:
        p = psutil.Process(os.getpid())
        for handler in p.get_open_files() + p.connections():
            os.close(handler.fd)
    except Exception:
        print('Exception caught')

    python = sys.executable
    os.execl(python, python, *sys.argv)


def main():
    pid = os.getpid()
    # restartProcess = multiprocessing.Process(target=restart, args=(pid,))
    restartProcess = multiprocessing.Process(target=restart_program)

    print(f"(PID: {pid})")
    restartProcess.start()
    while True:
        print("Sleeping for 5 seconds")
        time.sleep(5)

if __name__ == '__main__':
    main()
