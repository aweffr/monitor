from collections import deque
import sys

sys.path.extend(["./Core", "./GUI"])
import process_watcher
import process_keeper
import email_sender
import threading, time
import read_config
from PyQt5.QtWidgets import QApplication
import MonitorGUI


def watcher(configDict, shareQueue=None):
    process_watcher.monitor(
        target_process=configDict["target_process"],
        interval=configDict["interval"],
        log_file=configDict["log_file"],
        email_context=configDict["email_context"],
        email_length=configDict["email_length"],
        memory_limit=configDict["memory_limit"],
        shareQueue=shareQueue,
        keywordDict=configDict
    )

    # email_sender.send_email(from_addr=configDict["from_addr"],
    #                         password=configDict["password"],
    #                         smtp_server=configDict["smtp_server"],
    #                         to_addr=configDict["to_addr"],
    #                         email_context=configDict["email_context"])
    return 0


def GUI(configDict, shareQueue=None):
    app = QApplication(sys.argv)
    mainWindow = MonitorGUI.PlotFrame(
        width=6, height=3, shareQueue=shareQueue,
        processMemoryLimit=configDict["memory_limit"])
    mainWindow.show()
    app.exec_()


def processKeeper(configDict, scanTimeCycle=5):
    while True:
        blackList, whiteList = [], []
        time.sleep(scanTimeCycle)
        if 'black_list' in configDict:
            blackList = configDict['black_list']
        if 'white_list' in configDict:
            whiteList = configDict['white_list']
        for pName in blackList:
            process_keeper.process_killer(pName)
        for pName in whiteList:
            pass


if __name__ == "__main__":
    shareQueue = deque(maxlen=25)
    try:
        configDict = read_config.read_config("./config.conf")
    except Exception as e:
        print("Configuration File Wrong!", e)
        sys.exit(-1)
    print("Configuration Load Complete. Start Monitor.")

    t1 = threading.Thread(target=watcher, kwargs={"configDict": configDict, "shareQueue": shareQueue})
    t2 = threading.Thread(target=GUI, kwargs={"configDict": configDict, "shareQueue": shareQueue})
    t3 = threading.Thread(target=processKeeper, kwargs={"configDict": configDict,
                                                        "scanTimeCycle": 5})
    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()
    print("Exit!")
