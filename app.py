from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_script import Manager
from flask_wtf import FlaskForm
import json
import time
from random import randint

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
    d = {
        "time": time.strftime("%H:%M:%S", time.localtime()),
        "cpu_percent": randint(0, 100),
        "mem_percent": randint(0, 100),
        "process": randint(0, 100)
    }
    return json.dumps(d)


if __name__ == "__main__":
    manager.run()
