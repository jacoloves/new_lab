import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from network import NetworkEventScheduler, Node, Link, Switch

network_event_scheduler = NetworkEventScheduler(
    log_enabled=True, verbose=True, stp_verbose=False
)

node1 = Node(
    node_id="n1",
    mac_address="00:1A:2B:3C:4D:5E",
    network_event_scheduler=network_event_scheduler,
)
node2 = Node(
    node_id="n2",
    mac_address="00:1A:2B:3C:4D:5F",
    network_event_scheduler=network_event_scheduler,
)
node3 = Node(
    node_id="n3",
    mac_address="00:1A:2B:3C:4D:60",
    network_event_scheduler=network_event_scheduler,
)
node4 = Node(
    node_id="n4",
    mac_address="00:1A:2B:3C:4D:61",
    network_event_scheduler=network_event_scheduler,
)
# pattern 1
switch1 = Switch(node_id="s1", network_event_scheduler=network_event_scheduler)
# pattern 2
# switch1 = Switch(node_id="s9", network_event_scheduler=network_event_scheduler)
switch2 = Switch(node_id="s2", network_event_scheduler=network_event_scheduler)
switch3 = Switch(node_id="s3", network_event_scheduler=network_event_scheduler)
switch4 = Switch(node_id="s4", network_event_scheduler=network_event_scheduler)

link1 = Link(
    node1,
    switch1,
    bandwidth=100000,
    delay=0.001,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link2 = Link(
    switch1,
    switch2,
    bandwidth=100000,
    delay=0.001,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link3 = Link(
    switch1,
    switch3,
    bandwidth=100000,
    delay=0.001,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link4 = Link(
    switch1,
    switch4,
    bandwidth=100000,
    delay=0.001,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link5 = Link(
    switch2,
    switch3,
    bandwidth=100000,
    delay=0.001,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link6 = Link(
    switch2,
    switch4,
    bandwidth=100000,
    delay=0.001,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link7 = Link(
    switch3,
    switch4,
    bandwidth=100000,
    delay=0.001,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link8 = Link(
    node2,
    switch3,
    bandwidth=100000,
    delay=0.001,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link9 = Link(
    node3,
    switch2,
    bandwidth=100000,
    delay=0.001,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)
link10 = Link(
    node4,
    switch4,
    bandwidth=100000,
    delay=0.001,
    loss_rate=0.0,
    network_event_scheduler=network_event_scheduler,
)


network_event_scheduler.draw()

node1.set_traffic(
    destination_mac="00:1A:2B:3C:4D:5F",
    bitrate=1000,
    start_time=1.0,
    duration=5.0,
    burstiness=1.0,
    header_size=40,
    payload_size=85,
)

node2.set_traffic(
    destination_mac="00:1A:2B:3C:4D:5E",
    bitrate=1000,
    start_time=3.0,
    duration=3.0,
    burstiness=1.0,
    header_size=40,
    payload_size=85,
)

network_event_scheduler.run()

switch1.print_forwarding_table()
switch2.print_forwarding_table()
switch3.print_forwarding_table()
switch4.print_forwarding_table()
