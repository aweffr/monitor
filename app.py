from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_script import Manager
import json
import time
from random import randint
import MonitorMain
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
    if len(MonitorMain.shareQueue) > 0:
        tmp = MonitorMain.shareQueue[-1]
        d = {
            "time": time.strftime("%H:%M:%S", time.localtime()),
            "cpu_percent": tmp[1],
            "mem_percent": tmp[2],
            "process": tmp[3]
        }
    else:
        d = {
            "time": time.strftime("%H:%M:%S", time.localtime()),
            "cpu_percent": 0,
            "mem_percent": 0,
            "process": 0
        }
    return json.dumps(d)


if __name__ == "__main__":
    t1 = threading.Thread(target=MonitorMain.run)
    t2 = threading.Thread(target=app.run)
    t1.run()
    t2.run()
    t1.join()
    t2.join()
