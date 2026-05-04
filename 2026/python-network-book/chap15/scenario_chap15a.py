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
    FTPClient,
    FTPServer,
    HTTPSClient,
    HTTPSServer,
)

nes = NetworkEventScheduler(
    seed=7, log_enabled=True, verbose=False, tcp_verbose=True, link_verbose=False
)

node1= Node(
    node_id="n1",
    ip_address="192.168.1.0/24",
    network_event_scheduler=nes,
)
node2 = Node(
    node_id="n2",
    ip_address="192.168.2.1/24",
    network_event_scheduler=nes,
)
switch1 = Switch(
    node_id="s1",
    ip_address="192.168.1.240/24",
    network_event_scheduler=nes,
)
router1 = Router(
    node_id="r1",
    ip_addresses=["192.168.1.254/24", "192.168.2.254/24"],
    network_event_scheduler=nes,
)
dns1 = DNSServer(
    node_id="dns1",
    ip_address="192.168.1.200/24",
    network_event_scheduler=nes,
)
dhcp1 = DHCPServer(
    node_id="dhcp1",
    ip_address="192.168.1.250/24",
    dns_server_ip="192.168.1.200/24",
    start_cidr="192.168.1.0/24",
    network_event_scheduler=nes
)

link1 = Link(
    node1,
    switch1,
    bandwidth=1000000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=nes,
)
link2 = Link(
    switch1,
    router1,
    bandwidth=1000000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=nes,
)
link3 = Link(
    dns1,
    switch1,
    bandwidth=1000000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=nes,
)
link4 = Link(
    dhcp1,
    switch1,
    bandwidth=1000000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=nes,
)
link5 = Link(
    node2,
    router1,
    bandwidth=1000000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=nes,
)



nes.draw()

dns1.add_dns_record("www.example.com", "192.168.2.1/24")

used_ips = ["192.168.1.240/24", "192.168.1.254/24", "192.168.1.200/24", "192.168.1.250/24"]
dhcp1.mark_ips_as_used(used_ips)

shared_files = {
    "index.html": b"<h1>Welcome to Secure example.com!</h1>",
    "secret.txt": b"TopSecretData",
    "large.dat": b"X" * 10000,
}
https_server = HTTPSServer(node2, shared_files=shared_files, verbose=True)
node2.register_application(
    443, "TCP", https_server
)

https_client = HTTPSClient(node1, verbose=True)
node1.register_application(
    0, "TCP", https_client
)

def start_https_download():
    https_client.connect(server_url="www.example.com", server_port=443)
    https_client.get_file("index.html")

nes.schedule_event(2.0, start_https_download)

nes.run_until(10.0)

node1.print_arp_table()
node1.print_url_to_ip_mapping()
node1.print_tcp_connections()
router1.print_arp_table()
router1.print_routing_table()
node2.print_arp_table()
node2.print_tcp_connections()


nes.generate_summary(nes.packet_logs)
nes.generate_throughput_graph(nes.packet_logs)
nes.generate_delay_histogram(nes.packet_logs)
