import logging

from flask import Flask
from pexpect import ExceptionPexpect

from .ssh import Ssh, SwitcherInnerError

logger = logging.getLogger("__name__")

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


def operate(cmd, kwargs):
    """
    :kwargs: switcher, interface, traffic_policy, public_ip
    """
    cmds = OPERATIONS[cmd]
    try:
        switcher = kwargs.pop("switcher")
        with Ssh(switcher, USER, PASSWORD) as ssh:
            for cmd in cmds.format(**kwargs).splitlines():
                ssh.run(cmd, raise_exception=True)
    except KeyError as e:
        logger.error("Imcomplete information for %s command: %s", cmd, e.args[0])
    except (SwitcherInnerError, ExceptionPexpect) as e:
        logger.error(e)
