import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from network import NetworkEventScheduler, Node, Link, Switch

network_event_scheduler = NetworkEventScheduler(log_enabled=True, verbose=False)

node1 = Node(
    node_id="n1",
    mac_address="00:1A:2B:3C:4A:5B",
    network_event_scheduler=network_event_scheduler,
)
node2 = Node(
    node_id="n2",
    mac_address="00:1A:2B:3C:4A:5C",
    network_event_scheduler=network_event_scheduler,
)
node3 = Node(
    node_id="n3",
    mac_address="00:1A:2B:3C:4B:5B",
    network_event_scheduler=network_event_scheduler,
)
node4 = Node(
    node_id="n4",
    mac_address="00:1A:2B:3C:4B:5C",
    network_event_scheduler=network_event_scheduler,
)

switch1 = Switch(node_id="s1", network_event_scheduler=network_event_scheduler)
switch2 = Switch(node_id="s2", network_event_scheduler=network_event_scheduler)

nlink1 = Link(
    node1,
    switch1,
    bandwidth=100000,
    delay=0.001,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
nlink2 = Link(
    node2,
    switch1,
    bandwidth=100000,
    delay=0.001,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
nlink3 = Link(
    node3,
    switch2,
    bandwidth=100000,
    delay=0.001,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
nlink4 = Link(
    node4,
    switch2,
    bandwidth=100000,
    delay=0.001,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
sslink = Link(
    switch1,
    switch2,
    bandwidth=100000,
    delay=0.001,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)


switch1.update_forwarding_table(node1.mac_address, nlink1)
switch1.update_forwarding_table(node2.mac_address, nlink2)
switch2.update_forwarding_table(node3.mac_address, nlink3)
switch2.update_forwarding_table(node4.mac_address, nlink4)

switch1.update_forwarding_table(node3.mac_address, sslink)
switch1.update_forwarding_table(node4.mac_address, sslink)
switch2.update_forwarding_table(node1.mac_address, sslink)
switch2.update_forwarding_table(node2.mac_address, sslink)


network_event_scheduler.draw()

node1.set_traffic(
    destination_mac="00:1A:2B:3C:4B:5B",
    bitrate=100000,
    start_time=1.0,
    duration=11.0,
    burstiness=1.0,
    header_size=40,
    payload_size=85,
)
node2.set_traffic(
    destination_mac="00:1A:2B:3C:4B:5C",
    bitrate=10000,
    start_time=2.0,
    duration=10.0,
    burstiness=1.0,
    header_size=40,
    payload_size=85,
)
node3.set_traffic(
    destination_mac="00:1A:2B:3C:4A:5B",
    bitrate=10000,
    start_time=1.0,
    duration=10.0,
    burstiness=2.0,
    header_size=40,
    payload_size=85,
)
node4.set_traffic(
    destination_mac="00:1A:2B:3C:4A:5C",
    bitrate=100000,
    start_time=1.0,
    duration=10.0,
    burstiness=1.0,
    header_size=40,
    payload_size=85,
)

network_event_scheduler.run()

network_event_scheduler.generate_summary(network_event_scheduler.packet_logs)
network_event_scheduler.generate_throughput_graph(network_event_scheduler.packet_logs)
network_event_scheduler.generate_delay_histogram(network_event_scheduler.packet_logs)
