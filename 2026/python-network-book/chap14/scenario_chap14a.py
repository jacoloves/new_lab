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
)

nes = NetworkEventScheduler(
    seed=7, log_enabled=True, verbose=False, stp_verbose=False, tcp_verbose=True
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
    ip_addresses=["192.168.1.200/24", "192.168.2.254/24"],
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

ftp_server = FTPServer(node2, shared_files={}, verbose=True)
node2.register_application(21, "TCP", ftp_server)
ftp_client = FTPClient(node1, verbose=False)
node1.register_application(0, "TCP", ftp_client)

file_path = 'data/cat.jpg'
with open(file_path, 'rb') as f:
    file_data = f.read()
ftp_server.shared_files["cat.jpg"] = file_data

def start_ftp_transfer():
    ftp_client.connect(server_url="www.example.com", server_port=21)
    ftp_client.retrieve_file("cat.jpg")
nes.schedule_event(1.0, start_ftp_transfer)

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

nes.plot_cwnd_log()
ftp_connections = [ck for ck, info in node2.tcp_connections.items() if info.get('transfer_info') and info['transfer_info'].get('progress')]
if ftp_connections:
    connection_key = ftp_connections[0]
    nes.plot_transfer_progress(node2, connection_key)
