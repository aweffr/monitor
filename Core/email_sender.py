# -*- coding: utf-8 -*-
from email import encoders
import time
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def msg_generator(from_addr, to_addr, email_context, header=u'服务器目前状况'):
    with open(email_context, 'r') as log_file:
        msg = MIMEText('\n'.join(log_file), 'plain', 'utf-8')
    msg['From'] = _format_addr(u'进程监控 <%s>' % from_addr)
    msg['To'] = _format_addr(u'管理员 <%s>' % to_addr)
    msg['Subject'] = Header(header, 'utf-8').encode()
    return msg


def msg_generator_attachment(from_addr, to_addr, email_context, header=u'服务器目前状况'):
    msg = MIMEMultipart()
    msg['From'] = _format_addr(u'进程监控 <%s>' % from_addr)
    msg['To'] = _format_addr(u'管理员 <%s>' % to_addr)
    msg['Subject'] = Header(header, 'utf-8').encode()
    text_part = MIMEText("服务器状况见附件。", 'plain', 'utf-8')
    msg.attach(text_part)
    part = MIMEApplication(open(email_context, 'rb').read())
    part.add_header('Content-Disposition', 'attachment', filename='status.csv')
    msg.attach(part)
    return msg


def send_email(from_addr, password, smtp_server, to_addr, email_context, xls_format=False):
    '''
    from_addr: Email sender. e.g aweffr@126.com
    password:     password      e.g huami123
    smtp_server:  email server
    to_addr:      account to send
    '''
    server = smtplib.SMTP(smtp_server, 25)  # SMTP协议默认端口是25
    server.set_debuglevel(False)  # 打印工作流
    server.login(from_addr, password)
    if xls_format:
        msg = msg_generator_attachment(from_addr, to_addr, email_context)
    else:
        msg = msg_generator(from_addr, to_addr, email_context)
    for i in range(3):
        try:
            server.sendmail(from_addr, to_addr, msg.as_string())
            break
        except Exception as e:
            print("Fail to send Email: %d (times)" % (i + 1), e)
    server.quit()


def send_restart_email(configDict, proc):
    emailFilePath = configDict["log_path"] + "restart_email_context.txt"
    f = open(emailFilePath, "w")
    f.writelines(
        "Process has been shutdown: {process_name}, now restart at {time}. \n\
        target process path: {cmdline}".format(**{
            "process_name": proc.name,
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "cmdline": proc.cmdline}))
    f.close()
    send_email(from_addr=configDict["from_addr"],
               password=configDict["password"],
               smtp_server=configDict["smtp_server"],
               to_addr=configDict["to_addr"],
               email_context=emailFilePath)


if __name__ == "__main__":
    import read_config, os

    os.chdir('..')
    config_dict = read_config.read_config("./config.conf")
    send_email(
        from_addr=config_dict["from_addr"],
        password=config_dict["password"],
        smtp_server=config_dict["smtp_server"],
        to_addr=config_dict["to_addr"],
        email_context="./Log/email_context.csv",
        xls_format=True)
