import random
import re
import uuid
from ipaddress import ip_interface, ip_network
from random import randint

from .packet import ARPPacket, DNSPacket, Packet, DHCPPacket, TCPPacket, UDPPacket
from .router import Router
from network import packet


class Node:
    def __init__(
        self,
        node_id,
        ip_address,
        network_event_scheduler,
        mac_address=None,
        dns_server=None,
        mtu=1500,
        default_route=None,
    ):
        self.node_id = node_id
        self.network_event_scheduler = network_event_scheduler
        self.ip_address = ip_address
        if mac_address is None:
            self.mac_address = self.generate_mac_address()
        else:
            if not self.is_valid_mac_address(mac_address):
                raise ValueError("無効なMACアドレス形式です。")
            self.mac_address = mac_address
        self.links = []
        self.used_ports = set()
        self.port_mapping = {}
        self.tcp_connections = {}
        self.window_size = 4
        self.max_attempts = 3
        self.windows = {}
        self.timeout_interval = 2
        self.scheduled_timeouts = {}
        self.pending_tcp_data = {}
        self.arp_table = {}
        self.waiting_for_arp_reply = {}
        self.dns_server_ip = dns_server
        self.url_to_ip_mapping = {}
        self.waiting_for_dns_reply = {}
        self.mtu = mtu
        self.fragmented_packets = {}
        self.default_route = default_route
        label = f"Node {node_id}\n{self.mac_address}"

        self.schedule_dhcp_packet()
        self.network_event_scheduler.add_node(node_id, label, ip_addresses=[ip_address])

    def is_valid_mac_address(self, mac_address):
        mac_format = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")
        return bool(mac_format.match(mac_address))

    def is_valid_cidr_notation(self, ip_address):
        try:
            ip_network(ip_address, strict=False)
            return True
        except ValueError:
            return False

    def is_network_address(self, address):
        try:
            interface = ip_interface(address)
            network = ip_network(address, strict=False)
            return (
                interface.ip == network.network_address
                and interface.network.prefixlen == network.prefixlen
            )
        except ValueError:
            return False

    def add_link(self, link, ip_address=None):
        if link not in self.links:
            self.links.append(link)

    def generate_mac_address(self):
        return ":".join(
            [
                "{:02x}".format(uuid.uuid4().int >> elements & 0xFF)
                for elements in range(0, 12, 2)
            ]
        )

    def select_available_port(self):
        for port in range(1024, 49152):
            if port not in self.used_ports:
                self.used_ports.add(port)
                return port
        raise Exception("No available ports")

    def select_random_port(self):
        return random.randint(1024, 49151)

    def assign_destination_port(self, source_port):
        destination_port = self.select_random_port()
        self.port_mapping[source_port] = destination_port
        return destination_port

    def get_destination_port(self, source_port):
        if source_port not in self.port_mapping:
            return self.assign_destination_port(source_port)
        return self.port_mapping[source_port]

    def schedule_dhcp_packet(self):
        if self.is_network_address(self.ip_address):
            initial_delay = random.uniform(0.5, 0.6)
            self.network_event_scheduler.schedule_event(
                self.network_event_scheduler.current_time + initial_delay,
                self.send_dhcp_discover,
            )

    def send_dhcp_discover(self):
        dhcp_discover_packet = DHCPPacket(
            source_mac=self.mac_address,
            destination_mac="FF:FF:FF:FF:FF:FF",
            source_ip="0.0.0.0/32",
            destination_ip="255.255.255.255/32",
            message_type="DISCOVER",
            network_event_scheduler=self.network_event_scheduler,
        )
        self.network_event_scheduler.log_packet_info(
            dhcp_discover_packet, "DHCP Discover sent", self.node_id
        )
        self._send_packet(dhcp_discover_packet)

    def send_dhcp_request(self, requested_ip):
        dhcp_request_packet = DHCPPacket(
            source_mac=self.mac_address,
            destination_mac="FF:FF:FF:FF:FF:FF",
            source_ip="0.0.0.0/32",
            destination_ip="255.255.255.255/32",
            message_type="REQUEST",
            network_event_scheduler=self.network_event_scheduler,
        )
        dhcp_request_packet.dhcp_data = {"requested_ip": requested_ip}
        self.network_event_scheduler.log_packet_info(
            dhcp_request_packet, "DHCP Request sent", self.node_id
        )
        self._send_packet(dhcp_request_packet)

    def add_to_arp_table(self, ip_address, mac_address):
        self.arp_table[ip_address] = mac_address

    def get_mac_address_from_ip(self, ip_address):
        return self.arp_table.get(ip_address, None)

    def print_arp_table(self):
        print(f"ARPテーブル(ルータ {self.node_id}) :")
        for ip_address, mac_address in self.arp_table.items():
            print(f"IPアドレス: {ip_address} -> MACアドレス: {mac_address}")

    def mark_ip_as_used(self, ip_address):
        pass

    def add_dns_record(self, domain_name, ip_address):
        self.url_to_ip_mapping[domain_name] = ip_address
        print(f"{self.node_id} DNS record added: {domain_name} -> {ip_address}")

    def process_ARP_packet(self, packet):
        if packet.header["destination_mac"] == "FF:FF:FF:FF:FF:FF":
            self.network_event_scheduler.log_packet_info(
                packet, "arrived", self.node_id
            )
            packet.set_arrived(self.network_event_scheduler.current_time)
            if (
                packet.payload.get("operation") == "request"
                and packet.payload["destination_ip"] == self.ip_address
            ):
                self._send_arp_reply(packet)
                return

        if packet.header["destination_mac"] == self.mac_address:
            if (
                packet.payload.get("operation") == "reply"
                and packet.payload["destination_ip"] == self.ip_address
            ):
                self.network_event_scheduler.log_packet_info(
                    packet, "ARP reply received", self.node_id
                )
                source_ip = packet.payload["source_ip"]
                source_mac = packet.payload["source_mac"]
                self.add_to_arp_table(source_ip, source_mac)
                self.on_arp_reply_received(source_ip, source_mac)
                return

    def process_DHCP_packet(self, packet):
        if packet.header["destination_mac"] == self.mac_address:
            self.network_event_scheduler.log_packet_info(
                packet, "arrived", self.node_id
            )
            packet.set_arrived(self.network_event_scheduler.current_time)
            if packet.message_type == "OFFER":
                self.network_event_scheduler.log_packet_info(
                    packet, "DHCP Offer received", self.node_id
                )
                offered_ip = packet.dhcp_data.get("offered_ip")
                if offered_ip:
                    self.send_dhcp_request(offered_ip)
                return
            elif packet.message_type == "ACK":
                self.network_event_scheduler.log_packet_info(
                    packet, "DHCP ACK received", self.node_id
                )
                assigned_ip = packet.dhcp_data.get("assigned_ip")
                if assigned_ip:
                    self.ip_address = assigned_ip
                    print(
                        f"Node {self.node_id} has been assigned the IP address {assigned_ip}."
                    )
                dns_server_ip = packet.dhcp_data.get("dns_server_ip")
                if dns_server_ip:
                    self.dns_server_ip = dns_server_ip
                    print(
                        f"Node {self.node_id} has been assigned the DNS server IP address {dns_server_ip}."
                    )
                return

    def process_DNS_packet(self, packet):
        if packet.header["destination_mac"] == self.mac_address:
            self.network_event_scheduler.log_packet_info(
                packet, "arrived", self.node_id
            )
            packet.set_arrived(self.network_event_scheduler.current_time)
            self.network_event_scheduler.log_packet_info(
                packet, "DNS packet received", self.node_id
            )
            if packet.query_domain and "resolved_ip" in packet.dns_data:
                self.on_dns_response_received(
                    packet.query_domain, packet.dns_data["resolved_ip"]
                )
                return

    def process_UDP_packet(self, packet):
        if packet.header["destination_mac"] == self.mac_address:
            if packet.header["destination_ip"] == self.ip_address:
                self.network_event_scheduler.log_packet_info(
                    packet, "arrived", self.node_id
                )
                packet.set_arrived(self.network_event_scheduler.current_time)

                self.process_data_packet(packet)
            else:
                self.network_event_scheduler.log_packet_info(
                    packet, "dropped", self.node_id
                )

    def process_TCP_packet(self, packet):
        if packet.header["destination_mac"] == self.mac_address:
            if packet.header["destination_ip"] == self.ip_address:
                self.network_event_scheduler.log_packet_info(
                    packet, "arrived", self.node_id
                )
                packet.set_arrived(self.network_event_scheduler.current_time)

                flags = packet.header.get("flags", "")

                if "SYN" in flags:
                    if "ACK" in flags:
                        self.establish_TCP_connection(packet)
                        self.send_TCP_ACK(packet)
                        self.send_tcp_data_packet(packet)
                    else:
                        self.send_TCP_SYN_ACK(packet)
                    return

                if "ACK" in flags:
                    self.handle_acknowledgement(packet)
                    if self.check_duplication_threshold(
                        packet
                    ):
                        self.check_and_retransmit_packets(packet)
                    else:
                        self.send_tcp_data_packet(packet)

                if "PSH" in flags:
                    self.update_ACK_number(packet)
                    self.send_TCP_ACK(packet)
                    self.process_data_packet(packet)

                if "FIN" in flags:
                    self.terminate_TCP_connection(packet)

            else:
                self.network_event_scheduler.log_packet_info(
                    packet, "dropped", self.node_id
                )

    def initialize_connection_info(
        self,
        connection_key=None,
        state="CLOSED",
        sequence_number=0,
        acknowledgment_number=0,
        data=b"",
    ):
        self.tcp_connections[connection_key] = {
            "state": state,
            "sequence_number": sequence_number,
            "acknowledgment_number": acknowledgment_number,
            "data": data,
            "last_ack_number": None,
            "duplicate_ack_count": 0,
        }

    def handle_acknowledgement(self, packet):
        connection_key = (packet.header["source_ip"], packet.header["source_port"])
        ack_number = packet.header["acknowledgment_number"]

        if connection_key not in self.tcp_connections:
            return

        if connection_key not in self.windows:
            self.windows[
                connection_key
            ] = {}

        if self.tcp_connections[connection_key]["last_ack_number"] == ack_number:
            self.tcp_connections[connection_key]["duplicate_ack_count"] += 1
        else:
            self.tcp_connections[connection_key]["duplicate_ack_count"] = 1
            self.tcp_connections[connection_key]["last_ack_number"] = ack_number

        for seq, packet_info in list(self.windows[connection_key].items()):
            if packet_info["expected_ack_number"] <= ack_number:
                if self.network_event_scheduler.tcp_verbose:
                    print(
                        f"Removing packet with sequence number {seq} from window for connection {connection_key} due to receiving ACK {ack_number}. Expected ACK was {packet_info['expected_ack_number']}."
                    )
                self.cancel_timeout(connection_key, seq)
                del self.windows[connection_key][seq]

                if self.tcp_connections[connection_key]["data"]:
                    self.send_tcp_data_packet(packet)

    def check_duplication_threshold(self, packet):
        connection_key = (packet.header["source_ip"], packet.header["source_port"])
        if connection_key in self.tcp_connections:
            if self.tcp_connections[connection_key]["duplicate_ack_count"] >= 3:
                if self.network_event_scheduler.tcp_verbose:
                    last_ack_number = self.tcp_connections[connection_key].get(
                        "last_ack_number"
                    )
                    print(
                        f"Duplicate ACK threshold reached for connection {connection_key} with ACK number {last_ack_number}."
                    )
                return True
            else:
                return False
        return False

    def check_and_retransmit_packets(self, packet):
        connection_key = (packet.header["source_ip"], packet.header["source_port"])
        sequence_number = self.find_retransmit_sequence_number(connection_key)
        if sequence_number is not None:
            self.retransmit_packet(connection_key, sequence_number)
        else:
            print(f"No packets to retransmit for connection {connection_key}")

    def update_ACK_number(self, packet):
        connection_key = (packet.header["source_ip"], packet.header["source_port"])
        if connection_key not in self.tcp_connections:
            return

        seq_start = packet.header["sequence_number"]
        payload_length = len(packet.payload)

        current_ack_number = self.tcp_connections[connection_key][
            "acknowledgment_number"
        ]

        received_set = self.tcp_connections[connection_key].setdefault(
            "received_sequence_number", set()
        )
        for seq in range(seq_start, seq_start + payload_length):
            received_set.add(seq)

        next_expected_seq = current_ack_number
        while next_expected_seq in received_set:
            next_expected_seq += 1

        if next_expected_seq != current_ack_number:
            self.tcp_connections[connection_key]["acknowledgment_number"] = (
                next_expected_seq
            )
            if self.network_event_scheduler.tcp_verbose:
                print(
                    f"Updated ACK number to {next_expected_seq} for connection {connection_key}."
                )
        else:
            pass

    def send_TCP_SYN_ACK(self, packet):
        connection_key = (packet.header["source_ip"], packet.header["source_port"])

        sequence_number = randint(1, 10000)
        acknowledgment_number = packet.header["sequence_number"] + 1

        if connection_key not in self.tcp_connections:
            self.initialize_connection_info(
                connection_key=connection_key,
                state="SYN_RECEIVED",
                sequence_number=sequence_number,
                acknowledgment_number=acknowledgment_number,
                data=b"",
            )

        control_packet_kwargs = {
            "flags": "SYN,ACK",
            "sequence_number": self.tcp_connections[connection_key]["sequence_number"],
            "acknowledgment_number": self.tcp_connections[connection_key][
                "acknowledgment_number"
            ],
            "source_port": packet.header["destination_port"],
            "destination_port": packet.header["source_port"],
        }
        self._send_tcp_packet(
            destination_ip=packet.header["source_ip"],
            destination_mac=packet.header["source_mac"],
            data=b"",
            **control_packet_kwargs,
        )

        self.update_tcp_connection_state(connection_key, "ESTABLISHED")
        self.tcp_connections[connection_key]["sequence_number"] += 1

    def establish_TCP_connection(self, packet):
        connection_key = (packet.header["source_ip"], packet.header["source_port"])
        if connection_key in self.tcp_connections:
            if self.tcp_connections[connection_key]["state"] == "ESTABLISHED":
                return
            else:
                self.update_tcp_connection_state(connection_key, "ESTABLISHED")
                self.tcp_connections[connection_key]["acknowledgment_number"] = (
                    packet.header["sequence_number"] + 1
                )

    def send_TCP_ACK(self, packet, final_ack=False):
        connection_key = (packet.header["source_ip"], packet.header["source_port"])

        if connection_key in self.tcp_connections:
            control_packet_kwargs = {
                "flags": "ACK",
                "sequence_number": self.tcp_connections[connection_key][
                    "sequence_number"
                ],
                "acknowledgment_number": self.tcp_connections[connection_key][
                    "acknowledgment_number"
                ],
                "source_port": packet.header["destination_port"],
                "destination_port": packet.header["source_port"],
            }
            self._send_tcp_packet(
                destination_ip=packet.header["source_ip"],
                destination_mac=packet.header["source_mac"],
                data=b"",
                **control_packet_kwargs,
            )
        else:
            if self.network_event_scheduler.tcp_verbose:
                print("Error: Connection key not found in tcp_connections.")


    def terminate_TCP_connection(self, packet):
        if self.network_event_scheduler.tcp_verbose:
            print(
                f"Terminating TCP connection with {packet.header['source_ip']}:{packet.header['source_port']}"
            )
        connection_key = (packet.header["source_ip"], packet.header["source_port"])
        if connection_key in self.tcp_connections:
            del self.tcp_connections[connection_key]
            print(f"TCP connection terminated with {connection_key}")
        else:
            print("Error: Connection key not found.")

    def print_tcp_connections(self):
        if not self.tcp_connections:
            print("現在、アクティブなTCPコネクションはありません。")
            return

        print("アクティブなTCPコネクションの状態:")
        for connection, state in self.tcp_connections.items():
            destination_ip, destination_port = connection
            print(
                f"宛先IP: {destination_ip}, 宛先ポート: {destination_port}, 状態: {state['state']}"
            )

    def receive_packet(self, packet, received_link):
        if packet.arrival_time == -1:
            self.network_event_scheduler.log_packet_info(packet, "lost", self.node_id)
        elif isinstance(packet, ARPPacket):
            self.process_ARP_packet(packet)
        elif isinstance(packet, DHCPPacket):
            self.process_DHCP_packet(packet)
        elif isinstance(packet, DNSPacket):
            self.process_DNS_packet(packet)
        elif isinstance(packet, UDPPacket):
            self.process_UDP_packet(packet)
        elif isinstance(packet, TCPPacket):
            self.process_TCP_packet(packet)
        else:
            self.network_event_scheduler.log_packet_info(
                packet, "dropped", self.node_id
            )

    def process_data_packet(self, packet):
        more_fragments = packet.header.get("fragment_flags", {}).get(
            "more_fragments", False
        )

        if more_fragments:
            self._store_fragment(packet)
        else:
            original_data_id = packet.header.get("fragment_flags", {}).get(
                "original_data_id"
            )
            if original_data_id and original_data_id in self.fragmented_packets:
                self._reassemble_and_process_packet(packet)
            else:
                self.direct_process_packet(packet)

    def _store_fragment(self, fragment):
        original_data_id = fragment.header["fragment_flags"]["original_data_id"]
        offset = fragment.header["fragment_offset"]

        if original_data_id not in self.fragmented_packets:
            self.fragmented_packets[original_data_id] = {}

        self.fragmented_packets[original_data_id][offset] = fragment
        self.network_event_scheduler.log_packet_info(
            fragment, "fragment_stored", self.node_id
        )

    def print_fragments_info(self):
        for data_id, fragments in self.fragmented_packets.items():
            print(f"Original Data ID: {data_id}")
            for offset, fragment in fragments.items():
                fragment_size = len(fragment.payload)
                print(f"  Offset: {offset}, Size: {fragment_size}")

    def _reassemble_and_process_packet(self, last_fragment):
        original_data_id = last_fragment.header["fragment_flags"]["original_data_id"]
        if original_data_id not in self.fragmented_packets:
            self.network_event_scheduler.log_packet_info(
                last_fragment, "reassemble_failed_no_fragments", self.node_id
            )
            return

        fragments = self.fragmented_packets.pop(original_data_id)
        sorted_offsets = sorted(fragments.keys())

        reassembled_data = b"".join(
            fragments[offset].payload for offset in sorted_offsets
        )

        total_data_length = sum(
            len(fragment.payload) for fragment in fragments.values()
        )
        last_offset_key = max(sorted_offsets)
        last_fragment_size = len(fragments[last_offset_key].payload)
        expected_total_length = last_offset_key + last_fragment_size
        if total_data_length != expected_total_length:
            self.network_event_scheduler.log_packet_info(
                last_fragment, "reassemble_failed_incomplete_data", self.node_id
            )
            return

        self.network_event_scheduler.log_packet_info(
            last_fragment, "reassembled", self.node_id
        )

    def direct_process_packet(self, packet):
        pass

    def on_arp_reply_received(self, destination_ip, destination_mac):
        if destination_ip in self.waiting_for_arp_reply:
            for packet_info in self.waiting_for_arp_reply[destination_ip]:
                data, protocol, kwargs = packet_info
                self.send_packet(destination_ip, data, protocol=protocol, **kwargs)
            del self.waiting_for_arp_reply[destination_ip]

    def send_arp_request(self, ip_address):
        arp_request_packet = ARPPacket(
            source_mac=self.mac_address,
            destination_mac="FF:FF:FF:FF:FF:FF",
            source_ip=self.ip_address,
            destination_ip=ip_address,
            operation="request",
            network_event_scheduler=self.network_event_scheduler,
        )
        self.network_event_scheduler.log_packet_info(
            arp_request_packet, "ARP request", self.node_id
        )
        self._send_packet(arp_request_packet)

    def _send_arp_reply(self, request_packet):
        arp_reply_packet = ARPPacket(
            source_mac=self.mac_address,
            destination_mac=request_packet.header["source_mac"],
            source_ip=self.ip_address,
            destination_ip=request_packet.header["source_ip"],
            operation="reply",
            network_event_scheduler=self.network_event_scheduler,
        )
        self.network_event_scheduler.log_packet_info(
            arp_reply_packet, "ARP reply", self.node_id
        )
        self._send_packet(arp_reply_packet)

    def send_packet(self, destination_ip, data, protocol="UDP", **kwargs):
        destination_mac = self.get_mac_address_from_ip(destination_ip)

        if destination_mac is None:
            self.send_arp_request(destination_ip)
            if destination_ip not in self.waiting_for_arp_reply:
                self.waiting_for_arp_reply[destination_ip] = []
            self.waiting_for_arp_reply[destination_ip].append((data, protocol, kwargs))
        else:
            if protocol == "UDP":
                self._send_packet_data(destination_ip, destination_mac, data, **kwargs)
            elif protocol == "TCP":
                if not self.is_tcp_connection_established(
                    destination_ip, kwargs.get("destination_port")
                ):
                    connection_key = (destination_ip, kwargs.get("destination_port"))
                    self.pending_tcp_data[connection_key] = {
                        "data": data,
                        "kwargs": kwargs,
                    }
                    self.initiate_tcp_handshake(
                        destination_ip, destination_mac, **kwargs
                    )
                else:
                    self._send_tcp_packet(
                        destination_ip, destination_mac, data, **kwargs
                    )

    def is_tcp_connection_established(self, destination_ip, destination_port):
        key = (destination_ip, destination_port)
        return self.tcp_connections.get(key, {}).get("state") == "ESTABLISHED"

    def update_tcp_connection_state(self, connection_key, new_state):
        if connection_key not in self.tcp_connections:
            self.initialize_connection_info(
                connection_key=connection_key, state=new_state
            )
        else:
            self.tcp_connections[connection_key]["state"] = new_state
        if self.network_event_scheduler.tcp_verbose:
            print(f"TCP connection state updated to {new_state} for {connection_key}")

    def initiate_tcp_handshake(self, destination_ip, destination_mac, **kwargs):
        if not self.is_tcp_connection_established(
            destination_ip, kwargs.get("destination_port")
        ):
            if self.network_event_scheduler.tcp_verbose:
                print(
                    f"Initiating TCP handshake: Sending SYN to {destination_ip}:{kwargs.get('destination_port')} from port {kwargs.get('source_port')}"
                )

            connection_key = (destination_ip, kwargs.get("destination_port"))
            if connection_key not in self.tcp_connections:
                self.initialize_connection_info(
                    connection_key=connection_key,
                    state="SYN_SENT",
                    sequence_number=randint(1, 10000),
                    acknowledgment_number=0,
                    data=b"",
                )

            control_packet_kwargs = {
                "flags": "SYN",
                "sequence_number": self.tcp_connections[connection_key][
                    "sequence_number"
                ],
                "acknowledgment_number": 0,
                "source_port": kwargs.get("source_port"),
                "destination_port": kwargs.get("destination_port"),
                "payload_size": 0,
            }
            self._send_tcp_packet(
                destination_ip=destination_ip,
                destination_mac=destination_mac,
                data=b"",
                **control_packet_kwargs,
            )

            self.tcp_connections[connection_key]["sequence_number"] += 1
            if self.network_event_scheduler.tcp_verbose:
                print(
                    f"Connection state updated to SYN_SENT for {destination_ip}:{kwargs.get('destination_port')}"
                )

    def _send_udp_packet(self, destination_ip, destination_mac, data, **kwargs):
        udp_header_size = 8
        ip_header_size = 20
        header_size = udp_header_size + ip_header_size
        self._send_ip_packet_data(
            destination_ip, destination_mac, data, header_size, protocol="UDP", **kwargs
        )

    def send_tcp_data_packet(self, packet, attempt=0):
        connection_key = (packet.header["source_ip"], packet.header["source_port"])
        if connection_key in self.tcp_connections:
            if 'traffic_info' not in self.tcp_connections[connection_key]:
                if self.network_event_scheduler.tcp_verbose:
                    print(f"No traffic info found for {connection_key}")
                return

            traffic_info = self.tcp_connections[connection_key]['traffic_info']
            if self.network_event_scheduler.current_time < traffic_info['end_time']:
                if connection_key not in self.windows:
                    self.windows[connection_key] = {}

                while len(self.windows[connection_key]) < self.window_size:
                    remaining_data = self.tcp_connections[connection_key]['data']
                    payload_size = traffic_info['payload_size']
                    data_to_send = remaining_data[:payload_size]

                    if not data_to_send:
                        break

                    data_packet_kwargs = {
                        "source_port": packet.header["destination_port"],
                        "destination_port": packet.header["source_port"],
                        "sequence_number": self.tcp_connections[connection_key]['sequence_number'],
                        "acknowledgment_number": self.tcp_connections[connection_key]['acknowledgment_number'],
                        "flags": "PSH"
                    }

                    self._send_tcp_packet(
                        destination_ip=packet.header["source_ip"],
                        destination_mac=packet.header["source_mac"],
                        data=data_to_send,
                        **data_packet_kwargs
                    )

                    sequence_number = self.tcp_connections[connection_key][
                        "sequence_number"
                    ]
                    expected_ack_number = sequence_number + len(data_to_send)
                    self.windows[connection_key][sequence_number] = {
                        "packet_info": {
                            "destination_ip": packet.header["source_ip"],
                            "destination_mac": packet.header["source_mac"],
                            "data": data_to_send,
                            "kwargs": data_packet_kwargs,
                        },
                        "expected_ack_number": expected_ack_number,
                        "attempt": attempt
                    }
                    self.schedule_timeout(connection_key, sequence_number)

                    self.tcp_connections[connection_key]['data'] = remaining_data[payload_size:]
                    self.tcp_connections[connection_key]['sequence_number'] += len(data_to_send)

    def _send_tcp_packet(self, destination_ip, destination_mac, data, **kwargs):
        tcp_header_size = 20
        ip_header_size = 20
        header_size = tcp_header_size + ip_header_size

        connection_key = (destination_ip, kwargs.get('destination_port'))
        if connection_key in self.tcp_connections:
            self._send_ip_packet_data(
                destination_ip, destination_mac, data, header_size, protocol="TCP", **kwargs
            )

            if self.network_event_scheduler.tcp_verbose:
                print(f"Sending TCP packet from {self.node_id} to {destination_ip}:{kwargs.get('destination_port')} with Flags: {kwargs.get('flags')}, Data Length: {len(data)}, Sequence Number: {kwargs.get('sequence_number')}, Acknowledgment Number: {kwargs.get('acknowledgment_number')}, ")

    def schedule_timeout(self, connection_key, sequence_number):
        event_time = self.network_event_scheduler.current_time + self.timeout_interval
        event_id = self.network_event_scheduler.schedule_event(
            event_time, self.handle_timeout, connection_key, sequence_number
        )
        if sequence_number in self.windows[connection_key]:
            self.windows[connection_key][sequence_number]["timeout_event_id"] = event_id

    def handle_timeout(self, connection_key, sequence_number):
        if (
            connection_key in self.windows
            and sequence_number in self.windows[connection_key]
        ):
            attempt = self.windows[connection_key][sequence_number]["attempt"]
            packet_info = self.windows[connection_key][sequence_number]["packet_info"]

            if attempt < self.max_attempts - 1:
                if self.network_event_scheduler.tcp_verbose:
                    print(
                        f"Timeout for sequence number {sequence_number}. Retransmitting packet."
                    )
                self.retransmit_packet(connection_key, sequence_number)
            else:
                if self.network_event_scheduler.tcp_verbose:
                    print(
                        f"Maximum attempts reached for sequence number: {sequence_number}. Dropping packet."
                    )
                del self.windows[connection_key][
                    sequence_number
                ]

    def cancel_timeout(self, connection_key, sequence_number):
        if (
            connection_key in self.windows
            and sequence_number in self.windows[connection_key]
        ):
            event_id = self.windows[connection_key][sequence_number].get("timeout_event_id")
            if event_id is not None:
                self.network_event_scheduler.cancel_event(event_id)

    def find_retransmit_sequence_number(self, connection_key):
        if connection_key in self.windows:
            unacknowledged_sequence_numbers = self.windows[connection_key].keys()
            if unacknowledged_sequence_numbers:
                min_unack_seq_num = min(unacknowledged_sequence_numbers)
                return min_unack_seq_num
        return None

    def retransmit_packet(self, connection_key, sequence_number):
        if (
            connection_key in self.windows
            and sequence_number in self.windows[connection_key]
        ):
            packet_info = self.windows[connection_key][sequence_number]["packet_info"]

            destination_ip = packet_info["destination_ip"]
            destination_mac = packet_info["destination_mac"]
            data = packet_info["data"]
            kwargs = packet_info["kwargs"]

            if self.network_event_scheduler.tcp_verbose:
                print(
                    f"Retransmitting packet with sequence number {sequence_number} to {destination_ip}:{kwargs.get('destination_port')}"
                )
            self._send_tcp_packet(destination_ip, destination_mac, data, **kwargs)
            self.windows[connection_key][sequence_number]["attempt"] += 1
            if (
                self.windows[connection_key][sequence_number]["attempt"]
                >= self.max_attempts
            ):
                if self.network_event_scheduler.tcp_verbose:
                    print(
                        f"Maximum retransmission attempts reached for packet with sequence number {sequence_number}. Dropping the packet."
                    )
                del self.windows[connection_key][sequence_number]
        else:
            if self.network_event_scheduler.tcp_verbose:
                print(
                    f"No packet with sequence number {sequence_number} found in history for retransmission."
                )

    def _send_ip_packet_data(
        self, destination_ip, destination_mac, data, header_size, protocol, **kwargs
    ):
        original_data_id = str(uuid.uuid4())
        total_size = len(data) if data else 1
        offset = 0

        while offset < total_size or (offset == 0 and total_size == 0):
            max_payload_size = self.mtu - header_size
            payload_size = min(max_payload_size, total_size - offset) if data else 0

            fragment_data = data[offset : offset + payload_size] if data else b""
            fragment_offset = offset

            more_fragments = False if total_size == 0 else offset + payload_size < total_size
            fragment_flags = {
                "more_fragments": more_fragments,
            }
            if more_fragments or payload_size > 0:
                fragment_flags["original_data_id"] = original_data_id

            if protocol == "UDP":
                packet = UDPPacket(
                    source_mac=self.mac_address,
                    destination_mac=destination_mac,
                    source_ip=self.ip_address,
                    destination_ip=destination_ip,
                    ttl=64,
                    data=fragment_data,
                    network_event_scheduler=self.network_event_scheduler,
                    fragment_flags=fragment_flags,
                    fragment_offset=fragment_offset,
                    header_size=header_size,
                    payload_size=payload_size,
                    source_port=kwargs.get("source_port"),
                    destination_port=kwargs.get("destination_port"),
                )
            elif protocol == "TCP":
                packet = TCPPacket(
                    source_mac=self.mac_address,
                    destination_mac=destination_mac,
                    source_ip=self.ip_address,
                    destination_ip=destination_ip,
                    ttl=64,
                    data=fragment_data,
                    network_event_scheduler=self.network_event_scheduler,
                    fragment_flags=fragment_flags,
                    fragment_offset=fragment_offset,
                    header_size=header_size,
                    payload_size=payload_size,
                    source_port=kwargs.get("source_port"),
                    destination_port=kwargs.get("destination_port"),
                    sequence_number=kwargs.get("sequence_number", 0),
                    acknowledgment_number=kwargs.get("acknowledgment_number", 0),
                    flags=kwargs.get("flags", ""),
                )

            packet.payload = fragment_data
            self._send_packet(packet)

            if not data:
                break

            offset += payload_size

    def _send_packet(self, packet):
        if self.default_route:
            self.default_route.enqueue_packet(packet, self)
        else:
            for link in self.links:
                link.enqueue_packet(packet, self)

    def start_udp_traffic(
        self,
        destination_url,
        bitrate,
        start_time,
        duration,
        header_size,
        payload_size,
        burstiness=1.0,
        protocol="UDP",
    ):
        def attempt_to_start_traffic():
            destination_ip = self.resolve_destination_ip(destination_url)
            if destination_ip is None:
                self.send_dns_query_and_set_traffic(
                    destination_url,
                    bitrate,
                    start_time,
                    duration,
                    header_size,
                    payload_size,
                    burstiness,
                    protocol,
                )
            else:
                self.set_udp_traffic(
                    destination_ip,
                    bitrate,
                    start_time,
                    duration,
                    header_size,
                    payload_size,
                    burstiness,
                    protocol,
                )

        self.network_event_scheduler.schedule_event(
            start_time, attempt_to_start_traffic
        )

    def set_udp_traffic(
        self,
        destination_ip,
        bitrate,
        start_time,
        duration,
        header_size,
        payload_size,
        burstiness=1.0,
        protocol="UDP",
    ):
        end_time = start_time + duration
        source_port = self.select_random_port()
        destination_port = self.select_random_port()

        def generate_packet():
            if self.network_event_scheduler.current_time < end_time:
                data = b"X" * payload_size
                self.send_packet(
                    destination_ip,
                    data,
                    protocol,
                    source_port=source_port,
                    destination_port=destination_port,
                )

                packet_size = header_size + payload_size
                interval = (payload_size * 8) / bitrate * burstiness
                self.network_event_scheduler.schedule_event(
                    self.network_event_scheduler.current_time + interval,
                    generate_packet,
                )

        self.network_event_scheduler.schedule_event(
            self.network_event_scheduler.current_time, generate_packet
        )

    def start_tcp_traffic(
        self,
        destination_url,
        bitrate,
        start_time,
        duration,
        header_size,
        payload_size,
        burstiness=1.0,
        protocol="TCP",
    ):
        def attempt_to_start_traffic():
            destination_ip = self.resolve_destination_ip(destination_url)
            if destination_ip is None:
                self.send_dns_query_and_set_traffic(
                    destination_url,
                    bitrate,
                    start_time,
                    duration,
                    header_size,
                    payload_size,
                    burstiness,
                    protocol="TCP",
                )
            else:
                self.set_tcp_traffic(
                    destination_ip,
                    bitrate,
                    start_time,
                    duration,
                    header_size,
                    payload_size,
                    burstiness,
                )

        self.network_event_scheduler.schedule_event(
            start_time, attempt_to_start_traffic
        )

    def set_tcp_traffic(
        self,
        destination_ip,
        bitrate,
        start_time,
        duration,
        header_size,
        payload_size,
        burstiness=1.0,
        protocol="TCP",
    ):
        end_time = start_time + duration
        source_port = self.select_random_port()
        destination_port = self.select_random_port()

        connection_key = (destination_ip, destination_port)

        if connection_key not in self.tcp_connections:
            data = b"X" * (int(bitrate * duration) // 8)
            self.initialize_connection_info(
                connection_key=connection_key,
                sequence_number=randint(1, 10000),
                data=data
            )

        self.tcp_connections[connection_key]["traffic_info"] = {
            "end_time": end_time,
            "payload_size": payload_size,
            "header_size": header_size,
            "bitrate": bitrate,
            "burstiness": burstiness,
            "next_sequence_number": self.tcp_connections[connection_key][
                "sequence_number"
            ],
        }

        self.send_packet(
            destination_ip,
            b"",
            protocol="TCP",
            source_port=source_port,
            destination_port=destination_port,
            flags="SYN",
        )

    def resolve_destination_ip(self, destination_url):
        return self.url_to_ip_mapping.get(destination_url, None)

    def send_dns_query_and_set_traffic(
        self,
        destination_url,
        bitrate,
        start_time,
        duration,
        header_size,
        payload_size,
        burstiness=1.0,
        protocol="UDP",
    ):
        if destination_url not in self.waiting_for_dns_reply:
            self.waiting_for_dns_reply[destination_url] = []
        self.waiting_for_dns_reply[destination_url].append(
            (
                bitrate,
                start_time,
                duration,
                header_size,
                payload_size,
                burstiness,
                protocol,
            )
        )
        self.send_dns_query(destination_url)

    def send_dns_query(self, destination_url):
        dns_query_packet = DNSPacket(
            source_mac=self.mac_address,
            destination_mac="FF:FF:FF:FF:FF:FF",
            source_ip=self.ip_address,
            destination_ip=self.dns_server_ip,
            query_domain=destination_url,
            query_type="A",
            network_event_scheduler=self.network_event_scheduler,
        )
        self.network_event_scheduler.log_packet_info(
            dns_query_packet, "DNS query", self.node_id
        )
        self._send_packet(dns_query_packet)

    def on_dns_response_received(self, query_domain, resolved_ip):
        self.add_dns_record(query_domain, resolved_ip)
        if query_domain in self.waiting_for_dns_reply:
            for parameters in self.waiting_for_dns_reply[query_domain]:
                (
                    bitrate,
                    start_time,
                    duration,
                    header_size,
                    payload_size,
                    burstiness,
                    protocol,
                ) = parameters
                if protocol == "UDP":
                    self.set_udp_traffic(
                        resolved_ip,
                        bitrate,
                        start_time,
                        duration,
                        header_size,
                        payload_size,
                        burstiness,
                    )
                elif protocol == "TCP":
                    self.set_tcp_traffic(
                        resolved_ip,
                        bitrate,
                        start_time,
                        duration,
                        header_size,
                        payload_size,
                        burstiness,
                    )
            del self.waiting_for_dns_reply[query_domain]

    def print_url_to_ip_mapping(self):
        print("URL to IP Mapping")
        if not self.url_to_ip_mapping:
            print("  No entries found.")
            return

        for url, ip_address in self.url_to_ip_mapping.items():
            print(f"  {url}: {ip_address}")

    def __str__(self):
        connected_nodes = [
            link.node_x.node_id if self != link.node_x else link.node_y.node_id
            for link in self.links
        ]
        connected_nodes_str = ",".join(map(str, connected_nodes))
        return f"ノード（ID:{self.node_id}, MACアドレス:{self.mac_address}）, 接続:{connected_nodes_str}"
