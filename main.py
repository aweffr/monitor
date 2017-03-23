from collections import deque
import sys

sys.path.extend(["./Core", "./GUI"])
import process_watcher
import email_sender
import threading, time
import read_config
from PyQt5.QtWidgets import QApplication
import plot


def watcher(configDict, shareQueue=None):
    process_watcher.monitor(
        target_process=configDict["target_process"],
        interval=configDict["interval"],
        log_file=configDict["log_file"],
        email_context=configDict["email_context"],
        email_length=configDict["email_length"],
        memory_limit=configDict["memory_limit"],
        shareQueue=shareQueue
    )

    email_sender.send_email(from_addr=configDict["from_addr"],
                            password=configDict["password"],
                            smtp_server=configDict["smtp_server"],
                            to_addr=configDict["to_addr"],
                            email_context=configDict["email_context"])
    return 0


def GUI(shareQueue=None):
    app = QApplication(sys.argv)
    mainWindow = plot.PlotFrame(width=6, height=3, shareQueue=shareQueue)
    mainWindow.show()
    app.exec_()


if __name__ == "__main__":
    shareQueue = deque(maxlen=25)
    configDict = read_config.read_config("./config.conf")
    t1 = threading.Thread(target=watcher, kwargs={"configDict": configDict, "shareQueue": shareQueue})
    t2 = threading.Thread(target=GUI, kwargs={"shareQueue": shareQueue})
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print("Exit!")
