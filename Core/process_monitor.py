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
import zipfile
import email_sender
import log_file_name
import sys
import threading
from read_config import read_config
from csv_writer import CsvWriter
from collections import deque
from pprint import pprint
from collections import OrderedDict

GLOBAL_DEBUG = False

MB_UNIT = 1024 * 1024


def get_pids_by_name(target_process_name):
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


def get_cpu_state(interval=1):
    """
    间隔interval秒获得CPU的全局占用状态。以字符串形式返回
    """
    return psutil.cpu_percent(interval)


def get_memory_state():
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


def need_to_switch(t1, t2, log_interval):
    if t1.tm_yday > t2.tm_yday:
        t2.tm_yday += 365
    return (t2.tm_yday - t1.tm_yday) > log_interval


def monitor(share_queue, quit_event, email_event, config_dict=dict()):
    try:
        target_process_name = config_dict["target_process"]
        interval = config_dict["interval"]
        log_path = config_dict["log_path"]
        email_context = config_dict["email_context"]
        email_length = config_dict["email_length"]
        memory_limit = config_dict["memory_limit"]
        log_interval = config_dict["log_interval"]
    except Exception as e:
        print "Error at configDict, monitor exit."
        sys.exit(-1)

    line_number = 0
    continueFlag = True
    emailMessageQueue = deque(maxlen=email_length)
    if log_interval == 7:
        log_opt = 'week'
    elif log_interval == 30:
        log_opt = 'month'
    else:
        log_opt = 'day'
    t1 = time.localtime()
    logFileName = log_file_name.log_file_name(opt=log_opt)
    csv_f = CsvWriter(logFileName, path=log_path)

    while continueFlag is True:
        # logTempDict 为单次记录信息的项
        td = OrderedDict()
        line_number += 1
        td['LineNumber'] = line_number
        # 时间
        td['Time'] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
        # 全局CPU和内存状态
        currentCpuState = get_cpu_state(interval=interval)
        td['CPU_percent'] = currentCpuState
        globalMemoryState = get_memory_state()
        td['memory_percent'], td['memory_used'], td['memory_total'] = globalMemoryState
        # 获取网络IO状态
        network_status = getNetworkState()
        td['bytes_sent'] = network_status.bytes_sent
        td['bytes_recv'] = network_status.bytes_recv
        td['packets_sent'] = network_status.packets_sent
        td['packets_recv'] = network_status.packets_recv
        # 目标进程状态
        shareProcessList = get_pids_by_name(target_process_name)
        processStatusDict, isExceed = process_state(target_process_name, shareProcessList, memory_limit)
        if processStatusDict['process_total_numbers'] > 0:
            td['process_name'] = processStatusDict['process_name']
            td['process_memory_occupied'] = processStatusDict['memory_occupied']
            td['process_total_numbers'] = processStatusDict['process_total_numbers']
            td['process_read_cnt'] = processStatusDict['p_read_cnt']
            td['process_write_cnt'] = processStatusDict['p_write_cnt']
        else:
            td['process_name'] = processStatusDict['process_name']
            td['process_memory_occupied'], td['process_total_numbers'], td['process_read_cnt'], td[
                'process_write_cnt'] = 0, 0, 0, 0

        if share_queue is not None:
            share_queue.append(
                (td['LineNumber'], td['CPU_percent'], td['memory_percent'], td['process_memory_occupied'])
            )

        # 将本次记录项放入限长队列
        emailMessageQueue.append(td)

        # ----------write dict to csv file----------------
        # print("Now writing at line: %d" % line_number)
        csv_f.dict_to_csv(td)
        t2 = time.localtime()

        if line_number % 120 == 0:
            csv_f.flush()

        if isExceed:
            try:
                csv_email_f = CsvWriter(email_context)
                csv_email_f.queue_dict_to_csv(emailMessageQueue)
                csv_email_f.close()
            except Exception as e:
                print("Error at generate Email file!", e)
            if email_event is None or not email_event.isSet():
                # print("email_event is None:", email_event is None)
                thd = threading.Thread(target=wrapped_email_sender,
                                       kwargs={'config_dict': config_dict, 'xls_format': True})
                # wrapped_email_sender(configDict=config_dict, xls_format=True)
                thd.run()
                if email_event is not None:
                    email_event.set()
        if quit_event is not None and quit_event.isSet():
            continueFlag = False  # <==> break
            csv_f.close()
        if need_to_switch(t1, t2, log_interval):
            fName = csv_f.filename
            csv_f.close()
            zipTheOldFile(fName.replace("csv", "zip"), fName, log_path)
            t1 = t2  # Update t1
            logFileName = log_file_name.log_file_name(opt=log_opt)
            csv_f = CsvWriter(logFileName, path=log_path)
    return 0


def zipTheOldFile(zipFileName, logFileName, path):
    try:
        with zipfile.ZipFile(path + zipFileName, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(path + logFileName)
    except Exception as e:
        print "Error: cannot zip current log: %s" % logFileName
        print e
    try:
        os.remove(path + logFileName)
    except Exception as e:
        print("Wrong at remove zipped log file.!", e)


def wrapped_email_sender(config_dict=dict(), xls_format=False):
    try:
        if xls_format:
            email_context = config_dict["email_context"].replace('txt', 'csv')
        else:
            email_context = config_dict["email_context"]

        email_sender.send_email(
            from_addr=config_dict["from_addr"],
            password=config_dict["password"],
            smtp_server=config_dict["smtp_server"],
            to_addr=config_dict["to_addr"],
            email_context=email_context,
            xls_format=xls_format)
    except Exception as e:
        print(e)

    print("Waring Email Sent!", "To addr: {addr}".format(**{'addr': config_dict["to_addr"]}))


if __name__ == "__main__":
    # 找到QQ游览器的id process_id = "qqbrowser.exe"
    # time_interval = int(raw_input("输出间隔(s):"))
    import os
    from MonitorMain import shareQueue, quitEvent, emailEvent
    os.chdir('..')
    try:
        keywordDict = read_config('config.conf')
    except Exception as e:
        print("Configuration File Wrong!")
        sys.exit(-1)
    print("Configuration Load Complete. Start Monitor.")

    monitor(shareQueue, quitEvent, emailEvent, config_dict=keywordDict)
