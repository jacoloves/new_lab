from network import NetworkEventScheduler, Node, Link, Switch

network_event_scheduler = NetworkEventScheduler(log_enabled=True, verbose=False)

node1 = Node(
    node_id="n1", address="00:01", network_event_scheduler=network_event_scheduler
)
node2 = Node(
    node_id="n2", address="00:02", network_event_scheduler=network_event_scheduler
)
switch1 = Switch(node_id="s1", network_event_scheduler=network_event_scheduler)

link1 = Link(
    node1,
    switch1,
    bandwidth=100000,
    delay=0.001,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link2 = Link(
    node2,
    switch1,
    bandwidth=100000,
    delay=0.001,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)

switch1.update_forwarding_table(node1.address, link1)
switch1.update_forwarding_table(node2.address, link2)

network_event_scheduler.draw()

node1.set_traffic(
    destination="00:02",
    bitrate=10000,
    start_time=1.0,
    duration=10.0,
    burstiness=1.0,
    header_size=40,
    payload_size=85,
)

network_event_scheduler.run()

network_event_scheduler.generate_summary(network_event_scheduler.packet_logs)
network_event_scheduler.generate_throughput_graph(network_event_scheduler.packet_logs)
network_event_scheduler.generate_delay_histogram(network_event_scheduler.packet_logs)
