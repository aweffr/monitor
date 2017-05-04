# coding=utf-8
import configparser

'''
Example Config File

[email]
from_addr = aweffr@126.com
password = huami123
to_addr = aweffr@foxmail.com, aweffr@126.com
smtp = smtp.126.com

[moniter]
target = qqbrowser.exe
memory_limit = 40
interval = 1.0

[file]
log_path = ./Log/
log_interval = 7
email_context = ./Log/email_context.txt
email_length = 40

[white_list]
process = java.exe, javaw.exe, explorer.exe

[black_list]
process = notepad.exe
'''


def time_to_seconds(string):
    string = list(map(int, string.strip().split(":")))
    if len(string) != 3:
        raise Exception("Error: Email Sending Interval")
    else:
        return 3600 * string[0] + 60 * string[1] + string[2]


def parse_process_path(s):
    s = str(s).replace("\\", "/")
    s = s.strip()
    out = []
    if s.startswith("["):
        s = s.replace("[", "").replace("]", "").split(",")
        for path in s:
            if len(path.strip()) > 0:
                out.append(path)
    else:
        out.append(s)
    return out


def parse_process_name(s):
    s = str(s)
    s = s.strip()
    out = []
    if s.startswith("["):
        s = s.replace("[", "").replace("]", "").split(",")
        for name in s:
            name = name.strip()
            if len(name) > 0:
                out.append(name)
    else:
        out.append(s)
    return out


def read_config(filename):
    cf = configparser.ConfigParser()
    cf.read(filename, encoding='utf-8')

    d = dict()

    d["debug_level"] = cf.get("debug", "debug_level", fallback="0")
    d["debug_file"] = cf.get("debug", "debug_file", fallback="program_log.txt")

    d["from_addr"] = cf.get("email", "from_addr")
    d["password"] = cf.get("email", "password")
    d["to_addr"] = cf.get("email", "to_addr").split(",")
    d["to_addr"] = map(lambda x: x.strip(), d["to_addr"])
    d["smtp_server"] = cf.get("email", "smtp")
    d["send_interval"] = time_to_seconds(cf.get("email", "send_interval"))

    d["target_process"] = cf.get("monitor", "target")
    d["process_name"] = parse_process_name(cf.get("monitor", "target"))
    d["memory_limit"] = float(cf.get("monitor", "memory_limit"))
    d["interval"] = float(cf.get("monitor", "interval", fallback='1.0'))

    # net_io_upper_bound的单位为MB，整数小数均可
    d['net_io_upper_bound'] = cf.getfloat('monitor', 'net_io_upper_bound')
    # net_io_limit为上限（百分比），当高于该百分比并超过峰值持续时间(net_io_time_limit)会邮件报警
    d['net_io_limit'] = cf.getfloat('monitor', 'net_io_limit')
    # net_io_time_limit为峰值持续时间
    d['net_io_time_limit'] = cf.getfloat('monitor', 'net_io_time_limit')

    d["log_path"] = cf.get("file", "log_path", fallback='./Log/').replace("\\", "/")
    d["log_interval"] = int(cf.get("file", "log_interval"))
    d["email_context"] = cf.get("file", "email_context", fallback='./Log/email_context.txt').replace("\\", "/")
    d["email_length"] = int(cf.get("file", "email_length"))

    d["white_list"] = cf.get("white_list", "process").split(",")
    d["white_list"] = map(lambda x: x.strip(), d["white_list"])
    d["black_list"] = cf.get("black_list", "process").split(",")
    d["black_list"] = map(lambda x: x.strip(), d["black_list"])

    if 'restart' in cf:
        d["need_restart"] = cf.getboolean("restart", "need_restart")
        d["restart_path"] = parse_process_path(cf.get("restart", "restart_path"))
        # d["process_name"] = cf.get("restart", "process_name")
        d["restart_interval"] = time_to_seconds(cf.get("restart", "restart_interval", fallback="00:00:60"))

    d['host'] = cf.get('web', 'ip', fallback='localhost')
    d['port'] = int(cf.get('web', 'port', fallback='5000'))
    return d


if __name__ == "__main__":
    from pprint import pprint
    import os

    os.chdir("..")
    d = read_config("./config.conf")
    pprint(d)
