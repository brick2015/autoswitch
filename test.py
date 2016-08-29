import json
from autosw import app

test_args = {
    "switcher": "10.188.0.6",
    "interface": "Ethernet0/0/17",
    "traffic_policy": "25M",
    "public_ip": "1.1.1.1"
}

client = app.test_client()

def test_before():
    rv = client.post("/before", data=json.dumps(test_args))
    assert rv.data == "ok"


def test_up():
    rv = client.post("/up", data=json.dumps(test_args))
    assert rv.data == "ok"


def test_down():
    rv = client.post("/down", data=json.dumps(test_args))
    assert rv.data == "ok"


if __name__ == "__main__":
    test_before()
    test_up()
    test_down()
