# coding=utf-8
import re
import logging

import requests
from flask import Flask
from pexpect import ExceptionPexpect

from .ssh import Ssh, SwitcherInnerError
from .config import *

logger = logging.getLogger(__name__)

OPERATIONS = {}
    
OPERATIONS["before"] = """\
interface  {interface}
undo arp anti-attack check user-bind enable
undo ip source check user-bind enable
undo shutdown
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


def operate(cmd, report=True, **kwargs):
    """
    :kwargs: switcher, interface, traffic_policy, public_ip
    """
    rv = {
        "command": cmd,
        "status": "ok",
        "interface": "",
        "msg": []
    }

    cmds = OPERATIONS[cmd]
    try:
        interface = kwargs["interface"]
        rv["interface"] = interface
        kwargs["interface"] = format_interface(interface)
        switcher = kwargs.pop("switcher")
        cmds = cmds.format(**kwargs)
    except KeyError as e:
        msg = "Imcomplete information for %s command: %s" % (cmd, e.args[0])
        rv["msg"].append(msg)
        rv["status"] = "error"
        logger.error(msg)
    except _FormatError as e:
        rv["msg"].append(str(e))
        rv["status"] = "error"
        logger.error(e)
    else:
        with Ssh(switcher, USER, PASSWORD) as ssh:
            for cmd in cmds.splitlines():
                try:
                    ssh.run(cmd, raise_exception=True)
                except SwitcherInnerError as e:
                    logger.warning(e)
                    rv["msg"].append(e.args[0] + " execute failed")
                except ExceptionPexpect as e:
                    logger.error(e)
                    rv["msg"].append(str(e))
                    rv["status"] = "error"
                    break
    rv["msg"] = "\n".join(rv["msg"])
    if report:
        try:
            logger.info("report status")
            r = requests.post(CALLBACK, json=rv, timeout=5)
            if not r.ok:
                r.raise_for_status()
        except Exception as e:
            logger.info("faild report status: %s:", e)
    else:
        return rv


class _FormatError(Exception):
    """interface format error"""


def format_interface(interface):
    try:
        interface_type, interface_num = re.search(r"([A-Za-z]+)(\d+\/\d+\/\d+)", interface).groups()
    except:
        raise _FormatError("cann't format interface %s" % interface)
    if "XGi" in interface_type:
        return "XGigabitEthernet" + interface_num
    if "Gi" in interface_type or "GE" in interface_type or "G" in interface_type:
        return "GigabitEthernet" + interface_num
    if "Eth" in interface_type or "E" in interface_type:
        return "Ethernet" + interface_num
    raise _FormatError("cann't format interface %s" % interface)


def get_mac_addr(switcher, interface):
    try:
        interface = format_interface(interface)
    except _FormatError:
        logger.error("get_mac_addr for %s : %s", interface, e)
        return "" 
    cmd = "display mac-address dynamic {}"
    with Ssh(switcher, USER, PASSWORD) as ssh:
        try:
            rv = ssh.run(cmd.format(interface))
        except (SwitcherInnerError, ExceptionPexpect) as e:
            logger.error("get_mac_addr for %s : %s", interface, e)
            return ""
        r = re.findall(r"\w{4}-\w{4}-\w{4}", rv)
        if r and len(r) == 1:
            mac = r.pop().replace("-", "")
            mac = ":".join([mac[i:i+2] for i in range(0, len(mac), 2)])
            return mac
        else:
            return ""


def is_description(switcher, interface):
    PATTERN = "NULL_$$$$&&&&"
    try:
        interface = format_interface(interface)
    except _FormatError:
        logger.error("get_mac_addr for %s : %s", interface, e)
        return False 

    cmds = "interface {}\n" \
            "display this"
    with Ssh(switcher, USER, PASSWORD) as ssh:
        try:
            for cmd in cmds.splitlines():
                rv = ssh.run(cmd.format(interface))
        except (SwitcherInnerError, ExceptionPexpect) as e:
            logger.error("is_description for %s : %s", interface, e)
            return False
    return PATTERN in rv
