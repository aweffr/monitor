#!/bin/bash
# monitor_run        Startup script for the python_monitor
# chkconfig: 2345 80 90
# description: Run the monitor for CPU, process and memory.
# processname: python
dir=/usr/local/huami/python2.7
nohup ${dir}/env/bin/python ${dir}/app.py > out_log 2>&1 &
