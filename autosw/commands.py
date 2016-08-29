import re
import logging

from flask import Flask
from pexpect import ExceptionPexpect

from .ssh import Ssh, SwitcherInnerError

logger = logging.getLogger(__name__)

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
        kwargs["interface"] = format_interface(kwargs["interface"])
    except Exception as e:
        logger.error(e)
        return

    try:
        switcher = kwargs.pop("switcher")
        cmds = cmds.format(**kwargs)
    except KeyError as e:
        logger.error("Imcomplete information for %s command: %s", cmd, e.args[0])
        return

    with Ssh(switcher, USER, PASSWORD) as ssh:
        for cmd in cmds.splitlines():
            try:
                ssh.run(cmd, raise_exception=True)
            except SwitcherInnerError as e:
                logger.warning(e)
            except ExceptionPexpect as e:
                logger.error(e)
                break


def format_interface(interface):
    try:
        interface_type, interface_num = re.search(r"([A-Za-z]+)(\d+\/\d+\/\d+)", interface).groups()
    except:
        raise Exception("cann't format interface %s" % interface)
    if "XGi" in interface_type:
        return "XGigabitEthernet" + interface_num
    if "Gi" in interface_type or "GE" in interface_type or "G" in interface_type:
        return "GigabitEthernet" + interface_num
    if "Eth" in interface_type or "E" in interface_type:
        return "Ethernet" + interface_num
    raise Exception("cann't format interface %s" % interface)
