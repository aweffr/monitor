import psutil
from process_monitor import get_pids_by_name
from subprocess import PIPE

GLOBAL_DEBUG = 0


def process_killer(targetProcessName):
    idList = get_pids_by_name(targetProcessName)
    if GLOBAL_DEBUG:
        print "process_killer( %s)" % targetProcessName,
        print "idList: %s" % str(idList)
    for pid in idList:
        try:
            p = psutil.Process(pid)
            p.kill()
        except Exception as e:
            print("Warning", e)


def process_starter(path):
    p = psutil.Popen([path, ])
    return p


if __name__ == "__main__":
    pass
    # process_killer(target_process="qqbrowser.exe")
    # process_starter("C:\Program Files (x86)\Tencent\QQBrowser\QQBrowser.exe")
