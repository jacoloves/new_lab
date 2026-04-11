import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from network import NetworkEventScheduler, Node, Link, Switch, Router

network_event_scheduler = NetworkEventScheduler(
    log_enabled=True, verbose=True, stp_verbose=True
)

node1 = Node(
    node_id="n1",
    ip_address="192.168.10.1/24",
    network_event_scheduler=network_event_scheduler,
)
node2 = Node(
    node_id="n2",
    ip_address="192.168.20.1/24",
    network_event_scheduler=network_event_scheduler,
)
node3 = Node(
    node_id="n3",
    ip_address="192.168.30.1/24",
    network_event_scheduler=network_event_scheduler,
)

switch1 = Switch(
    node_id="s1",
    ip_address="192.168.10.11/24",
    network_event_scheduler=network_event_scheduler,
)
switch2 = Switch(
    node_id="s2",
    ip_address="192.168.20.11/24",
    network_event_scheduler=network_event_scheduler,
)
switch3 = Switch(
    node_id="s3",
    ip_address="192.168.30.11/24",
    network_event_scheduler=network_event_scheduler,
)

router1 = Router(
    node_id="r1",
    ip_address=["192.168.10.254/24", "10.1.1.11/24", "10.1.1.12/24"],
    network_event_scheduler=network_event_scheduler,
)
router2 = Router(
    node_id="r2",
    ip_address=["192.168.20.254/24", "10.1.1.21/24", "10.1.1.22/24"],
    network_event_scheduler=network_event_scheduler,
)
router3 = Router(
    node_id="r3",
    ip_address=["192.168.30.254/24", "10.1.1.31/24", "10.1.1.32/24"],
    network_event_scheduler=network_event_scheduler,
)

link1a = Link(
    node1,
    switch1,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link1b = Link(
    switch1,
    router1,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link2a = Link(
    node2,
    switch2,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link2b = Link(
    switch2,
    router2,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link3a = Link(
    node3,
    switch3,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link3b = Link(
    switch3,
    router3,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link4a = Link(
    router1,
    router2,
    bandwidth=200000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link4b = Link(
    router2,
    router3,
    bandwidth=200000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link4c = Link(
    router3,
    router1,
    bandwidth=200000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)

### ここに設定を書く

node1.add_to_arp_table(node2.ip_address, router1.get_mac_address(link1b))
node1.add_to_arp_table(node3.ip_address, router1.get_mac_address(link1b))

node2.add_to_arp_table(node1.ip_address, router2.get_mac_address(link2b))
node2.add_to_arp_table(node3.ip_address, router2.get_mac_address(link2b))

node3.add_to_arp_table(node1.ip_address, router3.get_mac_address(link3b))
node3.add_to_arp_table(node2.ip_address, router3.get_mac_address(link3b))

router1.add_to_arp_table(node1.ip_address, node1.mac_address)
router1.add_to_arp_table(node2.ip_address, router2.get_mac_address(link4a))
router1.add_to_arp_table(node3.ip_address, router3.get_mac_address(link4c))

router2.add_to_arp_table(node2.ip_address, node2.mac_address)
router2.add_to_arp_table(node1.ip_address, router1.get_mac_address(link4a))
router2.add_to_arp_table(node3.ip_address, router3.get_mac_address(link4b))

router3.add_to_arp_table(node3.ip_address, node3.mac_address)
router3.add_to_arp_table(node1.ip_address, router1.get_mac_address(link4c))
router3.add_to_arp_table(node2.ip_address, router2.get_mac_address(link4b))
###


network_event_scheduler.draw()

node1.set_traffic(
    destination_ip="192.168.20.1/24",
    bitrate=10000,
    start_time=1.0,
    duration=2.0,
    header_size=50,
    payload_size=10000,
    burstiness=1.0,
)
node1.set_traffic(
    destination_ip="192.168.30.1/24",
    bitrate=10000,
    start_time=1.0,
    duration=2.0,
    header_size=50,
    payload_size=10000,
    burstiness=1.0,
)
node2.set_traffic(
    destination_ip="192.168.10.1/24",
    bitrate=10000,
    start_time=1.0,
    duration=2.0,
    header_size=50,
    payload_size=10000,
    burstiness=1.0,
)
node2.set_traffic(
    destination_ip="192.168.30.1/24",
    bitrate=10000,
    start_time=1.0,
    duration=2.0,
    header_size=50,
    payload_size=10000,
    burstiness=1.0,
)
node3.set_traffic(
    destination_ip="192.168.10.1/24",
    bitrate=10000,
    start_time=1.0,
    duration=2.0,
    header_size=50,
    payload_size=10000,
    burstiness=1.0,
)
node3.set_traffic(
    destination_ip="192.168.20.1/24",
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
