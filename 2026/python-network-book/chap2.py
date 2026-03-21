import sys
import matplotlib.pyplot as plt

from node2 import NetworkEventScheduler, Node, Link

nes = NetworkEventScheduler(log_enabled=True, verbose=True)

header_size = 40
payload_size = 960
duration = 5.0

# === 実験A: 帯域幅の違い（delay固定） ===

# A-1: 1 Mbps
nodeA1 = Node(node_id=1, address="A1", network_event_scheduler=nes)
nodeA2 = Node(node_id=2, address="A2", network_event_scheduler=nes)
Link(nodeA1, nodeA2, bandwidth=1_000_000, delay=0.01, loss_rate=0.0, network_event_scheduler=nes)
nodeA1.set_traffic(destination="A2", bitrate=500_000, start_time=0.0, duration=duration, burstiness=1.0, header_size=header_size, payload_size=payload_size)

# A-2: 10 Mbps
nodeB1 = Node(node_id=3, address="B1", network_event_scheduler=nes)
nodeB2 = Node(node_id=4, address="B2", network_event_scheduler=nes)
Link(nodeB1, nodeB2, bandwidth=10_000_000, delay=0.01, loss_rate=0.0, network_event_scheduler=nes)
nodeB1.set_traffic(destination="B2", bitrate=5_000_000, start_time=0.0, duration=duration, burstiness=1.0, header_size=header_size, payload_size=payload_size)


# === 実験B: 遅延の違い（帯域幅固定） ===
# B-1: 遅延 1ms（LAN相当）
nodeC1 = Node(node_id=5, address="C1", network_event_scheduler=nes)
nodeC2 = Node(node_id=6, address="C2", network_event_scheduler=nes)
Link(nodeC1, nodeC2, bandwidth=10_000_000, delay=0.001, loss_rate=0.0, network_event_scheduler=nes)
nodeC1.set_traffic(destination="C2", bitrate=5_000_000, start_time=0.0, duration=duration, burstiness=1.0, header_size=header_size, payload_size=payload_size)

# B-2: 遅延 100ms（広域WAN相当）
nodeD1 = Node(node_id=7, address="D1", network_event_scheduler=nes)
nodeD2 = Node(node_id=8, address="D2", network_event_scheduler=nes)
Link(nodeD1, nodeD2, bandwidth=10_000_000, delay=0.1, loss_rate=0.0, network_event_scheduler=nes)
nodeD1.set_traffic(destination="D2", bitrate=5_000_000, start_time=0.0, duration=duration, burstiness=1.0, header_size=header_size, payload_size=payload_size)
"""

"""
# --- 帯域幅 1 Mbps ---
node1 = Node(node_id=1, address="00:01", network_event_scheduler=nes)
node2 = Node(node_id=2, address="00:02", network_event_scheduler=nes)
Link(node1, node2, bandwidth=1_000_000, delay=0.0, loss_rate=0.0, network_event_scheduler=nes)
node1.set_traffic(destination="00:02", bitrate=1_000_000, start_time=0.0, duration=1.0, burstiness=1.0, header_size=header_size, payload_size=payload_size)

# --- 帯域幅 10 Mbps ---
node3 = Node(node_id=3, address="00:03", network_event_scheduler=nes)
node4 = Node(node_id=4, address="00:04", network_event_scheduler=nes)
Link(node3, node4, bandwidth=10_000_000, delay=0.0, loss_rate=0.0, network_event_scheduler=nes)
node3.set_traffic(destination="00:04", bitrate=10_000_000, start_time=0.0, duration=1.0, burstiness=1.0, header_size=header_size, payload_size=payload_size)

# --- 帯域幅 100 Mbps ---
node5 = Node(node_id=5, address="00:05", network_event_scheduler=nes)
node6 = Node(node_id=6, address="00:06", network_event_scheduler=nes)
Link(node5, node6, bandwidth=100_000_000, delay=0.0, loss_rate=0.0, network_event_scheduler=nes)
node5.set_traffic(destination="00:06", bitrate=100_000_000, start_time=0.0, duration=1.0, burstiness=1.0, header_size=header_size, payload_size=payload_size)

nes.run()
nes.generate_summary(nes.packet_logs)
nes.generate_throughput_graph(nes.packet_logs)
nes.generate_delay_histogram(nes.packet_logs)

"""
node1 = Node(node_id=1, address="00:01", network_event_scheduler=nes)
node2 = Node(node_id=2, address="00:02", network_event_scheduler=nes)

link1 = Link(node1, node2, bandwidth=100000, delay=0.001, loss_rate=0.2, network_event_scheduler=nes)

header_size = 40
payload_size = 85
node1.set_traffic(destination="00:02", bitrate=100000000, start_time=1.0, duration=10.0, burstiness=1.0, header_size=header_size, payload_size=payload_size)

nes.run()
nes.print_packet_logs()
nes.generate_summary(nes.packet_logs)
nes.generate_throughput_graph(nes.packet_logs)
nes.generate_delay_histogram(nes.packet_logs)
"""
