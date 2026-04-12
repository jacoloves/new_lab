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
# service.example.net の宛先ノード
node3 = Node(
    node_id="n3",
    ip_address="192.168.1.2/24",
    network_event_scheduler=network_event_scheduler,
)
# api.example.org の宛先ノード
node4 = Node(
    node_id="n4",
    ip_address="192.168.1.3/24",
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
# node3, node4 を switch1 に接続
link5 = Link(
    node3,
    switch1,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link6 = Link(
    node4,
    switch1,
    bandwidth=100000,
    delay=0.01,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)


network_event_scheduler.draw()

# DNSレコードの登録
dns1.add_dns_record("www.example.com", "192.168.1.1")
dns1.add_dns_record("service.example.net", "192.168.1.2")
dns1.add_dns_record("api.example.org", "192.168.1.3")

# ドメイン名でトラフィックを設定（DNS解決 → ARP解決 → データ送信の流れを観察）
node1.start_traffic(
    destination_url="www.example.com",
    bitrate=10000,
    start_time=1.0,
    duration=2.0,
    header_size=50,
    payload_size=1000,
    burstiness=1.0,
)
node1.start_traffic(
    destination_url="service.example.net",
    bitrate=10000,
    start_time=1.5,
    duration=2.0,
    header_size=50,
    payload_size=1000,
    burstiness=1.0,
)
node1.start_traffic(
    destination_url="api.example.org",
    bitrate=10000,
    start_time=2.0,
    duration=2.0,
    header_size=50,
    payload_size=1000,
    burstiness=1.0,
)

network_event_scheduler.run_until(6.0)


def print_arp_logs(packet_logs):
    """ARPパケットのログを抽出して表示する"""
    print("\n" + "=" * 60)
    print("ARP ログ サマリー")
    print("=" * 60)

    for packet_id, log in packet_logs.items():
        arp_events = [event for event in log["events"] if "ARP" in event["event"]]

        if not arp_events:
            continue

        print(f"\nパケットID: {packet_id}")
        print(f"  送信元: {log['source_ip']} ({log['source_mac']})")
        print(f"  宛先:   {log['destination_ip']} ({log['destination_mac']})")
        for event in arp_events:
            print(
                f"  Time: {event['time']:.4f}"
                f"  Node: {event['node_id']:<8}"
                f"  Event: {event['event']}"
            )


def print_dns_logs(packet_logs):
    """DNSパケットのログを抽出して表示する"""
    print("\n" + "=" * 60)
    print("DNS ログ サマリー")
    print("=" * 60)

    dns_event_keywords = ("DNS query", "DNS response", "DNS packet")

    for packet_id, log in packet_logs.items():
        dns_events = [
            event for event in log["events"]
            if any(kw in event["event"] for kw in dns_event_keywords)
        ]

        if not dns_events:
            continue

        print(f"\nパケットID: {packet_id}")
        print(f"  送信元: {log['source_ip']} ({log['source_mac']})")
        print(f"  宛先:   {log['destination_ip']} ({log['destination_mac']})")
        for event in dns_events:
            print(
                f"  Time: {event['time']:.4f}"
                f"  Node: {event['node_id']:<8}"
                f"  Event: {event['event']}"
            )


print_dns_logs(network_event_scheduler.packet_logs)
print_arp_logs(network_event_scheduler.packet_logs)
node1.print_url_to_ip_mapping()
network_event_scheduler.generate_summary(network_event_scheduler.packet_logs)
