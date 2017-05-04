# -*- coding: utf-8 -*-
from __future__ import print_function

'''
功能：
从运行开始，每隔 X(s) 打印当前CPU的使用率，内存的使用率，当前目标进程线程数和使用率。
若监控的进程内存占用超过一定限值，终止并重启该进程。

version 1.0:
精细初始化
'''
import psutil
from psutil import STATUS_ZOMBIE, STATUS_DEAD, STATUS_STOPPED
import time
from copy import copy
import zipfile
import log_file_name
import sys
import threading
import email_sender
from read_config import read_config
from csv_writer import CsvWriter
from collections import deque, OrderedDict
from subprocess import PIPE

GLOBAL_DEBUG = False

target_init_process_dict = {}
target_running_process_dict = {}
alive_dict = {}

MB_UNIT = 1024 * 1024
KB_UNIT = 1024


def parse_proc_id_tomcat(cwd):
    """
    cwd是tomcat的当前工作目录
    :param cwd: 
    :return: 
    """
    print("parse_proc_id_tomcat, cwd=", cwd)
    assert isinstance(cwd, str)
    assert cwd.lower().find("tomcat") != -1
    if cwd.find("bin") != -1:
        return cwd[:cwd.lower().find("bin")].rstrip("\\").rstrip("/")
    else:
        return cwd.rstrip("\\").rstrip("/")


class ProcDao(object):
    def __init__(self, proc):
        self.is_jar = False
        self.is_tomcat = False
        self.proc_uid = None
        self.pid = proc.pid
        self.process_bind = proc
        self.name = proc.name()
        self.cmdline = proc.cmdline()
        self.exe = proc.exe()
        self.cwd = proc.cwd()
        self.regularization()

    def get_proc_uid(self):
        return self.proc_uid

    def __hash__(self):
        return hash(self.pid) + hash(self.name)

    def __eq__(self, other):
        if type(self) == type(other):
            return self.__hash__() == other.__hash__()

    def __str__(self):
        return "%s: %d, path=%s" % (self.name, self.pid, str(self.proc_uid))

    def regularization(self):
        """
        确定本进程跟踪的是直接启动的jar包还是tomcat。
        如果是jar包，将jar包设置为绝对路径，并将jar包的绝对路径作为uid
        如果是tomcat,解析tmocat的根目录，并将tomcat的根目录作为uid
        :return: 
        """
        for params in self.cmdline:
            if params.find('-jar') != -1:
                self.is_jar = True
                break
            elif params.lower().find('tomcat') != -1:
                self.is_tomcat = True
                break
        assert self.is_jar or self.is_tomcat

        if self.is_jar:
            # 修改jar包为绝对路径
            self.proc_uid = self.get_jar_path()
        elif self.is_tomcat:
            self.proc_uid = self.get_tomcat_root()

    def is_alive(self):
        try:
            status = self.process_bind.status()
            if (status is STATUS_ZOMBIE) \
                    or (status is STATUS_STOPPED) \
                    or (status is STATUS_DEAD):
                return False
        except Exception as e:
            print(e)
            return False
        return True

    def restart(self):
        try:
            if self.is_jar:
                self.process_bind = psutil.Popen(['java', '-jar', self.proc_uid], stdout=PIPE)
                self.pid = self.process_bind.pid
            elif self.is_tomcat:
                self.process_bind = psutil.Popen(self.cmdline, stdout=PIPE, cwd=self.proc_uid)
                self.pid = self.process_bind.pid
        except Exception as e:
            print("Error when ProcDao.restart()", e)

    def get_tomcat_root(self):
        assert self.is_tomcat
        tomcat_root_path = None
        for command in self.cmdline:
            if command.find("-Dcatalina.home=") != -1:
                tomcat_root_path = command.replace("-Dcatalina.home=", "").replace("\\", "/")
                break
        assert tomcat_root_path is not None
        return tomcat_root_path

    def get_jar_path(self):
        idx = None
        for idx_tmp, param in enumerate(self.cmdline):
            if param.find("-jar") != -1:
                idx = idx_tmp + 1
                break
        assert idx is not None
        candidate = self.cmdline[idx]
        if candidate.startswith('.'):
            # 相对路径
            out = candidate.replace(".", self.cwd, 1).replace("\\", "/")
        elif (candidate.count("/") + candidate.count("\\")) == 0:
            # root目录启动
            out = self.cwd + "/" + candidate
        else:
            # jar包名为绝对路径
            out = candidate
        return out


def popen_in_thread(arg_list, **kwargs):
    psutil.Popen(arg_list, stdout=PIPE, **kwargs)


def monitor_init(config_dict):
    global alive_dict
    global target_init_process_dict

    rlock = threading.RLock()
    rlock.acquire()

    target_name_list = config_dict['process_name']

    customized_process_path_list = config_dict['restart_path']
    if config_dict['need_restart']:
        for path in customized_process_path_list:
            if path.lower().find("tomcat") != -1:
                alive_dict[parse_proc_id_tomcat(path)] = [False, path, "tomcat"]
            elif path.find(".jar") != -1 or path.find("-jar") != -1:
                alive_dict[path] = [False, path, "jar"]

    print("Before init scanning, status_dict is:", alive_dict, sep="\n")

    # First Scan
    for proc in psutil.process_iter():
        if proc.name().lower() in target_name_list:
            tmp = ProcDao(proc)
            target_init_process_dict[tmp.proc_uid] = tmp
            if tmp.proc_uid in alive_dict:
                alive_dict[tmp.proc_uid][0] = True

    print("After init scanning, status_dict is:", alive_dict, sep="\n")

    for proc_id, val in alive_dict.iteritems():
        running, path, typestr = val
        print(proc_id, running, path)
        if not running:
            if typestr == "tomcat":
                psutil.Popen([path, ], cwd=proc_id, stdout=PIPE)
            if typestr == "jar":
                psutil.Popen(["java", "-jar", path], stdout=PIPE)

    rlock.release()


def refresh_target_processes(target_process_name_list):
    '''
    由目标进程的名字（字符串）获得进程id，以列表形式返回。
    '''
    global target_running_process_dict, target_init_process_dict
    target_running_process_dict.clear()
    target_alive_process_list = []
    for proc in psutil.process_iter():
        if proc.name().lower() in target_process_name_list:
            tmp = ProcDao(proc)
            target_running_process_dict[tmp.proc_uid] = tmp
            if tmp.proc_uid not in target_init_process_dict:
                target_init_process_dict[tmp.proc_uid] = tmp
    return target_alive_process_list


def check_process_status_and_restart(config_dict):
    global alive_dict
    global target_running_process_dict, target_init_process_dict
    # Scan
    for uid, proc in copy(target_init_process_dict).iteritems():
        if not proc.is_alive():
            proc.restart()
            email_sender.send_restart_email(config_dict, proc)


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
    global_memory_state = memory.percent, memory.used // MB_UNIT, memory.total // MB_UNIT
    return global_memory_state


net_status_queue = deque(maxlen=50)


def get_network_state():
    """
    获得全局网络IO状态
    :return: 类字典对象‘snetio’, 属性有'bytes_recv', 'bytes_sent', 'packets_recv', 'packets_sent'
    """
    global net_status_queue
    io_state = psutil.net_io_counters(pernic=False)
    # io_state = psutil.net_io_counters(pernic=True)
    # assert 'eth0' in io_state
    # io_state = io_state['eth0']
    bs, br = io_state.bytes_sent, io_state.bytes_recv
    tmp = (bs, br, time.time())
    net_status_queue.append(tmp)
    if len(net_status_queue) > 1:
        tmp1, tmp2 = net_status_queue[-1], net_status_queue[-2]
        delta_time = tmp1[2] - tmp2[2]
        delta_sent = (tmp1[0] - tmp2[0] + 0.0) / delta_time
        delta_recv = (tmp1[1] - tmp2[1] + 0.0) / delta_time
        delta_sent, delta_recv = delta_sent / KB_UNIT, delta_recv / KB_UNIT
    else:
        delta_sent, delta_recv = 0.0, 0.0
    return delta_sent, delta_recv


def process_state(name, limit=50):
    """
    输入进程的名字，id列表。
    根据进程列表返回进程的状态（字符串）和是否超限的布尔值。
    """
    global target_running_process_dict
    if len(target_running_process_dict) == 0:
        process_status_dict = {
            "process_name": name,
            "process_total_numbers": 0,
            "memory_occupied": 0}
        return process_status_dict, False
    memory_cnt = 0.0
    io_read_cnt = 0
    io_write_cnt = 0
    try:
        for key, proc_dao in target_running_process_dict.iteritems():
            # print(proc_dao.pid, proc_dao.proc_uid)
            proc = proc_dao.process_bind
            with proc.oneshot():
                memory_cnt += proc.memory_percent()
                io_read_cnt += proc.io_counters().read_count
                io_write_cnt += proc.io_counters().write_count
    except Exception as e:
        print("Warning at function process_state():", e)

    memory_exceed = (memory_cnt > limit)
    process_status_dict = {
        "process_name": name,
        "memory_occupied": memory_cnt,
        "process_total_numbers": len(target_init_process_dict),
        "p_read_cnt": io_read_cnt,
        "p_write_cnt": io_write_cnt
    }
    return process_status_dict, memory_exceed


def need_to_switch(t1, t2, log_interval):
    if t1.tm_yday > t2.tm_yday:
        t2.tm_yday += 365
    return (t2.tm_yday - t1.tm_yday) > log_interval


def monitor(share_queue, quit_event, email_event, config_dict=dict()):
    try:
        target_process_name_list = config_dict["target_process"]
        interval = config_dict["interval"]
        log_path = config_dict["log_path"]
        email_context = config_dict["email_context"]
        email_length = config_dict["email_length"]
        memory_limit = config_dict["memory_limit"]
        log_interval = config_dict["log_interval"]
    except Exception as e:
        print("Error at configDict, monitor exit.", e)
        sys.exit(-1)

    line_number = 0
    continue_flag = True
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

    while continue_flag is True:
        # logTempDict 为单次记录信息的项
        td = OrderedDict()
        line_number += 1
        td['LineNumber'] = line_number
        # 时间
        td['Time'] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
        # 全局CPU和内存状态
        currentCpuState = get_cpu_state(interval=interval)
        td['CPU_percent'] = currentCpuState
        global_memory_state = get_memory_state()
        td['memory_percent'], td['memory_used'], td['memory_total'] = global_memory_state
        # 获取网络IO状态
        network_status = get_network_state()
        td['bytes_sent'] = network_status[0]
        td['bytes_recv'] = network_status[1]
        # 目标进程状态
        refresh_target_processes(target_process_name_list)
        process_status_dict, is_exceed = process_state(target_process_name_list, memory_limit)
        if process_status_dict['process_total_numbers'] > 0:
            td['process_name'] = process_status_dict['process_name']
            td['process_memory_occupied'] = process_status_dict['memory_occupied']
            td['process_total_numbers'] = process_status_dict['process_total_numbers']
            td['process_read_cnt'] = process_status_dict['p_read_cnt']
            td['process_write_cnt'] = process_status_dict['p_write_cnt']
        else:
            td['process_name'] = process_status_dict['process_name']
            td['process_memory_occupied'], td['process_total_numbers'], td['process_read_cnt'], td[
                'process_write_cnt'] = 0, 0, 0, 0

        if share_queue is not None:
            share_queue.append(
                (td['LineNumber'], td['CPU_percent'], td['memory_percent'],
                 td['process_memory_occupied'], td['bytes_recv'] + td['bytes_sent'])
            )

        # 将本次记录项放入限长队列
        emailMessageQueue.append(td)

        # ----------write dict to csv file----------------
        # print("Now writing at line: %d" % line_number)
        csv_f.dict_to_csv(td)
        t2 = time.localtime()

        # if line_number % 120 == 0:
        #     csv_f.flush()

        if is_exceed:
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
            continue_flag = False  # <==> break
            csv_f.close()
        if need_to_switch(t1, t2, log_interval):
            f_name = csv_f.filename
            csv_f.close()
            zip_the_old_file(f_name.replace("csv", "zip"), f_name, log_path)
            t1 = t2  # Update t1
            logFileName = log_file_name.log_file_name(opt=log_opt)
            csv_f = CsvWriter(logFileName, path=log_path)
    return 0


def zip_the_old_file(zipFileName, logFileName, path):
    try:
        with zipfile.ZipFile(path + zipFileName, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(path + logFileName)
    except Exception as e:
        print("Error: cannot zip current log file: %s" % logFileName, e)
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
    from monitor_main import shareQueue, quitEvent, emailEvent

    os.chdir('..')
    try:
        keywordDict = read_config('config.conf')
    except Exception as e:
        print("Configuration File Wrong!")
        sys.exit(-1)
    print("Configuration Load Complete. Start Monitor.")

    monitor(shareQueue, quitEvent, emailEvent, config_dict=keywordDict)
