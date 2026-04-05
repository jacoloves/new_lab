import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from network import NetworkEventScheduler, Node, Link, Switch, Router

network_event_scheduler = NetworkEventScheduler(
    log_enabled=True, verbose=True, stp_verbose=True
)

node1 = Node(
    node_id="n1",
    mac_address="00:1A:2B:3C:4D:5E",
    ip_address="192.168.1.1/24",
    network_event_scheduler=network_event_scheduler,
)
node2 = Node(
    node_id="n2",
    mac_address="00:1A:2B:3C:4D:5F",
    ip_address="192.168.2.1/24",
    network_event_scheduler=network_event_scheduler,
)
router1 = Router(
    node_id="r1",
    ip_address=["192.168.1.254/24", "10.1.3.1/24", "10.1.4.1/24"],
    network_event_scheduler=network_event_scheduler,
)
router2 = Router(
    node_id="r2",
    ip_address=["192.168.2.254/24", "10.2.3.1/24", "10.2.4.1/24"],
    network_event_scheduler=network_event_scheduler,
)
router3 = Router(
    node_id="r3",
    ip_address=["10.1.3.2/24", "10.2.3.2/24"],
    network_event_scheduler=network_event_scheduler,
)
router4 = Router(
    node_id="r4",
    ip_address=["10.1.4.2/24", "10.2.4.2/24"],
    network_event_scheduler=network_event_scheduler,
)

link1 = Link(
    node1,
    router1,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link2 = Link(
    router2,
    node2,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link3 = Link(
    router1,
    router3,
    bandwidth=200000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link4 = Link(
    router1,
    router4,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link5 = Link(
    router2,
    router3,
    bandwidth=200000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link6 = Link(
    router2,
    router4,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)

network_event_scheduler.draw()

router1.print_interfaces()
router2.print_interfaces()
router3.print_interfaces()
router4.print_interfaces()

network_event_scheduler.run_until(20.0)

#network_event_scheduler.generate_throughput_graph(network_event_scheduler.packet_logs)
