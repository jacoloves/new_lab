import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from network import NetworkEventScheduler, Node, Link, Switch, Router

network_event_scheduler = NetworkEventScheduler(
    log_enabled=True, verbose=False, stp_verbose=True, routing_verbose=True
)

n1 = Node(
    node_id="n1",
    mac_address="00:AA:BB:CC:DD:01",
    ip_address="192.168.1.10/24",
    network_event_scheduler=network_event_scheduler,
)
n2 = Node(
    node_id="n2",
    mac_address="00:AA:BB:CC:DD:02",
    ip_address="192.168.2.10/24",
    network_event_scheduler=network_event_scheduler,
)
n3 = Node(
    node_id="n3",
    mac_address="00:AA:BB:CC:DD:03",
    ip_address="192.168.3.10/24",
    network_event_scheduler=network_event_scheduler,
)
r1 = Router(
    node_id="r1",
    ip_address=["192.168.1.1/24", "10.1.2.1/24", "10.1.3.1/24"],
    network_event_scheduler=network_event_scheduler,
)
r2 = Router(
    node_id="r2",
    ip_address=["10.1.2.2/24", "10.2.4.2/24", "192.168.2.1/24"],
    network_event_scheduler=network_event_scheduler,
)
r3 = Router(
    node_id="r3",
    ip_address=["10.1.3.3/24", "10.3.4.3/24", "10.3.5.3/24"],
    network_event_scheduler=network_event_scheduler,
)
r4 = Router(
    node_id="r4",
    ip_address=["10.2.4.4/24", "10.3.4.4/24"],
    network_event_scheduler=network_event_scheduler,
)
r5 = Router(
    node_id="r5",
    ip_address=["10.3.5.5/24", "192.168.3.1/24"],
    network_event_scheduler=network_event_scheduler,
)

link1 = Link(
    n1,
    r1,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link2 = Link(
    r1,
    r2,
    bandwidth=20000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link3 = Link(
    r1,
    r3,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link4 = Link(
    r2,
    r4,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link5 = Link(
    r3,
    r4,
    bandwidth=300000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link6 = Link(
    r3,
    r5,
    bandwidth=200000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link7 = Link(
    r5,
    n3,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)

n1.set_traffic(
    destination_mac="00:AA:BB:CC:DD:02",
    destination_ip="192.168.2.10",
    bitrate=10000,
    start_time=15.0,
    duration=2.0,
    header_size=50,
    payload_size=10000,
    burstiness=1.0,
)
n1.set_traffic(
    destination_mac="00:AA:BB:CC:DD:03",
    destination_ip="192.168.3.10",
    bitrate=10000,
    start_time=15.0,
    duration=2.0,
    header_size=50,
    payload_size=10000,
    burstiness=1.0,
)

network_event_scheduler.run_until(25.0)

r1.print_routing_table()
r2.print_routing_table()
r3.print_routing_table()
r4.print_routing_table()
r5.print_routing_table()

network_event_scheduler.generate_summary(network_event_scheduler.packet_logs)
