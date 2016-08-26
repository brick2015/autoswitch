import logging
from ssh import Ssh

cmds = """\
interface  {0}
undo shutdown
port link-type access
port default vlan 888
stp root-protection
# traffic-policy {1} inbound
arp anti-attack check user-bind enable
ip source check user-bind enable
user-bind static ip-address {2} interface {0}
"""

def interface_on(host, interface, traffic_policy, ip):
    try:
        with Ssh(host, "backup", "www.51idc.com") as ssh:
            for cmd in cmds.format(interface, traffic_policy, ip).splitlines():
                ssh.run(cmd, raise_exception=True)
    except Exception as e:
        print "*****", e


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    interface_on("10.198.1.42", "Ethernet0/0/17", "25M", "1.1.1.1")
