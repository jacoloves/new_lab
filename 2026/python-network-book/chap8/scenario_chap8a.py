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
    ip_address="192.168.1.2/24",
    network_event_scheduler=network_event_scheduler,
)
node3 = Node(
    node_id="n3",
    ip_address="192.168.1.3/24",
    network_event_scheduler=network_event_scheduler,
)
node4 = Node(
    node_id="n4",
    ip_address="192.168.1.4/24",
    network_event_scheduler=network_event_scheduler,
)

switch1 = Switch(
    node_id="s1",
    ip_address="192.168.1.11/24",
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
    node2,
    switch1,
    bandwidth=200000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link3 = Link(
    node3,
    switch1,
    bandwidth=200000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link4 = Link(
    node4,
    switch1,
    bandwidth=200000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)


network_event_scheduler.draw()

node1.set_traffic(
    destination_ip="192.168.1.2/24",
    bitrate=10000,
    start_time=1.0,
    duration=2.0,
    header_size=50,
    payload_size=10000,
    burstiness=1.0,
)
node2.set_traffic(
    destination_ip="192.168.1.3/24",
    bitrate=10000,
    start_time=1.0,
    duration=2.0,
    header_size=50,
    payload_size=10000,
    burstiness=1.0,
)
node3.set_traffic(
    destination_ip="192.168.1.4/24",
    bitrate=10000,
    start_time=1.0,
    duration=2.0,
    header_size=50,
    payload_size=10000,
    burstiness=1.0,
)
node4.set_traffic(
    destination_ip="192.168.1.1/24",
    bitrate=10000,
    start_time=1.0,
    duration=2.0,
    header_size=50,
    payload_size=10000,
    burstiness=1.0,
)

network_event_scheduler.run_until(5.0)

node1.print_arp_table()
node2.print_arp_table()
node3.print_arp_table()
node4.print_arp_table()
switch1.print_forwarding_table()

network_event_scheduler.generate_summary(network_event_scheduler.packet_logs)
