from collections import deque
import sys

sys.path.extend(["./Core", "./GUI"])
import process_monitor
import process_keeper
import threading
import read_config
from PyQt5.QtWidgets import QApplication
import MonitorGUI
import time


def watcher(configDict, shareQueue=None, quitEvent=None, emailEvent=None):
    process_monitor.monitor(
        target_process=configDict["target_process"],
        interval=configDict["interval"],
        log_path=configDict["log_path"],
        email_context=configDict["email_context"],
        email_length=configDict["email_length"],
        memory_limit=configDict["memory_limit"],
        log_interval=configDict["log_interval"],
        shareQueue=shareQueue,
        quitEvent=quitEvent,
        keywordDict=configDict,
        emailEvent=emailEvent
    )


def GUI(configDict, shareQueue=None, quitEvent=None):
    app = QApplication(sys.argv)
    mainWindow = MonitorGUI.PlotFrame(
        width=6, height=3, shareQueue=shareQueue,
        processMemoryLimit=configDict["memory_limit"],
        quitEvent=quitEvent)
    mainWindow.show()
    app.exec_()


def processKeeper(configDict, scanTimeCycle=10, quitEvent=None):
    if 'black_list' not in configDict and 'white_list' not in configDict \
            and 'need_restart' not in configDict:
        return
    # 有白名单和黑名单，进入名单监控循环。
    need_restart = configDict['need_restart']
    if need_restart:
        process_name = configDict['process_name']
    while quitEvent is not None and (not quitEvent.isSet()):
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
        if need_restart and len(process_monitor.getPidsByName(process_name)) == 0:
            process_keeper.process_starter(configDict['restart_path'])



def emailSenderReset(configDict, emailEvent, quitEvent=None):
    while quitEvent is not None and (not quitEvent.isSet()):
        if emailEvent.isSet():
            t1 = time.time()
            while time.time() - t1 < configDict['send_interval']:
                time.sleep(30)
                emailEvent.clear()
                break
        else:
            time.sleep(30)

if __name__ == "__main__":
    shareQueue = deque(maxlen=25)
    shareProcessList = list()
    try:
        configDict = read_config.read_config("./config.conf")
    except Exception as quitEvent:
        print("Configuration File Wrong!", quitEvent)
        sys.exit(-1)
    print("Configuration Load Complete. Start Monitor.")

    quitEvent = threading.Event()
    emailEvent = threading.Event()
    t1 = threading.Thread(target=watcher,
                          kwargs={"configDict": configDict, "shareQueue": shareQueue,
                                  "quitEvent": quitEvent, "emailEvent": emailEvent})
    t2 = threading.Thread(target=GUI,
                          kwargs={"configDict": configDict, "shareQueue": shareQueue,
                                  "quitEvent": quitEvent})
    t3 = threading.Thread(target=processKeeper, kwargs={"configDict": configDict,
                                                        "scanTimeCycle": 10,
                                                        "quitEvent": quitEvent})
    t4 = threading.Thread(target=emailSenderReset, kwargs={"configDict": configDict,
                                                           "emailEvent": emailEvent,
                                                           "quitEvent": quitEvent})
    thread_lst = [t1, t2, t3, t4]
    for t in thread_lst:
        t.start()
    # -------------------DEBUG----------------------
    while not quitEvent.isSet():
        for t in thread_lst:
            print(t.getName(), "is_alive:", t.is_alive())
        time.sleep(5)
    if quitEvent.isSet():
        for t in thread_lst:
            print(t.getName(), "is_alive:", t.is_alive())
    # -----------------DEBUG END--------------------
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    print("Exit!")
    sys.exit(0)
    # input("Press any key to exit!")
