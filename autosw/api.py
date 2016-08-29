from threading import Thread

from flask import Flask, request

from .commands import operate

app = Flask(__name__)


@app.route("/before", methods=["POST"])
def before():
    """
    {"switcher": "xxx", "interface": "xxx",}
    """
    j = request.get_json(force=True)
    Thread(target=operate, args=("before", j)).start()
    return "ok"


@app.route("/up", methods=["POST"])
def up():
    """
    {"switcher": "xxx", 
     "interface": "xxx",
     "traffic_policy": "xxx", 
     "public_ip": "xxx"}
    """
    j = request.get_json(force=True)
    Thread(target=operate, args=("up",j)).start()
    return "ok"


@app.route("/down", methods=["POST"])
def down():
    """
    {"switcher": "xxx", 
     "interface": "xxx",
     "public_ip": "xxx"}
    """
    j = request.get_json(force=True)
    Thread(target=operate, args=("down", j)).start()
    return "ok"
