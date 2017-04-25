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
configLoadComplete = [False,]


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


def process_keeper_function(configDict, scanTimeCycle=5, quitEvent=None):
    """
    守护用线程，用于重启和终止进程。
    :param configDict: 
    :param scanTimeCycle: 
    :param quitEvent: 
    :return: 
    """
    need_restart = configDict['need_restart']
    while quitEvent is not None and (not quitEvent.isSet()):
        black_list, white_list = [], []
        time.sleep(scanTimeCycle)
        if 'black_list' in configDict:
            black_list = configDict['black_list']
        if 'white_list' in configDict:
            white_list = configDict['white_list']
        for pName in black_list:
            process_keeper.process_killer_by_name(pName)
        # for pName in white_list:
        #     pass
        if need_restart:
            process_monitor.check_process_status_and_restart(configDict)


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
        configLoadComplete[0] = True
    except Exception as e:
        print("Configuration File Wrong!", e)
        sys.exit(-1)
    print("Configuration Load Complete.")

    process_monitor.monitor_init(configDict)

    t1 = threading.Thread(
        target=watcher
    )
    t2 = threading.Thread(
        target=process_keeper_function,
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
