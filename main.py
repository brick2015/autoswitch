import logging

from flask import Flask

from ssh import Ssh

logging.basicConfig(level=logging.DEBUG)

USER = "backup"
PASSWORD = "www.51idc.com"

OPERATIONS = {}
    
OPERATIONS["before"] = """\
interface  {interface}
port link-type access
port default vlan 888
"""

OPERATIONS["up"] = """\
interface  {interface}
undo shutdown
port link-type access
port default vlan 18
stp root-protection
undo traffic-policy inbound
traffic-policy {traffic_policy} inbound
arp anti-attack check user-bind enable
ip source check user-bind enable
user-bind static ip-address {public_ip} interface {interface}
"""

OPERATIONS["down"] = """\
interface  {interface}
undo description
shutdown
undo port default vlan
undo traffic-policy inbound
undo arp anti-attack check user-bind enable
undo ip source check user-bind enable
undo user-bind static ip-address {public_ip} interface {interface}
"""

# def operate(cmd, switcher, interface, traffic_policy, public_ip):
def operate(cmd, switcher, **kwargs):
    """
    :kwargs: interface, traffic_policy, public_ip
    """
    cmds = OPERATIONS[cmd]
    try:
        with Ssh(switcher, USER, PASSWORD) as ssh:
            for cmd in cmds.format(**kwargs).splitlines():
                ssh.run(cmd, raise_exception=True)
    except Exception as e:
        print type(e), e

test_args = {
    "interface": "Ethernet0/0/17",
    "traffic_policy": "25M",
    "public_ip": "1.1.1.1"
}


if __name__ == '__main__':
    # operate("before", "10.198.1.42", **test_args)
    operate("up", "10.188.0.6", **test_args)
