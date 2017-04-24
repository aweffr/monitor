# coding=utf-8

from collections import deque
import sys

sys.path.extend(["./Core", ])
import process_monitor
import email_sender
import process_keeper
import threading
import read_config
import time

shareQueue = deque(maxlen=100)
quitEvent = threading.Event()
emailEvent = threading.Event()
shareProcessList = list()
configDict = dict()
configLoadComplete = False


def watcher():
    global configDict, shareQueue, quitEvent, emailEvent
    assert configDict is not None
    assert shareQueue is not None
    assert quitEvent is not None
    assert emailEvent is not None
    process_monitor.monitor(
        share_queue=shareQueue,
        quit_event=quitEvent,
        config_dict=configDict,
        email_event=emailEvent
    )


def processKeeper(configDict, scanTimeCycle=10, quitEvent=None):
    if 'black_list' not in configDict and 'white_list' not in configDict \
            and 'need_restart' not in configDict:
        return

    need_restart = configDict['need_restart']
    if need_restart:
        process_name = configDict['process_name']
        path_list = configDict['restart_path']
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
        if need_restart:
            need_restart_list = process_monitor.check_process_by_path(path_list)
            if len(need_restart_list) > 0:
                restart_procedure(configDict, need_restart_list)


def restart_procedure(configDict, need_restart_list):
    emailFilePath = configDict["log_path"] + "restart_email_context.txt"
    f = open(emailFilePath, "w")
    f.writelines(
        "Process has been shutdown: {process_name}, now restart at {time}. \n\
        target process path: {restart_path}".format(**{
            "process_name": configDict['process_name'],
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "restart_path": str(need_restart_list)}))
    f.close()
    email_sender.send_email(from_addr=configDict["from_addr"],
                            password=configDict["password"],
                            smtp_server=configDict["smtp_server"],
                            to_addr=configDict["to_addr"],
                            email_context=emailFilePath)
    for path in need_restart_list:
        try:
            process_keeper.process_starter(path)
        except Exception as e:
            print(e)
    if "restart_interval" in configDict:
        time.sleep(configDict["restart_interval"])


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


def run():
    global quitEvent, emailEvent, shareQueue, configDict, configLoadComplete
    try:
        configDict = read_config.read_config("./config.conf")
        configLoadComplete = True
    except Exception as e:
        print("Configuration File Wrong!", e)
        sys.exit(-1)
    print("Configuration Load Complete.")

    t1 = threading.Thread(
        target=watcher
    )
    t2 = threading.Thread(
        target=processKeeper,
        kwargs={"configDict": configDict,
                "scanTimeCycle": 10,
                "quitEvent": quitEvent}
    )
    t3 = threading.Thread(
        target=emailSenderReset,
        kwargs={"configDict": configDict,
                "emailEvent": emailEvent,
                "quitEvent": quitEvent}
    )
    thread_lst = [t1, t2, t3]
    for t in thread_lst:
        t.start()
    print("Succeed: Start Monitor.")


if __name__ == "__main__":
    run()
    # shareQueue = deque(maxlen=100)
    # shareProcessList = list()
    # try:
    #     configDict = read_config.read_config("./config.conf")
    # except Exception as quitEvent:
    #     print("Configuration File Wrong!", quitEvent)
    #     sys.exit(-1)
    # print("Configuration Load Complete. Start Monitor.")
    #
    # quitEvent = threading.Event()
    # emailEvent = threading.Event()
    # t1 = threading.Thread(
    #     target=watcher,
    #     kwargs={"configDict": configDict, "shareQueue": shareQueue,
    #             "quitEvent": quitEvent, "emailEvent": emailEvent}
    # )
    # t2 = threading.Thread(
    #     target=processKeeper,
    #     kwargs={"configDict": configDict,
    #             "scanTimeCycle": 10,
    #             "quitEvent": quitEvent}
    # )
    # t3 = threading.Thread(
    #     target=emailSenderReset,
    #     kwargs={"configDict": configDict,
    #             "emailEvent": emailEvent,
    #             "quitEvent": quitEvent}
    # )
    # thread_lst = [t1, t2, t3]
    # for t in thread_lst:
    #     t.start()
    # # -------------------DEBUG----------------------
    # if False:
    #     while not quitEvent.isSet():
    #         for t in thread_lst:
    #             print(t.getName(), "is_alive:", t.is_alive())
    #         time.sleep(5)
    #     if quitEvent.isSet():
    #         for t in thread_lst:
    #             print(t.getName(), "is_alive:", t.is_alive())
    # # -----------------DEBUG END--------------------
    # t1.join()
    # t2.join()
    # t3.join()
    # print("Exit!")
    # sys.exit(0)
    # # input("Press any key to exit!")
