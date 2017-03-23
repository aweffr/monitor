# -*- coding: utf-8 -*-

'''
功能：
从运行开始，每隔 X(s) 打印当前CPU的使用率，内存的使用率，当前目标进程线程数和使用率。
若监控的进程内存占用超过一定限值，终止并重启该进程。

version 0.1:
基于python3.6实现基本功能。
'''

import psutil
import time
import email_sender
import sys
from read_config import read_config
from subprocess import PIPE
from collections import deque

GLOBAL_DEBUG = True

MB_UNIT = 1024 * 1024
line_number = 1
p_memory_val = 0.0
global_memory = 0.0
cpu_status = 0.0


def getPidsByName(target_process_name):
    '''
    由目标进程的名字（字符串）获得进程id，以列表形式返回。
    '''
    pids = psutil.pids()
    id_list = []
    for pid in pids:
        try:
            if str(psutil.Process(pid).name()).lower() == target_process_name:
                id_list.append(pid)
        except Exception as e:
            print("Pid: " + str(pid) + "not found.")
    return id_list


def getCpuState(interval=1):
    """
    间隔1秒获得CPU的全局占用状态。以字符串形式返回
    """
    global cpu_status
    cpu_status = psutil.cpu_percent(interval)
    return cpu_status


def getMemoryState():
    """
    获得全局内存的占用状态。以字符串形式返回
    """
    global global_memory
    memory = psutil.virtual_memory()
    global_memory = memory.percent
    line = "Memory: %4s%% %6s/%s" % (
        memory.percent,
        str(memory.used // MB_UNIT) + "Mb",
        str(memory.total // MB_UNIT) + "Mb"
    )
    return memory.percent, memory.used / MB_UNIT, memory.total / MB_UNIT


def process_state(name, id_list, limit=50):
    """
    输入进程的名字，id列表。
    根据进程列表返回进程的状态（字符串）和是否超限的布尔值。
    """
    global p_memory_val
    if len(id_list) == 0:
        return "找不到进程:%s" % name, False
    lines = []
    lines.append("进程名称: %s    总进程数: %d    " % (name, len(id_list)))
    memory_cnt = 0.0
    for pid in id_list:
        try:
            p = psutil.Process(pid)
        except psutil.NoSuchProcess as e:
            print("Waring:", e)
            continue
        memory_cnt += p.memory_percent()
    p_memory_val = memory_cnt
    lines.append("内存占用: %.2f%%" % memory_cnt)
    memory_exceed = (memory_cnt > limit)
    return " ".join(lines), memory_exceed


def printLogFromDict(out_file, d):
    # 将单次扫描所得的结果（字典类型）写入文件。
    for key, value in d.items():
        out_file.writelines(key + " : " + value + "\n")


def print_recent_logs(out_file, queue):
    # 将最近的记录（大小由队列的长度限值决定）写入文件中。
    for d in queue:
        printLogFromDict(out_file, d)


def process_killer(target_process):
    id_list = getPidsByName(target_process)
    for pid in id_list:
        try:
            p = psutil.Process(pid)
            # if p.parent().name() == target_process:
            p.kill()
        except Exception as e:
            print("Warning", e)


def monitor(target_process, interval, log_file, email_context, email_length=25, memory_limit=50, shareQueue=None):
    global p_memory_val, global_memory
    target_process_name = target_process
    q = deque(maxlen=email_length)
    line_number = 0
    isExceed = False
    t1 = time.clock()

    with open(log_file, "w") as f:
        f.writelines("Logical CPU(s) number: %d\n" % psutil.cpu_count())
        while True:
            # log_temp为单次记录信息的项
            logTemoDict = dict()
            line_number += 1
            logTemoDict['LineNumber'] = str(line_number)
            # 时间
            logTemoDict['Time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            # 全局CPU和内存状态
            currentCpuState = getCpuState(interval=interval)
            currentMemoryPercent, currentMemoryUsed, currentMemoryTotal = getMemoryState()
            memoryLogString = "Memory: %4s%% %6s/%s" % (
                str(currentMemoryPercent),
                str(currentMemoryUsed) + "Mb",
                str(currentMemoryTotal) + "Mb"
            )
            logTemoDict['Global Status'] = "CPU:%s%%    %s" % (str(currentCpuState), memoryLogString)
            # 目标进程状态
            processIdList = getPidsByName(target_process_name)
            memoryString, isExceed = process_state(target_process_name, processIdList, memory_limit)
            logTemoDict['Target Process'] = memoryString
            if shareQueue is not None:
                shareQueue.append((line_number, currentCpuState, currentMemoryPercent, p_memory_val), )
                if GLOBAL_DEBUG:
                    print(shareQueue[-1])
            # 将本次记录项放入限长队列
            q.append(logTemoDict)
            if not isExceed:
                printLogFromDict(f, logTemoDict)
                f.flush()
            else:  # if isExceed
                t2 = time.clock()
                f.writelines("Total Running time: %.3f\n" % (t2 - t1))
                with open(email_context, "w") as send_file:
                    print_recent_logs(send_file, q)
                break
    return 0


def process_start(path):
    p = psutil.Popen([path, ], stdout=PIPE)
    return p


if __name__ == "__main__":
    # 找到QQ游览器的id process_id = "qqbrowser.exe"
    # time_interval = int(raw_input("输出间隔(s):"))
    try:
        d = read_config("config.conf")
    except Exception as e:
        print("Configation File Wrong!")
        sys.exit(0)
    print("Configation Load Complete. Start Monitor.")

    monitor(target_process=d["target_process"],
            interval=d["interval"],
            log_file=d["log_file"],
            email_context=d["email_context"],
            email_length=d["email_length"],
            memory_limit=d["memory_limit"]
            )

    email_sender.send_email(from_addr=d["from_addr"],
                            password=d["password"],
                            smtp_server=d["smtp_server"],
                            to_addr=d["to_addr"],
                            email_context=d["email_context"])

    # process_killer(target_process="qqbrowser.exe")
    # process_start("C:\Program Files (x86)\Tencent\QQBrowser\QQBrowser.exe")
