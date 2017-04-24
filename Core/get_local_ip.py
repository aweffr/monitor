# coding=utf-8

import socket


def get_local_ip():
    return socket.gethostbyname(
        socket.gethostname()
    )


if __name__ == "__main__":
    local_ip = get_local_ip()  # 得到本地ip
    print "local ip: %s" % local_ip
