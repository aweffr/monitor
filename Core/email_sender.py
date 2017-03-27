# -*- coding: utf-8 -*-
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def msg_generator(from_addr, to_addr, email_context):
    with open(email_context, 'r') as log_file:
        msg = MIMEText('\n'.join(log_file), 'plain', 'utf-8')
    msg['From'] = _format_addr(u'进程监控 <%s>' % from_addr)
    msg['To'] = _format_addr(u'管理员 <%s>' % to_addr)
    msg['Subject'] = Header(u'服务器目前状况', 'utf-8').encode()
    return msg


def send_email(from_addr, password, smtp_server, to_addr, email_context):
    '''
    from_addr: Email sender. e.g aweffr@126.com
    password:     password      e.g huami123
    smtp_server:  email server
    to_addr:      account to send
    '''
    server = smtplib.SMTP(smtp_server, 25)  # SMTP协议默认端口是25
    server.set_debuglevel(False)  # 打印工作流
    server.login(from_addr, password)
    msg = msg_generator(from_addr, to_addr, email_context)
    for i in range(3):
        try:
            server.sendmail(from_addr, to_addr, msg.as_string())
            break
        except Exception as e:
            print("Fail to send Email:", e)
    server.quit()


if __name__ == "__main__":
    from_addr = "aweffr@126.com"
    password = "huami123"
    # 输入SMTP服务器地址:
    smtp_server = "smtp.126.com"
    # 输入收件人地址:
    to_addr = ["aweffr@foxmail.com", "aweffr@126.com"]
    send_email(from_addr, password, smtp_server, to_addr, 'email_context.txt')
