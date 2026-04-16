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
    log_enabled=True, verbose=True, stp_verbose=False, nat_verbose=True
)

node1 = Node(
    node_id="n1",
    ip_address="192.168.1.0/24",
    network_event_scheduler=network_event_scheduler,
)
node2 = Node(
    node_id="n2",
    ip_address="10.0.0.2/24",
    network_event_scheduler=network_event_scheduler,
)
node3 = Node(
    node_id="n3",
    ip_address="192.168.1.0/24",
    network_event_scheduler=network_event_scheduler,
)
node4 = Node(
    node_id="n4",
    ip_address="192.168.1.0/24",
    network_event_scheduler=network_event_scheduler,
)
node5 = Node(
    node_id="n5",
    ip_address="192.168.1.0/24",
    network_event_scheduler=network_event_scheduler,
)
switch1 = Switch(
    node_id="s1",
    ip_address="192.168.1.240/24",
    network_event_scheduler=network_event_scheduler,
)
router1 = Router(
    node_id="r1",
    ip_addresses=["192.168.1.254/24", "10.0.0.1/24"],
    nat_enabled=True,
    external_ip="10.0.0.1/24",
    network_event_scheduler=network_event_scheduler,
)
dns1 = DNSServer(
    node_id="dns1",
    ip_address="192.168.1.200/24",
    network_event_scheduler=network_event_scheduler,
)
dhcp1 = DHCPServer(
    node_id="dhcp1",
    ip_address="192.168.1.250/24",
    dns_server_ip="192.168.1.200/24",
    start_cidr="192.168.1.0/24",
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
    dns1,
    switch1,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link4 = Link(
    dhcp1,
    switch1,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link5 = Link(
    node2,
    router1,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link6 = Link(
    node3,
    switch1,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link7 = Link(
    node4,
    switch1,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link8 = Link(
    node5,
    switch1,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)


network_event_scheduler.draw()

dns1.add_dns_record("www.example.com", "192.168.2.1/24")

used_ips = [
    "192.168.1.240/24",
    "192.168.1.254/24",
    "192.168.1.200/24",
    "192.168.1.250/24",
]
dhcp1.mark_ips_as_used(used_ips)

node1.start_traffic(
    destination_url="www.example.com",
    bitrate=10000,
    start_time=1.0,
    duration=2.0,
    header_size=50,
    payload_size=10000,
    burstiness=1.0,
)
node2.start_traffic(
    destination_url="www.example.com",
    bitrate=10000,
    start_time=2.0,
    duration=2.0,
    header_size=50,
    payload_size=10000,
    burstiness=1.0,
)
node3.start_traffic(
    destination_url="www.example.com",
    bitrate=10000,
    start_time=3.0,
    duration=2.0,
    header_size=50,
    payload_size=10000,
    burstiness=1.0,
)
node4.start_traffic(
    destination_url="www.example.com",
    bitrate=10000,
    start_time=4.0,
    duration=2.0,
    header_size=50,
    payload_size=10000,
    burstiness=1.0,
)
node5.start_traffic(
    destination_url="www.example.com",
    bitrate=10000,
    start_time=5.0,
    duration=2.0,
    header_size=50,
    payload_size=10000,
    burstiness=1.0,
)

network_event_scheduler.run_until(5.0)

node1.print_url_to_ip_mapping()
router1.print_nat_table()
router1.print_arp_table()
router1.print_routing_table()

network_event_scheduler.generate_summary(network_event_scheduler.packet_logs)

nat_logs = []
for packet_id, log in network_event_scheduler.packet_logs.items():
    for event in log.get("events", []):
        if "NAT" in event.get("event_type", ""):
            nat_logs.append(
                {
                    "packet_id": packet_id,
                    "time": event["time"],
                    "event_type": event["event_type"],
                    "node_id": event.get("node_id", ""),
                }
            )

for log in nat_logs:
    print(log)
