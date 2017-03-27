# -*- coding: utf-8 -*-

'''
功能：
从运行开始，每隔 X(s) 打印当前CPU的使用率，内存的使用率，当前目标进程线程数和使用率。
若监控的进程内存占用超过一定限值，终止并重启该进程。

version 0.1:
基于python3.6实现基本功能。
'''
from subprocess import PIPE
import psutil
import time
import email_sender
import log_file_name
import sys
from read_config import read_config
from collections import deque
from pprint import pprint

GLOBAL_DEBUG = False

MB_UNIT = 1024 * 1024


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
    return psutil.cpu_percent(interval)


def getMemoryState():
    """
    获得全局内存的占用状态。以字符串形式返回
    """
    memory = psutil.virtual_memory()
    globalMemoryState = memory.percent, memory.used // MB_UNIT, memory.total // MB_UNIT
    return globalMemoryState


def globalMemoryStateToString(globalMemoryState):
    currentMemoryPercent, currentMemoryUsed, currentMemoryTotal = globalMemoryState
    memoryLogString = "Memory: %4s%% %6s/%s" % (
        str(currentMemoryPercent),
        str(currentMemoryUsed) + "Mb",
        str(currentMemoryTotal) + "Mb"
    )
    return memoryLogString


def getNetworkState():
    """
    获得全局网络IO状态
    :return: 类字典对象‘snetio’, 属性有'bytes_recv', 'bytes_sent', 'packets_recv', 'packets_sent'
    """
    io_state = psutil.net_io_counters()
    return io_state


def netWorkStateToString(io_state):
    outString = "(全局) 发送字节数:%d    接受字节数:%d    发送包数:%d    接受包数:%d" % (
        io_state.bytes_sent, io_state.bytes_recv, io_state.packets_sent, io_state.packets_recv
    )
    return outString


def process_state(name, id_list, limit=50):
    """
    输入进程的名字，id列表。
    根据进程列表返回进程的状态（字符串）和是否超限的布尔值。
    """
    if len(id_list) == 0:
        processStatusDict = {
            "process_name": name,
            "process_total_numbers": 0,
            "memory_occupied": 0}
        return processStatusDict, False
    memory_cnt = 0.0
    io_read_cnt = 0
    io_write_cnt = 0
    for pid in id_list:
        try:
            p = psutil.Process(pid)
        except psutil.NoSuchProcess as e:
            print("Waring:", e)
            continue
        memory_cnt += p.memory_percent()
        io_read_cnt += p.io_counters().read_count
        io_write_cnt += p.io_counters().write_count

    memory_exceed = (memory_cnt > limit)
    processStatusDict = {
        "process_name": name,
        "memory_occupied": memory_cnt,
        "process_total_numbers": len(id_list),
        "p_read_cnt": io_read_cnt,
        "p_write_cnt": io_write_cnt
    }
    return processStatusDict, memory_exceed


def processStatusToString(statusDict):
    if GLOBAL_DEBUG:
        pprint(statusDict)
    if statusDict["process_total_numbers"] == 0:
        return "找不到进程: %s" % statusDict["process_name"]
    lines = ["进程名称: %s    总进程数: %d    " % (statusDict["process_name"], statusDict["process_total_numbers"]),
             "内存占用: %.2f%%\n" % statusDict["memory_occupied"],
             "IO信息：    read:%d    write:%d" % (statusDict["p_read_cnt"], statusDict["p_write_cnt"])]
    return " ".join(lines)


def printLogFromDict(out_file, d):
    # 将单次扫描所得的结果（字典类型）写入文件。
    for key, value in d.items():
        out_file.writelines(key + " : " + value + "\n")


def print_recent_logs(out_file, queue):
    # 将最近的记录（大小由队列的长度限值决定）写入文件中。
    for d in queue:
        printLogFromDict(out_file, d)


def need_to_switch(t1, t2, log_interval):
    if t1.tm_yday > t2.tm_yday:
        t2.tm_yday += 365
    return (t2.tm_yday - t1.tm_yday) > log_interval


def monitor(target_process, interval, log_path,
            email_context, email_length=25,
            memory_limit=50, shareQueue=None,
            quitEvent=None,
            keywordDict=dict(),
            log_interval=7):
    target_process_name = target_process
    emailMessageQueue = deque(maxlen=email_length)
    line_number = 0
    emailSent = False
    continueFlag = True
    monitorStartTime = time.clock()
    t1 = time.localtime()
    logFileName = time.strftime("%Y-%m-%d.txt", time.localtime())
    f = open(log_path + logFileName, 'w')
    while continueFlag is True:
        f.writelines("Logical CPU(s) number: %d\n" % psutil.cpu_count())
        # log_temp为单次记录信息的项
        logTempDict = dict()
        line_number += 1
        logTempDict['LineNumber'] = str(line_number)
        # 时间
        logTempDict['Time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # 全局CPU和内存状态
        currentCpuState = getCpuState(interval=interval)
        globalMemoryState = getMemoryState()
        logTempDict['Global Status'] = "CPU:%s%%    %s" % (
            str(currentCpuState), globalMemoryStateToString(globalMemoryState)
        )
        # 获取网络IO状态
        network_status = getNetworkState()
        logTempDict['NetworkStatus'] = netWorkStateToString(network_status)
        # 目标进程状态
        processIdList = getPidsByName(target_process_name)
        processStatusDict, isExceed = process_state(target_process_name, processIdList, memory_limit)
        logTempDict['Target Process'] = processStatusToString(processStatusDict)
        if shareQueue is not None:
            shareQueue.append(
                (line_number, currentCpuState, globalMemoryState[0], processStatusDict["memory_occupied"]),
            )
            if GLOBAL_DEBUG:
                print("DEBUG:", shareQueue[-1])
        # 将本次记录项放入限长队列
        emailMessageQueue.append(logTempDict)
        monitorEndTime = time.clock()
        t2 = time.localtime()
        if not isExceed:
            printLogFromDict(f, logTempDict)
            # 不主动flush日志，减轻磁盘负担
            if GLOBAL_DEBUG or (line_number % 60 == 0):
                f.flush()
        else:  # if isExceed
            f.writelines("Total Running time: %.3f\n" % (monitorEndTime - monitorStartTime))
            with open(email_context, "w") as send_file:
                print_recent_logs(send_file, emailMessageQueue)
            if not emailSent:
                wrapped_email_sender(keywordDict=keywordDict)
                print("Waring Email Sent!")
                emailSent = True
        if quitEvent != None and quitEvent.isSet():
            continueFlag = False  # <==> break
        if need_to_switch(t1, t2, log_interval):
            f.close()
            logFileName = time.strftime("%Y-%m-%d.txt", time.localtime())
            f = open(log_path + logFileName, 'w')
    return 0


def process_start(path):
    p = psutil.Popen([path, ], stdout=PIPE)
    return p


def wrapped_email_sender(keywordDict=dict()):
    try:
        email_sender.send_email(from_addr=keywordDict["from_addr"],
                                password=keywordDict["password"],
                                smtp_server=keywordDict["smtp_server"],
                                to_addr=keywordDict["to_addr"],
                                email_context=keywordDict["email_context"], )
    except Exception as e:
        print(e)
        return


if __name__ == "__main__":
    # 找到QQ游览器的id process_id = "qqbrowser.exe"
    # time_interval = int(raw_input("输出间隔(s):"))
    configFile = r"C:\Users\aweff\Documents\01.Intern\Moniter\config.conf"
    try:
        keywordDict = read_config(configFile)
    except Exception as e:
        print("Configuration File Wrong!")
        sys.exit(-1)
    print("Configuration Load Complete. Start Monitor.")

    monitor(target_process=keywordDict["target_process"],
            interval=keywordDict["interval"],
            log_path=keywordDict["log_path"],
            email_context=keywordDict["email_context"],
            email_length=keywordDict["email_length"],
            memory_limit=keywordDict["memory_limit"],
            log_interval=keywordDict["log_interval"],
            keywordDict=keywordDict
            )

    # email_sender.send_email(from_addr=keywordDict["from_addr"],
    #                         password=keywordDict["password"],
    #                         smtp_server=keywordDict["smtp_server"],
    #                         to_addr=keywordDict["to_addr"],
    #                         email_context=keywordDict["email_context"])
