import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from network import NetworkEventScheduler, Node, Link, Switch

network_event_scheduler = NetworkEventScheduler(
    log_enabled=True, verbose=True, stp_verbose=False
)

node1 = Node(
    node_id="n1",
    mac_address="00:1A:2B:3C:4D:5E",
    ip_address="192.168.1.1",
    network_event_scheduler=network_event_scheduler,
)
node2 = Node(
    node_id="n2",
    mac_address="00:1A:2B:3C:4D:5F",
    ip_address="192.168.1.2",
    network_event_scheduler=network_event_scheduler,
)

link1 = Link(
    node1,
    node2,
    bandwidth=100000,
    delay=0.001,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)


network_event_scheduler.draw()

node1.set_traffic(
    destination_mac="00:1A:2B:3C:4D:5F",
    destination_ip="192.168.1.2",
    bitrate=1000,
    start_time=1.0,
    duration=2.0,
    header_size=50,
    payload_size=10000,
    burstiness=1.0,
)

network_event_scheduler.run()

network_event_scheduler.generate_throughput_graph(network_event_scheduler.packet_logs)

