from collections import deque
import sys

sys.path.extend(["./Core", "./GUI"])
import process_watcher
import email_sender
import threading, time
import read_config
from PyQt5.QtWidgets import QApplication
import plot

q = deque(maxlen=25)


def watcher(d):
    global q
    process_watcher.monitor(
        target_process=d["target_process"],
        interval=d["interval"],
        log_file=d["log_file"],
        email_context=d["email_context"],
        email_length=d["email_length"],
        memory_limit=d["memory_limit"],
        q_data=q
    )

    email_sender.send_email(from_addr=d["from_addr"],
                            password=d["password"],
                            smtp_server=d["smtp_server"],
                            to_addr=d["to_addr"],
                            email_context=d["email_context"])
    return 0


def GUI():
    global q
    app = QApplication(sys.argv)
    mainWindow = plot.PlotFrame(width=6, height=3, data_q=q)
    mainWindow.show()
    app.exec_()


if __name__ == "__main__":
    d = read_config.read_config("./config.conf")
    t1 = threading.Thread(target=watcher, args=[d, ])
    t2 = threading.Thread(target=GUI)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print("Exit!")
