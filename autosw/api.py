from threading import Thread

from flask import Flask, request, jsonify

from .commands import operate, get_mac_addr, is_description

app = Flask(__name__)


@app.route("/vlan_up", methods=["POST"])
def vlan_up():
    """
    {"switcher": "xxx", "interface": "xxx",}
    """
    j = request.get_json(force=True)
    rv = operate("vlan_up", report=False, **j)
    return jsonify(rv)


@app.route("/vlan_down", methods=["POST"])
def vlan_down():
    """
    {"switcher": "xxx", "interface": "xxx",}
    """
    j = request.get_json(force=True)
    Thread(target=operate, args=("vlan_down", False), kwargs=j).start()
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


@app.route("/mac", methods=["POST"])
def mac():
    """
    {"switcher": "xxx", 
     "interface": "xxx"}
    """
    j = request.get_json(force=True)
    mac_addr = get_mac_addr(j["switcher"], j["interface"])
    if mac_addr:
        return jsonify(status="ok", mac=mac_addr)
    else:
        return jsonify(status="error", mac=mac_addr)


@app.route("/description", methods=["POST"])
def description():
    """
    {"switcher": "xxx", 
     "interface": "xxx"}
    """
    j = request.get_json(force=True)
    ready = is_description(j["switcher"], j["interface"])
    if ready:
        return jsonify(status="ok")
    else:
        return jsonify(status="error")
