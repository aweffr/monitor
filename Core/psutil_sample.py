# -*- coding: utf-8 -*-
import psutil

MB_UNIT = 1024 * 1024

print
psutil.cpu_percent()

for x in range(2):
    # 以interval间隔获取CPU使用率
    print
    psutil.cpu_percent(interval=0.5)
for x in range(2):
    print
    psutil.cpu_percent(percpu=True, interval=0.5)

# 获取CPU时间分片
print
psutil.cpu_times()

# 内存
print
psutil.virtual_memory()
print
psutil.virtual_memory().total / (MB_UNIT)

# 交换内存
print
psutil.swap_memory()

# 查看磁盘信息
print
psutil.disk_partitions()  # 查看所有分区信息
print
psutil.disk_usage('c:\\')  # 查看指定分区的磁盘空间情况

# 查看进程信息
pids = psutil.pids()

for pid in pids:
    print
    "pid:%d, name:%s" % (pid, psutil.Process(pid).name())
