import random
import re
from typing import Protocol
import uuid
from ipaddress import ip_interface, ip_network
from random import randint

from .packet import ARPPacket, DNSPacket, Packet, DHCPPacket, TCPPacket, UDPPacket
from .router import Router
from network import packet
from .application import ApplicationManager


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
        self.ip_address = ip_address
        self.network_event_scheduler = network_event_scheduler
        self.local_seed = self.network_event_scheduler.get_seed()
        if self.local_seed is not None:
            random.seed(self.local_seed)
        if mac_address is None:
            self.mac_address = self.generate_mac_address()
        else:
            if not self.is_valid_mac_address(mac_address):
                raise ValueError("無効なMACアドレス形式です。")
            self.mac_address = mac_address

        self.links = []
        self.applications = {}
        self.used_ports = set()
        self.port_mapping = {}
        self.tcp_connections = {}
        self.cwnd = 1
        self.ssthresh = 32
        self.MAX_CWND = 128
        self.tcp_state = {}
        self.max_attempts = 10
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

        label = f"Node {node_id}\n{mac_address}"
        self.network_event_scheduler.add_node(node_id, label, ip_addresses=[ip_address])

        self.application_layer = ApplicationManager(self)

        if self.is_network_address(self.ip_address):
            if self.application_layer:
                self.application_layer.register_dhcp_client()

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

    def register_application(self, port, protocol, application_instance):
        self.applications[(port, protocol)] = application_instance

        self.used_ports.add(port)

        if hasattr(application_instance, "__class__"):
            class_name = application_instance.__class__.__name__
            if class_name == "FTPServer":
                if self.application_layer and hasattr(
                    self.application_layer, "register_ftp_server"
                ):
                    self.application_layer.register_ftp_server(application_instance)
            elif class_name == "FTPClient":
                if self.application_layer and hasattr(
                    self.application_layer, "register_ftp_client"
                ):
                    self.application_layer.register_ftp_client(application_instance)

    def select_available_port(self):
        for port in range(1024, 49152):
            if port not in self.used_ports:
                self.used_ports.add(port)
                return port
        raise Exception("No available ports")

    def select_random_port(self):
        return random.randint(1024, 49151)

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
        if self.application_layer and self.application_layer.dns_client:
            self.application_layer.dns_client.url_to_ip_mapping[domain_name] = (
                ip_address
            )
            print(f"{self.node_id} DNS record added: {domain_name} -> {ip_address}")

    def process_ARP_packet(self, packet):
        self.network_event_scheduler.log_packet_info(packet, "arrived", self.node_id)
        packet.set_arrived(self.network_event_scheduler.current_time)

        if packet.header["destination_mac"] == "FF:FF:FF:FF:FF:FF":
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

    def process_UDP_packet(self, packet):
        if packet.header["destination_mac"] in [self.mac_address, "FF:FF:FF:FF:FF:FF"]:
            if packet.header["destination_ip"] in [
                self.ip_address,
                "255.255.255.255/32",
            ]:
                self.network_event_scheduler.log_packet_info(
                    packet, "arrived", self.node_id
                )
                packet.set_arrived(self.network_event_scheduler.current_time)

                if isinstance(packet, DHCPPacket):
                    if self.application_layer and hasattr(
                        self.application_layer, "on_dhcp_packet_received"
                    ):
                        self.application_layer.on_dhcp_packet_received(packet)
                    return

                if isinstance(packet, DNSPacket):
                    if self.application_layer and hasattr(
                        self.application_layer, "on_dhcp_packet_received"
                    ):
                        self.application_layer.on_dns_packet_received(packet)
                    return

                if self.application_layer and hasattr(
                    self.application_layer, "on_packet_received"
                ):
                    self.application_layer.on_dhcp_packet_received(packet)
                else:
                    self.process_data_packet(packet)
            else:
                self.network_event_scheduler.log_packet_info(
                    packet, "dropped", self.node_id
                )

    def process_TCP_packet(self, packet):
        if self.network_event_scheduler.tcp_verbose:
            print(
                f"Processing TCP packet from {packet.header['source_ip']}:{packet.header['source_port']} to {packet.header['destination_ip']}:{packet.header['destination_port']}"
            )

        if packet.header["destination_mac"] == self.mac_address:
            if packet.header["destination_ip"] == self.ip_address:
                self.network_event_scheduler.log_packet_info(
                    packet, "arrived", self.node_id
                )
                packet.set_arrived(self.network_event_scheduler.current_time)
                flags = packet.header.get("flags", "")
                if self.network_event_scheduler.tcp_verbose:
                    print(f"TCP flags: {flags}")

                connection_key = (
                    packet.header["source_ip"],
                    packet.header["source_port"],
                )
                source_port = packet.header["destination_port"]
                sequence_number = packet.header["sequence_number"]
                ack_number = packet.header["acknowledgment_number"]
                dscp = packet.header["dscp"]
                payload_length = len(packet.payload)

                if "SYN" in flags:
                    if "ACK" in flags:
                        self.establish_TCP_connection(connection_key, sequence_number)
                        self.send_TCP_ACK(connection_key, source_port, dscp)
                    else:
                        self.send_TCP_SYN_ACK(
                            connection_key, source_port, sequence_number, dscp
                        )
                    return

                if "ACK" in flags:
                    if (
                        connection_key in self.tcp_connections
                        and self.tcp_connections[connection_key]["state"]
                        == "SYN_RECEIVED"
                    ):
                        self.establish_TCP_connection(connection_key, sequence_number)
                    self.handle_acknowledgement(connection_key, ack_number)

                if "PSH" in flags:
                    self.update_ACK_number(
                        connection_key, sequence_number, payload_length
                    )
                    self.send_TCP_ACK(connection_key, source_port, dscp)
                    self.process_data_packet(packet)

                if "FIN" in flags:
                    self.terminate_TCP_connection(connection_key)

                if self.application_layer and hasattr(
                    self.application_layer, "on_packet_received"
                ):
                    self.application_layer.on_packet_received(packet)
                else:
                    self.network_event_scheduler.log_packet_info(
                        packet, "no application found", self.node_id
                    )
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
            "sequence_number_base": sequence_number,
            "acknowledgment_number": acknowledgment_number,
            "data": data,
            "last_ack_number": None,
            "duplicate_ack_count": 0,
            "cwnd": self.cwnd,
            "ssthresh": self.ssthresh,
            "congestion_state": "slow_start",
            "transfer_info": None,
            "timeout_event_ids": {},
            "retransmission_event_ids": {},
        }

    def transition_to_state(self, connection_key, new_state):
        if connection_key not in self.tcp_connections:
            return

        current_state = self.tcp_connections[connection_key]["congestion_state"]
        if current_state == new_state:
            return

        cwnd = self.tcp_connections[connection_key]["cwnd"]
        ssthresh = self.tcp_connections[connection_key]["ssthresh"]

        if new_state == "slow_start":
            self.tcp_connections[connection_key]["ssthresh"] = max(cwnd // 2, 2)
            self.tcp_connections[connection_key]["cwnd"] = 1
            self.tcp_connections[connection_key]["congestion_state"] = new_state
            if self.network_event_scheduler.tcp_verbose:
                print(
                    f"Transitioning to {new_state} for connection {connection_key}. ssthresh set to {self.tcp_connections[connection_key]['ssthresh']}, cwnd reset to 1."
                )

        elif new_state == "congestion_avoidance":
            self.tcp_connections[connection_key]["congestion_state"] = new_state
            if self.network_event_scheduler.tcp_verbose:
                print(
                    f"Transitioning to {new_state} for connection {connection_key}. Continuing to increase cwnd linearly."
                )

        elif new_state == "fast_recovery":
            self.tcp_connections[connection_key]["ssthresh"] = max(cwnd // 2, 2)
            self.tcp_connections[connection_key]["cwnd"] = (
                self.tcp_connections[connection_key]["ssthresh"] + 3
            )
            self.tcp_connections[connection_key]["congestion_state"] = new_state
            if self.network_event_scheduler.tcp_verbose:
                print(
                    f"Transitioning to {new_state} for connection {connection_key}. cwnd set to {self.tcp_connections[connection_key]['cwnd']}."
                )

        self.log_congestion_window(
            connection_key, self.tcp_connections[connection_key]["cwnd"], new_state
        )

    def handle_acknowledgement(self, connection_key, ack_number):
        if connection_key not in self.tcp_connections:
            return

        conn_info = self.tcp_connections[connection_key]
        if self.network_event_scheduler.tcp_verbose:
            print(
                f"[DEBUG] handle_acknowledgement for {connection_key}, ack_number={ack_number}"
            )
            print(f"[DEBUG] cwnd={conn_info['cwnd']}, ssthresh={conn_info['ssthresh']}")

        if connection_key in self.windows:
            unacked_seqs = sorted(self.windows[connection_key].key())
            print(f"[DEBUG] Unacked packets for {connection_key}: {unacked_seqs}")

        self.remove_acked_packets_from_window(connection_key, ack_number)

        transfer_info = conn_info.get("transfer_info", None)
        print(f"[DEBUG] Transfer info: {transfer_info}")
        if transfer_info and transfer_info["file_size"] > 0:
            seq_base = conn_info["sequence_number_base"]
            bytes_acked = ack_number - seq_base
            print(f"[DEBUG] Bytes acked: {bytes_acked}")
            if bytes_acked > transfer_info["bytes_transferred"]:
                transfer_info["bytes_transferred"] = bytes_acked
                transfer_info["progress"].append(
                    (self.network_event_scheduler.current_time, bytes_acked)
                )
                if self.network_event_scheduler.tcp_verbose:
                    print(
                        f"Transfer Progress: {bytes_acked}/{transfer_info['file_size']} bytes transferred."
                    )

        last_ack = conn_info.get("last_ack_number", 0)
        is_duplicate_ack = ack_number == last_ack
        conn_info["last_ack_number"] = ack_number

        state = conn_info["congestion_state"]
        if state == "fast_recovery":
            seq_to_retransmit = self.find_retransmit_sequence_number(connection_key)
            if seq_to_retransmit is not None:
                if (
                    ack_number > last_ack
                    and ack_number
                    < self.windows[connection_key][seq_to_retransmit][
                        "expected_ack_number"
                    ]
                ):
                    conn_info["cwnd"] = max(
                        conn_info["cwnd"] - 1, conn_info["ssthresh"]
                    )
                    self.retransmit_packet(connection_key, seq_to_retransmit)
                    self.schedule_send_next_chunk(connection_key)
                    return
                else:
                    conn_info["cwnd"] = conn_info["ssthresh"]
                    self.transition_to_state(connection_key, "congestion_avoidance")
                    self.schedule_send_next_chunk(connection_key)
                    return

        if is_duplicate_ack:
            conn_info["duplicate_ack_count"] += 1
            if conn_info["duplicate_ack_count"] >= 3:
                self.fast_retransmit(connection_key)
                self.schedule_send_next_chunk(connection_key)
        else:
            conn_info["duplicate_ack_count"] = 0
            self.adjust_congestion_window(connection_key)
            self.schedule_send_next_chunk(connection_key)

    def send_next_chunk_event(self, connection_key):
        thread_info = self.tcp_connections[connection_key].get("transfer_info", None)
        if thread_info:
            file_size = transfer_info.get("file_size", 0)
            bytes_transferred = transfer_info.get("bytes_transferred", 0)
            if bytes_transferred < file_size:
                app = self.application_layer
                chunk = app.get_data_chunk(
                    connection_key, transfer_info["payload_size"]
                )
                if chunk:
                    dst_ip, dst_port = connection_key
                    self.send_app_data(
                        dst_ip, chunk, protocol="TCP", destination_port=dst_port
                    )

    def schedule_timeout(self, connection_key, sequence_number):
        event_time = self.network_event_scheduler.current_time + self.timeout_interval
        event_id = self.network_event_scheduler.schedule_event(
            event_time, self.handle_timeout, connection_key, sequence_number
        )
        self.tcp_connections[connection_key]["timeout_event_ids"].append(event_id)

    def handle_timeout(self, connection_key, sequence_number):
        if (
            connection_key in self.windows
            and sequence_number in self.windows[connection_key]
        ):
            attempt = self.windows[connection_key][sequence_number]["attempt"]
            packet_info = self.windows[connection_key][sequence_number]["packet_info"]

            current_cwnd = self.tcp_connections[connection_key]["cwnd"]
            self.tcp_connections[connection_key]["ssthresh"] = max(current_cwnd // 2, 2)
            self.tcp_connections[connection_key]["cwnd"] = 1

            if attempt < self.max_attempts - 1:
                if self.network_event_scheduler.tcp_verbose:
                    print(
                        f"Timeout for sequence number {sequence_number}. Retransmitting packet."
                    )
                self.retransmit_packet(connection_key, sequence_number)
                self.schedule_timeout(connection_key, sequence_number)
            else:
                if self.network_event_scheduler.tcp_verbose:
                    print(
                        f"Maximum attempts reached for sequence number: {sequence_number}. Dropping packet."
                    )
                del self.windows[connection_key][sequence_number]

            self.transition_to_state(connection_key, "slow_start")

            if self.network_event_scheduler.tcp_verbose:
                print(
                    f"Timeout handled for connection {connection_key}. State transitioned to slow_start."
                )

            self.schedule_send_next_chunk(connection_key)

    def cancel_timeout(self, connection_key, sequence_number):
        if (
            connection_key in self.tcp_connections
            and "timeout_event_ids" in self.tcp_connections[connection_key]
        ):
            if (
                sequence_number
                in self.tcp_connections[connection_key]["timeout_event_ids"]
            ):
                event_id = self.tcp_connections[connection_key][
                    "timeout_event_ids"
                ].pop(sequence_number)
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
            dscp = packet_info["dscp"]
            kwargs = packet_info["kwargs"]

            if self.network_event_scheduler.tcp_verbose:
                print(
                    f"Retransmitting packet with sequence number {sequence_number} to {destination_ip}:{kwargs.get('destination_port')}"
                )
            self._send_transport_packet(
                "TCP", destination_ip, destination_mac, data, dscp, **kwargs
            )
            self.windows[connection_key][sequence_number]["attempt"] += 1

            self.schedule_timeout(connection_key, sequence_number)

            if (
                self.windows[connection_key][sequence_number]["attempt"]
                >= self.max_attempts
            ):
                if self.network_event_scheduler.tcp_verbose:
                    print(
                        f"Maximum retransmission attempts reached for packet with sequence number {sequence_number}. Dropping the packet."
                    )

                current_cwnd = self.tcp_connections[connection_key]["cwnd"]
                self.tcp_connections[connection_key]["ssthresh"] = max(
                    current_cwnd // 2, 2
                )
                self.tcp_connections[connection_key]["cwnd"] = 1

                self.cancel_timeout(connection_key, sequence_number)
                self.cancel_retransmission_event(connection_key, sequence_number)
                del self.windows[connection_key][sequence_number]

                self.transition_to_state(connection_key, "slow_start")
            else:
                self.cancel_retransmission_event(connection_key, sequence_number)
                self.schedule_retransmission(connection_key)
        else:
            if self.network_event_scheduler.tcp_verbose:
                print(
                    f"No packet with sequence number {sequence_number} found in history for retransmission."
                )

    def cancel_retransmission_event(sefl, connection_key, sequence_number):
        if (
            connection_key in self.tcp_connections
            and "retransmission_event_ids" in self.tcp_connections[connection_key]
        ):
            retrans_ids = self.tcp_connections[connection_key][
                "retransmission_event_ids"
            ]
            if sequence_number im retrans_ids:
                event_id = retrans_ids.pop(sequence_number)
                self.network_event_scheduler.cancel_event(event_id)

    def remove_acked_packets_from_window(self, connection_key, ack_number):
        if connection_key not in self.windows:
            return

        for seq, packet_info in list(self.windows[connection_key].items()):
            if packet_info["expected_ack_number"] <= ack_number:
                self.cancel_timeout(connection_key, seq)
                self.cancel_retransmission_event(
                    connection_key, seq
                )
                del selc.windows[connection_key][seq]

    def fast_retransmit(self, connection_key):
        self.transition_to_state(connection_key, "fast_recovery")
        seq_num = self.find_retransmit_sequence_number(connection_key)
        if seq_num is not None:
            self.cancel_retransmission_event(connection_key, seq_num)
            self.schedule_retransmission(connection_key)
        else:
            self.tcp_connections[connection_key]["cwnd"] = self.tcp_connections[
                connection_key
            ]["ssthresh"]
            self.transition_to_state(connection_key, "congestion_avoidance")

    def schedule_retransmission(self, connection_key):
        sequence = self.find_retransmit_sequence_number(connection_key)
        if sequence_number is not None:
            event_time = (
                self.network_event_scheduler.current_time + self.timeout_interval / 2
            )
            event_id = self.network_event_scheduler.schedule_event(
                event_time, self.retransmit_packet, connection_key, sequence_number
            )
            self.tcp_connections[connection_key] ["retransmission_event_ids"][
                sequence_number
            ] = event_id
        else:
            if self.network_event_scheduler.tcp_connections:
                print(f"No packets to retransmit for connection {connection_key}")

    def log_congestion_window(self, connection_key, cwnd, state):
        log_entry = {
            "time": self.network_event_scheduler.current_time,
            "connection": connection_key,
            "cwnd": cwnd,
            "state": state,
        }
        self.network_event_scheduler.log_cwnd_event(log_entry)
        if self.network_event_scheduler.tcp_verbose:
            print(f"Logged cwnd event: {log_entry}")
            
    def adjust_congestion_window(self, connection_key):
        if connection_key not in self.tcp_connections:
            return

        state = self.tcp_connections[connection_key]["congestion_state"]
        cwnd = self.tcp_connections[connection_key]["cwnd"]
        ssthresh = self.tcp_connections[connection_key]["ssthresh"]

        if state == "slow_start":
            new_cwnd = min(cwnd + 1, self.MAX_CWND)
            self.tcp_connections[connection_key]["cwnd"] = new_cwnd
            self.log_congestion_window(connection_key, new_cwnd, "slow_start")

            if self.network_event_scheduler.tcp_verbose:
                print(
                    f"Updated cwnd to {new_cwnd} for connection {connection_key} in slow start."
                )

            if new_cwnd >= ssthresh:
                self.transition_to_state(connection_key, "congestion_avoidance")

        elif state == "congestion_avoidance":
            increment = 1.0 / cwnd
            new_cwnd = min(cwnd + increment, self.MAX_CWND)
            self.tcp_connections[connection_key]["cwnd"] = new_cwnd
            self.log_congestion_window(connection_key, new_cwnd, "congestion_avoidance")

            if self.network_event_scheduler.tcp_verbose:
                print(
                    f"Updated cwnd to {new_cwnd} for connection {connection_key} in congestion avoidance."
                )

        elif state == "fast_recovery":
            new_cwnd = min(cwnd + 1, self.MAX_CWND)
            self.tcp_connections[connection_key]["cwnd"] = new_cwnd
            self.log_congestion_window(connection_key, new_cwnd, "fast_recovery")

            if self.network_event_scheduler.tcp_verbose:
                print(
                    f"Updated cwnd to {new_cwnd} for connection {connection_key} in fast recovery."
                )

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

                self.fast_retransmit(connection_key)
                return True
            else:
                return False
        return False

    def update_ACK_number(
        self, connection_key, received_sequence_number, payload_length
    ):
        if connection_key not in self.tcp_connections:
            if self.network_event_scheduler.tcp_verbose:
                print(f"[update_ACK_number] Connection {connection_key} not found.")
            return

        conn_info = self.tcp_connections[connection_key]
        current_ack_number = conn_info["acknowledgment_number"]

        start_seq = received_sequence_number
        end_seq = received_sequence_number + payload_length

        received_seq_set = conn_info.setdefault("received_sequence_number", set())
        for seq in range(start_seq, end_seq):
            received_seq_set.add(seq)

        out_of_order = conn_info.setdefault("out_of_order_packets", [])

        next_expected = current_ack_number
        while next_expected in received_seq_set:
            next_expected += 1

        if next_expected > current_ack_number:
            conn_info["acknowledgment_number"] = next_expected

            while out_of_order and out_of_order[0] < next_expected:
                out_of_order.pop(0)

            if self.network_event_scheduler.tcp_verbose:
                print(
                    f"[update_ACK_number] Updated ACK to {next_expected} for {connection_key}"
                )
        else:
            if end_seq > current_ack_number:
                if end_seq not in out_of_order:
                    out_of_order.append(end_seq)
                    out_of_order.sort()
            if self.network_event_scheduler.tcp_verbose:
                print(f"[update_ACK_number] No ACK update; out_of_order={out_of_order}")

    def send_TCP_SYN_ACK(self, connection_key, source_port, sequence_number, dscp):
        acknowledgment_number = sequence_number + 1

        if connection_key not in self.tcp_connections:
            self.initialize_connection_info(
                connection_key=connection_key,
                state="SYN_RECEIVED",
                sequence_number=sequence_number,
                acknowledgment_number=acknowledgment_number,
                data=None,
            )

        control_packet_kwargs = {
            "flags": "SYN,ACK",
            "sequence_number": self.tcp_connections[connection_key]["sequence_number"],
            "acknowledgment_number": self.tcp_connections[connection_key][
                "acknowledgment_number"
            ],
            "source_port": source_port,
            "destination_port": connection_key[1],
        }

        destination_ip = connection_key[0]
        dscp = dscp
        self.send_control_tcp_packet(destination_ip, b"", dscp, **control_packet_kwargs)

        self.tcp_connections[connection_key]["sequence_number"] += 1

    def establish_TCP_connection(self, connection_key, sequence_number):
        if connection_key in self.tcp_connections:
            if self.tcp_connections[connection_key]["state"] == "ESTABLISHED":
                return
            else:
                self.update_tcp_connection_state(connection_key, "ESTABLISHED")
                self.tcp_connections[connection_key]["acknowledgment_number"] = (
                    sequence_number + 1
                )
        else:
            initial_seq = randint(1, 10000)
            self.initialize_connection_info(
                connection_key, 
                state="ESTABLISHED",
                sequence_number=initial_seq,
                acknowledgment_number=sequence_number + 1,
                data=b"",
            )

        if (
            "transfer_info" not in self.tcp_connections[connection_key]
            or self.tcp_connections[connection_key]["transfer_info"] is None
        ):
            end_time = self.network_event_scheduler.current_time + 3600
            payload_size = 1460
            self.tcp_connections[connection_key]["transfer_info"] = {
                "end_time": end_time,
                "payload_size": payload_size,
                "bytes_transferred": 0,
                "progress": [],
                "file_size": 0,
            }

        if self.application_layer and hasattr(
            self.application_layer, "on_connection_established"
        ):
            self.application_layer.on_connection_established(connection_key)

    def send_TCP_ACK(self, connection_key, source_port, dscp):
        if connection_key in self.tcp_connections:
            control_packet_kwargs = {
                "flags": "ACK",
                "sequence_number": self.tcp_connections[connection_key][
                    "sequence_number"
                ],
                "acknowledgment_number": self.tcp_connections[connection_key][
                    "acknowledgment_number"
                ],
                "source_port": source_port,
                "destination_port": connection_key[1],
            }
            destination_ip = connection_key[0]
            dscp = dscp

            self.send_control_tcp_packet(
                destination_ip, b"", dscp, **control_packet_kwargs
            )
        else:
            if self.network_event_scheduler.tcp_verbose:
                print("Error: Connection key not found in tcp_connections.")

    def terminate_TCP_connection(self, connection_key):
        if self.network_event_scheduler.tcp_verbose:
            print(f"Terminating TCP connection with {connection_key}")
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
        if packet,arrival_time == =1:
            self.network_event_scheduler.log_packet_info(packet, "lost", self.node_id)
        elif isinstance(packet, ARPPacket):
            self.process_ARP_packet(packet)
        elif isinstance(packet DHCPPacket):
            if self.application_layer and hasattr(
                self.application_layer, "on_dhcp_packet_received"
            ):
                self.application_layer.on_dhcp_packet_received(packet)
        elif isinstance(packet, DNSPacket):
            if self.application_layer and hasattr(
                self.application_layer, "on_dns_packet_received"
            ):
                self.application_layer.on_dns_packet_received(packet)
        elif isinstance(packet, UDPPacket):
            self.process_UDP_packet(packet)
        elif isinstance(packet, TCPPacket):
            self.process_TCP_packet(packet)
        else:
            self.network_event_scheduler.log_packet_info(
                packet, "dropped", self.node_id
            )

    def process_data_packet(self, packet):
        self.direct_process_packet(packet)

    def direct_process_packet(self, packet):
        pass

    def on_arp_reply_received(self, destination_ip, destination_mac):
        if destination_ip in self.waiting_for_arp_reply:
            for data, protocol, dscp, kwargs in self.waiting_for_arp_reply[
                destination_ip
            ]:
                self._send_transport_packet(
                    protocol, destination_ip, destination_mac, data, dscp, **kwargs
                )
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
        arp_request_packet = ARPPacket(
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

    def is_tcp_connection_established(self, destination_ip, destination_port):
        key = (destination_ip, destination_port)
        return self.tcp_connections.get(key, {}).get("state") == "ESTABLISHED"


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
