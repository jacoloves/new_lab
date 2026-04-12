import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from network import NetworkEventScheduler, Node, Link, Switch, Router, DNSServer

network_event_scheduler = NetworkEventScheduler(
    log_enabled=True, verbose=True, stp_verbose=True
)

node1 = Node(
    node_id="n1",
    ip_address="192.168.1.1/24",
    dns_server="192.168.1.200/24",
    network_event_scheduler=network_event_scheduler,
)
node2 = Node(
    node_id="n2",
    ip_address="192.168.2.1/24",
    network_event_scheduler=network_event_scheduler,
)
switch1 = Switch(
    node_id="s1",
    ip_address="192.168.1.11/24",
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
    node2,
    router1,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)


network_event_scheduler.draw()

node1.set_traffic(
    destination_ip="192.168.1.200",
    bitrate=10000,
    start_time=1.0,
    duration=2.0,
    header_size=50,
    payload_size=10000,
    burstiness=1.0,
)

network_event_scheduler.run_until(5.0)


def print_arp_logs(packet_logs):
    print("\n" + "=" * 60)
    print("ARP ログ サマリー")
    print("=" * 60)

    for packet_id, log in packet_logs.items():
        arp_events = [event for event in log["events"] if "ARP" in event["event"]]

        if not arp_events:
            continue

        print(f"\nパケットID: {packet_id}")
        print(f"  送信元: {log['source_ip']} ({log['source_mac']})")
        print(f"  宛先: {log['destination_ip']} ({log['destination_mac']})")
        for event in arp_events:
            print(
                f"  Time: {event['time']:.4f}"
                f"  Node: {event['node_id']:<8}"
                f"  Event: {event['event']}"
            )


print_arp_logs(network_event_scheduler.packet_logs)
router1.print_arp_table()
network_event_scheduler.generate_summary(network_event_scheduler.packet_logs)
