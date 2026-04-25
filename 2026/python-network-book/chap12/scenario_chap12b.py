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
    seed=7, log_enabled=True, verbose=True, stp_verbose=False, tcp_verbose=True
)

node1 = Node(
    node_id="n1",
    ip_address="192.168.1.0/24",
    network_event_scheduler=network_event_scheduler,
)
node2 = Node(
    node_id="n2",
    ip_address="192.168.2.1/24",
    network_event_scheduler=network_event_scheduler,
)
switch1 = Switch(
    node_id="s1",
    ip_address="192.168.1.240/24",
    network_event_scheduler=network_event_scheduler,
)
router1 = Router(
    node_id="r1",
    ip_addresses=["192.168.1.254/24", "192.168.2.254/24"],
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


network_event_scheduler.draw()

dns1.add_dns_record("www.example.com", "192.168.2.1/24")

used_ips = [
    "192.168.1.240/24",
    "192.168.1.254/24",
    "192.168.1.200/24",
    "192.168.1.250/24",
]
dhcp1.mark_ips_as_used(used_ips)

node1.start_tcp_traffic(
    destination_url="www.example.com",
    bitrate=1000000000,
    start_time=1.0,
    duration=5.0,
    header_size=50,
    payload_size=100,
)

network_event_scheduler.run_until(10.0)

node1.print_arp_table()
node1.print_url_to_ip_mapping()
node1.print_tcp_connections()
router1.print_arp_table()
router1.print_routing_table()
node2.print_arp_table()
node2.print_tcp_connections()

network_event_scheduler.generate_summary(network_event_scheduler.packet_logs)
network_event_scheduler.plot_cwnd_log()
