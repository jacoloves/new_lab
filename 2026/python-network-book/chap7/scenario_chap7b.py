import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from network import NetworkEventScheduler, Node, Link, Switch, Router

network_event_scheduler = NetworkEventScheduler(
    log_enabled=True, verbose=True, stp_verbose=True
)

node1 = Node(
    node_id="n1",
    ip_address="192.168.1.1/24",
    network_event_scheduler=network_event_scheduler,
)
node2 = Node(
    node_id="n2",
    ip_address="192.168.2.1/24",
    network_event_scheduler=network_event_scheduler,
)

switch1 = Switch(
    node_id="s1",
    ip_address="192.168.1.11/24",
    network_event_scheduler=network_event_scheduler,
)
switch2 = Switch(
    node_id="s2",
    ip_address="192.168.2.11/24",
    network_event_scheduler=network_event_scheduler,
)

router1 = Router(
    node_id="r1",
    ip_address=["192.168.1.254/24", "10.1.1.1/24"],
    network_event_scheduler=network_event_scheduler,
)
router2 = Router(
    node_id="r2",
    ip_address=["192.168.2.254/24", "10.1.1.2/24"],
    network_event_scheduler=network_event_scheduler,
)

link1 = Link(
    node1,
    switch1,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link2 = Link(
    switch1,
    router1,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link3 = Link(
    router1,
    router2,
    bandwidth=200000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link4 = Link(
    router2,
    switch2,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link5 = Link(
    switch2,
    node2,
    bandwidth=200000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)

node1.add_to_arp_table(node2.ip_address, router1.get_mac_address(link2))
node2.add_to_arp_table(node1.ip_address, router2.get_mac_address(link4))
router1.add_to_arp_table(node1.ip_address, node1.mac_address)
router1.add_to_arp_table(node2.ip_address, router2.get_mac_address(link3))
router2.add_to_arp_table(node1.ip_address, router1.get_mac_address(link3))
router2.add_to_arp_table(node2.ip_address, node2.mac_address)

network_event_scheduler.draw()

node1.set_traffic(
    destination_ip="192.168.2.1/24",
    bitrate=10000,
    start_time=1.0,
    duration=2.0,
    header_size=50,
    payload_size=10000,
    burstiness=1.0,
)

network_event_scheduler.run_until(5.0)

switch1.print_forwarding_table()
switch2.print_forwarding_table()

router1.print_interfaces()
router2.print_interfaces()

router1.print_routing_table()
router2.print_routing_table()

network_event_scheduler.generate_summary(network_event_scheduler.packet_logs)
