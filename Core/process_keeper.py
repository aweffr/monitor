import psutil
from subprocess import PIPE

GLOBAL_DEBUG = 0


def process_killer_by_name(target_process_name):
    """
    kill process by process name.
    :param target_process_name: string
    :return: None 
    """
    proc_name = target_process_name.lower()
    for proc in psutil.process_iter():
        if proc.name().lower() == proc_name:
            try:
                proc.terminate()
            except Exception as e:
                print("Fail at process_killer_by_name()", e)


if __name__ == "__main__":
    pass
    # process_killer(target_process="qqbrowser.exe")
    # process_starter("C:\Program Files (x86)\Tencent\QQBrowser\QQBrowser.exe")
