# Wired experiment 1!
# 3 consumers linked together, 3 separate producers, 4-5 intermediate nodes (3 normal "best", one slow fourth)
# Start traffic consumer on each node, after X number of seconds bring down some # of links (0, 1, 2, all normal)
# Compare # of interests and elapsed time for each (congestion)
#
# http://minindn.memphis.edu/experiment.html
#
from mininet.log import setLogLevel, info
from mininet.topo import Topo
from mininet.link import TCIntf
from time import time, sleep
from minindn.minindn import Minindn
from minindn.apps.app_manager import AppManager
from minindn.util import MiniNDNCLI, getPopen
from minindn.apps.nfd import Nfd
from minindn.helpers.nfdc import Nfdc
from minindn.apps.tshark import Tshark


# from minindn.apps.nlsr import Nlsr

def run():
    PREFIX = "/ndn/test/"
    Minindn.cleanUp()
    Minindn.verifyDependencies()
    topo = Topo()
    # Setup topo
    print("Setup")
    c1 = topo.addHost('c1')
    i1 = topo.addHost('i1')

    i2 = topo.addHost('i2')
    i3 = topo.addHost('i3')
    i4 = topo.addHost('i4')
    i5 = topo.addHost('i5')

    i6 = topo.addHost('i6')
    p1 = topo.addHost('p1')

    topo.addLink(c1, i1, bw=10)

    topo.addLink(i1, i2, bw=4, delay='40ms')
    topo.addLink(i1, i3, bw=4, delay='10ms')
    topo.addLink(i1, i4, bw=4, delay='40ms')
    topo.addLink(i1, i5, bw=4, delay='40ms')

    topo.addLink(i2, i6, bw=7, delay='7ms')
    topo.addLink(i3, i6, bw=7, delay='7ms')
    topo.addLink(i4, i6, bw=7, delay='7ms')
    topo.addLink(i5, i6, bw=7, delay='7ms')

    topo.addLink(i6, p1, bw=10)
    ndn = Minindn(topo=topo)
    ndn.start()
    nfds = AppManager(ndn, ndn.net.hosts, Nfd)
    # Setup routes to C2
    # This is not functional but I'm saving this as an example for the future :)
    # for host1 in ndn.net.hosts:
    #     for host2 in ndn.net.hosts:
    #         if 'p' in host1.name and not 'p' in host2.name:
    #             return
    #         elif 'i' in host1.name and 'c' in host2.name:
    #             return
    #         else:
    #             interface = host2.connectionsTo(host1)[0]
    #             interface_ip = interface.IP()
    #             Nfdc.registerRoute(host1, PREFIX, interface_ip)
    links = {"c1": ["i1", "i2"], "i1": ["p1"], "i2": ["p2"]}
    for first in links:
        for second in links[first]:
            host1 = ndn.net[first]
            host2 = ndn.net[second]
            interface = host2.connectionsTo(host1)[0]
            interface_ip = interface.IP()
            Nfdc.registerRoute(host1, PREFIX, interface_ip)
    interface = host2.connectionsTo(host1)[0]
    interface_ip = interface.IP()
    Nfdc.registerRoute(host1, PREFIX, interface_ip)

    # Run small thing before to ensure info caching, large afterwards?
    # print("Setup round")
    # getPopen(ndn.net["c1"], "ndn-traffic-client -c 5 cons_conf")
    # getPopen(ndn.net["p1"], "ndn-traffic-server -c 5 prod_conf")
    # # TODO: Traffic generator!
    # sleep(5)  # ?
    # nfds["i3"].stop()
    # tempshark = Tshark(ndn["c1"])
    # tempshark.start()

    # print("Round 1")
    # time1 = time()
    # getPopen(ndn.net["c1"], "ndn-traffic-client -c 20 cons_conf")
    # getPopen(ndn.net["p1"], "ndn-traffic-server -c 20 prod_conf")
    # # Wait on processes to close, end
    # time2 = time()
    # print("Time elapsed: {} s".format(time2 - time1))
    MiniNDNCLI(ndn.net)


if __name__ == '__main__':
    run()
