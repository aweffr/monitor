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
memory_limit = 25
interval = 1.0

[file]
log_file = ./Log/log.txt
email_context = ./Log/email_context.txt
email_length = 40

[whitelist]
process1 = java.exe
process2 = javaw.exe
process3 = explorer.exe

[blacklist]
process1 = notepad.exe
'''


def read_config(filename):
    cf = configparser.ConfigParser()
    cf.read(filename)

    d = dict()
    d["from_addr"] = cf.get("email", "from_addr")
    d["password"] = cf.get("email", "password")
    d["to_addr"] = cf.get("email", "to_addr").split(",")
    d["to_addr"] = list(map(lambda x: x.strip(), d["to_addr"]))
    d["smtp_server"] = cf.get("email", "smtp")

    d["target_process"] = cf.get("moniter", "target")
    d["memory_limit"] = float(cf.get("moniter", "memory_limit"))
    d["interval"] = float(cf.get("moniter", "interval"))

    d["log_file"] = cf.get("file", "log_file")
    d["email_context"] = cf.get("file", "email_context")
    d["email_length"] = int(cf.get("file", "email_length"))

    d["white_list"] = cf.get("white_list", "process").split(",")
    d["white_list"] = list(map(lambda x: x.strip(), d["white_list"]))
    d["black_list"] = cf.get("black_list", "process").split(",")
    d["black_list"] = list(map(lambda x: x.strip(), d["black_list"]))

    return d


if __name__ == "__main__":
    from pprint import pprint

    d = read_config("../config.conf")
    pprint(d)
    #
    # d2 =
