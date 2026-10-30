import os
import sys

from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.link import TCLink

MODE = sys.argv[1] if len(sys.argv) > 1 else 'priority'  # priority | baseline

QOS_PRIORITY = (
    'ovs-vsctl set port s1-eth1 qos=@q -- '
    '--id=@q create qos type=linux-htb other-config:max-rate=10000000 '
    'queues=0=@q0,1=@q1 -- '
    '--id=@q0 create queue other-config:max-rate=7000000 -- '
    '--id=@q1 create queue other-config:min-rate=3000000 other-config:max-rate=10000000'
)

QOS_BASELINE = (
    'ovs-vsctl set port s1-eth1 qos=@q -- '
    '--id=@q create qos type=linux-htb other-config:max-rate=10000000 '
    'queues=0=@q0 -- '
    '--id=@q0 create queue other-config:max-rate=10000000'
)


def topology():
    net = Mininet(controller=RemoteController, link=TCLink)
    net.addController('c0', ip='127.0.0.1', port=6633)
    s1 = net.addSwitch('s1', protocols='OpenFlow13')

    server = net.addHost('server', ip='10.0.0.1')
    p1 = net.addHost('p1', ip='10.0.0.2')
    p2 = net.addHost('p2', ip='10.0.0.3')
    p3 = net.addHost('p3', ip='10.0.0.4')

    # server link must be added first so it becomes s1-eth1
    net.addLink(server, s1, delay='5ms', jitter='2ms')
    net.addLink(p1, s1, bw=10, delay='5ms', jitter='2ms')
    net.addLink(p2, s1, bw=10, delay='5ms', jitter='2ms')
    net.addLink(p3, s1, bw=20, delay='5ms')

    net.start()
    os.system(QOS_PRIORITY if MODE == 'priority' else QOS_BASELINE)
    print(f'*** QoS mode: {MODE}')
    CLI(net)
    os.system('ovs-vsctl clear port s1-eth1 qos')
    net.stop()


if __name__ == '__main__':
    topology()
