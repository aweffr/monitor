import configparser

'''
Example Config File

[email]
from = aweffr@126.com
password = huami123
to = aweffr@foxmail.com
smtp = smtp.126.com

[moniter]
target = qqbrowser.exe
memory_limit = 40
interval = 1.0

[file]
log_file = log.txt
email_context = email_context.txt
email_length = 25
'''


def read_config(filename):
    cf = configparser.ConfigParser()
    cf.read(filename)

    d = dict()
    d["from_addr"] = cf.get("email", "from_addr")
    d["password"] = cf.get("email", "password")
    d["to_addr"] = cf.get("email", "to_addr")
    d["smtp_server"] = cf.get("email", "smtp")

    d["target_process"] = cf.get("moniter", "target")
    d["memory_limit"] = float(cf.get("moniter", "memory_limit"))
    d["interval"] = float(cf.get("moniter", "interval"))

    d["log_file"] = cf.get("file", "log_file")
    d["email_context"] = cf.get("file", "email_context")
    d["email_length"] = int(cf.get("file", "email_length"))

    return d


if __name__ == "__main__":
    d = read_config("config.conf")
    print(d)
