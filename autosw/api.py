from threading import Thread

from flask import Flask, request, jsonify

from .commands import operate

app = Flask(__name__)


@app.route("/before", methods=["POST"])
def before():
    """
    {"switcher": "xxx", "interface": "xxx",}
    """
    j = request.get_json(force=True)
    rv = operate("before", report=False, **j)
    return jsonify(rv)


@app.route("/up", methods=["POST"])
def up():
    """
    {"switcher": "xxx", 
     "interface": "xxx",
     "traffic_policy": "xxx", 
     "public_ip": "xxx"}
    """
    j = request.get_json(force=True)
    Thread(target=operate, args=("up",), kwargs=j).start()
    return "ok"


@app.route("/down", methods=["POST"])
def down():
    """
    {"switcher": "xxx", 
     "interface": "xxx",
     "public_ip": "xxx"}
    """
    j = request.get_json(force=True)
    Thread(target=operate, args=("down",), kwargs=j).start()
    return "ok"
