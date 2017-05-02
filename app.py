# coding=utf-8
from __future__ import print_function
import sys
sys.path.extend(["./Core", ])
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_script import Manager
from get_local_ip import get_local_ip
import json
import time
import monitor_main
import threading

app = Flask(__name__)
bootstrap = Bootstrap(app)
manager = Manager(app)


@app.route("/")
def index():
    return render_template("monitor.html")


@app.route("/ajaxtest")
def ajax_test():
    return render_template("ajaxtest.html")


@app.route("/getdata")
def getdata():
    if len(monitor_main.shareQueue) > 0:
        tmp = monitor_main.shareQueue[-1]
        d = {
            "time": time.strftime("%H:%M:%S", time.localtime()),
            "cpu_percent": tmp[1],
            "mem_percent": tmp[2],
            "process": tmp[3],
            "net_io": tmp[4]
        }
    else:
        d = {
            "time": time.strftime("%H:%M:%S", time.localtime()),
            "cpu_percent": 0,
            "mem_percent": 0,
            "process": 0,
            "net_io": 0
        }
    return json.dumps(d)

def app_run(host, port):
    global app
    try:
        app.run(host=host, port=port)
    except Exception as e:
        print("Web Interrupted!", e)
        sys.exit(1)
    finally:
        monitor_main.quitEvent.set()



if __name__ == "__main__":
    t1 = threading.Thread(target=monitor_main.run)
    t1.run()
    # 确保已经读取设置
    while not monitor_main.configLoadComplete[0]:
        time.sleep(1)
    d = monitor_main.configDict
    t2 = threading.Thread(
        target=app_run,
        kwargs={'host': d['host'], 'port': d['port']})
    t2.run()
    t1.join()
    t2.join()
