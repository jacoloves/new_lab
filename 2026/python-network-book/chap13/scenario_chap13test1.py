import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from network import (
    NetworkEventScheduler,
    Node,
    Link,
    Switch,
    Router,
    DNSServer,
    DHCPServer,
)

network_event_scheduler = NetworkEventScheduler(
    seed=7, log_enabled=True, verbose=False, stp_verbose=False, tcp_verbose=True
)

src1 = Node(
    node_id="n1",
    ip_address="192.168.1.1/24",
    network_event_scheduler=network_event_scheduler,
)
src2 = Node(
    node_id="n2",
    ip_address="192.168.1.2/24",
    network_event_scheduler=network_event_scheduler,
)
switch1 = Switch(
    node_id="s1",
    ip_address="192.168.1.240/24",
    network_event_scheduler=network_event_scheduler,
)
dst1 = Node(
    node_id="d1",
    ip_address="192.168.1.250/24",
    network_event_scheduler=network_event_scheduler,
)

link1 = Link(
    src1,
    switch1,
    bandwidth=10000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link2 = Link(
    src2,
    switch1,
    bandwidth=10000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link3 = Link(
    switch1,
    dst1,
    bandwidth=100,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)


network_event_scheduler.draw()


src1.start_udp_traffic(
    destination_url="192.168.1.250/24",
    bitrate=1000,
    start_time=1.0,
    duration=5.0,
    header_size=28,
    payload_size=72,
    dscp=0,
)
src2.start_udp_traffic(
    destination_url="192.168.1.250/24",
    bitrate=1000,
    start_time=1.0,
    duration=5.0,
    header_size=28,
    payload_size=72,
    dscp=16,
)

network_event_scheduler.run_until(10.0)


network_event_scheduler.generate_summary(network_event_scheduler.packet_logs)
network_event_scheduler.generate_throughput_graph(network_event_scheduler.packet_logs)
network_event_scheduler.generate_delay_histogram(network_event_scheduler.packet_logs)
