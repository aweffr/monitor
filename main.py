from collections import deque
import sys
sys.path.extend(["./Core", "./GUI"])
import process_watcher
import process_keeper
import threading, time
import read_config
from PyQt5.QtWidgets import QApplication
import MonitorGUI


# TODO: 定制邮件发送的（频次）参数

def watcher(configDict, shareQueue=None, shareEvent=None):
    process_watcher.monitor(
        target_process=configDict["target_process"],
        interval=configDict["interval"],
        log_path=configDict["log_path"],
        email_context=configDict["email_context"],
        email_length=configDict["email_length"],
        memory_limit=configDict["memory_limit"],
        log_interval=configDict["log_interval"],
        shareQueue=shareQueue,
        quitEvent=shareEvent,
        keywordDict=configDict
    )


def GUI(configDict, shareQueue=None, shareEvent=None):
    app = QApplication(sys.argv)
    mainWindow = MonitorGUI.PlotFrame(
        width=6, height=3, shareQueue=shareQueue,
        processMemoryLimit=configDict["memory_limit"],
        shareEvent=shareEvent)
    mainWindow.show()
    app.exec_()


def processKeeper(configDict, scanTimeCycle=5, shareEvent=None):
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
        if shareEvent.isSet():
            break


if __name__ == "__main__":
    shareQueue = deque(maxlen=25)
    try:
        configDict = read_config.read_config("./config.conf")
    except Exception as e:
        print("Configuration File Wrong!", e)
        sys.exit(-1)
    print("Configuration Load Complete. Start Monitor.")

    e = threading.Event()
    t1 = threading.Thread(target=watcher,
                          kwargs={"configDict": configDict, "shareQueue": shareQueue,
                                  "shareEvent": e})
    t2 = threading.Thread(target=GUI,
                          kwargs={"configDict": configDict, "shareQueue": shareQueue,
                                  "shareEvent": e})
    t3 = threading.Thread(target=processKeeper, kwargs={"configDict": configDict,
                                                        "scanTimeCycle": 5,
                                                        "shareEvent": e})
    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()
    # input("Press any key to exit!")
