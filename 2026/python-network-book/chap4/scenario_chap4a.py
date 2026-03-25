import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from network import NetworkEventScheduler, Node, Link, Switch

network_event_scheduler = NetworkEventScheduler(log_enabled=True, verbose=False)

node1 = Node(
    node_id="n1",
    mac_address="00:1A:2B:3C:4D:5E",
    network_event_scheduler=network_event_scheduler,
)
node2 = Node(
    node_id="n2",
    mac_address="00:1A:2B:3C:4D:5F",
    network_event_scheduler=network_event_scheduler,
)
node3 = Node(
    node_id="n3",
    mac_address="00:1A:2B:3C:4D:60",
    network_event_scheduler=network_event_scheduler,
)
node4 = Node(
    node_id="n4",
    mac_address="00:1A:2B:3C:4D:61",
    network_event_scheduler=network_event_scheduler,
)
switch1 = Switch(node_id="s1", network_event_scheduler=network_event_scheduler)

link1 = Link(
    node1,
    switch1,
    bandwidth=100000,
    delay=0.001,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link2 = Link(
    node2,
    switch1,
    bandwidth=100000,
    delay=0.001,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link3 = Link(
    node3,
    switch1,
    bandwidth=100000,
    delay=0.001,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link4 = Link(
    node4,
    switch1,
    bandwidth=100000,
    delay=0.001,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)

network_event_scheduler.draw()

node1.set_traffic(
    destination_mac="00:1A:2B:3C:4D:5F",
    bitrate=10000,
    start_time=1.0,
    duration=2.0,
    burstiness=1.0,
    header_size=40,
    payload_size=85,
)
node2.set_traffic(
    destination_mac="00:1A:2B:3C:4D:61",
    bitrate=10000,
    start_time=1.0,
    duration=2.0,
    burstiness=1.0,
    header_size=40,
    payload_size=85,
)

network_event_scheduler.run()

switch1.print_forwarding_table()

# network_event_scheduler.generate_summary(network_event_scheduler.packet_logs)
# network_event_scheduler.generate_throughput_graph(network_event_scheduler.packet_logs)
# network_event_scheduler.generate_delay_histogram(network_event_scheduler.packet_logs)
