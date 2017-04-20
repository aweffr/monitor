# -*- coding: utf-8 -*-
from pprint import pprint

import sys

from xlsxwriter import Workbook
from xlsxwriter.worksheet import *
import xlsxwriter
from psutil._common import snetio

col_lst = ['Time', 'GlobalCpu', 'GlobalMemory', 'GlobalNetwork', 'TargetProcessStatus']


def writedeque(send_file, emailMessageQueue):
    if len(emailMessageQueue) == 0:
        return
    offset = emailMessageQueue[0]['LineNumber']
    sheet = send_file.add_worksheet(name='sheet1')
    for d in emailMessageQueue:
        d['LineNumber'] -= (offset-1)
        write_sheet(sheet, d)


def init_sheet(xls_file):
    row = 0
    col = 0
    head_lst = ['Time', 'CPU(%)', 'Memory(%)', 'MemoryUsed', 'MemoryTotal',
                'bytes_sent', 'bytes_recv', 'packets_sent', 'packets_recv',
                'errin', 'errout', 'dropin', 'dropout', 'memory_occupied',
                'p_read_cnt', 'p_write_cnt', 'process_name', 'process_total_numbers']
    for head in head_lst:
        xls_file.write(row, col, head)
        col += 1


def write_sheet(xls_file, log_dict):
    row = log_dict['LineNumber']
    col = 0
    for key, val in log_dict.items():
        if row == 1:
            xls_file.write(0, col, key)
        xls_file.write(row, col, val)
        col += 1


if __name__ == "__main__":
    workbook = xlsxwriter.Workbook('demo2.xlsx')  # 创建一个Excel文件
    sheet1 = workbook.add_worksheet(name='sheet1')  # 创建一个工作表对象
    init_sheet(sheet1)
    sample_dict = {'GlobalCpu': 42.4,
                   'GlobalMemory': (68.3, 2745, 4022),
                   'GlobalNetwork': snetio(bytes_sent=51938878, bytes_recv=616517977, packets_sent=356753,
                                           packets_recv=598017, errin=0, errout=0, dropin=0, dropout=0),
                   'LineNumber': 11,
                   'TargetProcessStatus': {'memory_occupied': 0.43159710352114866,
                                           'p_read_cnt': 44,
                                           'p_write_cnt': 0,
                                           'process_name': 'qqbrowser.exe',
                                           'process_total_numbers': 1},
                   'Time': '2017/03/28 11:34:03'}
    write_sheet(sheet1, sample_dict)
    workbook.close()

"""
sample dict:
{'GlobalCpu': 45.8,
 'GlobalMemory': (78.7, 3167, 4022),
 'GlobalNetwork': snetio(bytes_sent=51936414, bytes_recv=616515894, packets_sent=356739, packets_recv=598009, errin=0, errout=0, dropin=0, dropout=0),
 'LineNumber': 10,
 'TargetProcessStatus': {'memory_occupied': 14.452384467165988,
                         'p_read_cnt': 302441,
                         'p_write_cnt': 314334,
                         'process_name': 'qqbrowser.exe',
                         'process_total_numbers': 13},
 'Time': '2017/03/28 11:34:02'}
{'GlobalCpu': 42.4,
 'GlobalMemory': (68.3, 2745, 4022),
 'GlobalNetwork': snetio(bytes_sent=51938878, bytes_recv=616517977, packets_sent=356753, packets_recv=598017, errin=0, errout=0, dropin=0, dropout=0),
 'LineNumber': 11,
 'TargetProcessStatus': {'memory_occupied': 0.43159710352114866,
                         'p_read_cnt': 44,
                         'p_write_cnt': 0,
                         'process_name': 'qqbrowser.exe',
                         'process_total_numbers': 1},
 'Time': '2017/03/28 11:34:03'}
{'GlobalCpu': 17.4,
 'GlobalMemory': (66.2, 2664, 4022),
 'GlobalNetwork': snetio(bytes_sent=51957287, bytes_recv=616522023, packets_sent=356800, packets_recv=598048, errin=0, errout=0, dropin=0, dropout=0),
 'LineNumber': 12,
 'TargetProcessStatus': {'memory_occupied': 0,
                         'process_name': 'qqbrowser.exe',
                         'process_total_numbers': 0},
 'Time': '2017/03/28 11:34:04'}

"""
