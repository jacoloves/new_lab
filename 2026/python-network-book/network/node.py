import re
import uuid
from ipaddress import ip_network
from .packet import Packet


class Node:
    def __init__(
        self,
        node_id,
        mac_address,
        ip_address,
        network_event_scheduler,
        mtu=1500,
        default_route=None,
    ):
        if not self.is_valid_mac_address(mac_address):
            raise ValueError("無効なMACアドレス形式です。")

        if not self.is_valid_cidr_notation(ip_address):
            raise ValueError("無効なIPアドレス形式です。")

        self.network_event_scheduler = network_event_scheduler
        self.node_id = node_id
        self.mac_address = mac_address
        self.ip_address = ip_address
        self.links = []
        self.mtu = mtu
        self.fragmented_packets = {}
        self.default_route = default_route
        label = f"Node {node_id}\n{mac_address}"
        self.network_event_scheduler.add_node(node_id, label)

    def is_valid_mac_address(self, mac_address):
        mac_format = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")
        return bool(mac_format.match(mac_address))

    def is_valid_cidr_notation(self, ip_address):
        try:
            ip_network(ip_address, strict=False)
            return True
        except ValueError:
            return False

    def add_link(self, link):
        if link not in self.links:
            self.links.append(link)

    def mark_ip_as_used(self, ip_address):
        pass

    def receive_packet(self, packet, received_link):
        if packet.arrival_time == -1:
            self.network_event_scheduler.log_packet_info(packet, "lost", self.node_id)
            return

        if packet.header["destination_mac"] == self.mac_address:
            node_ip_address = self.ip_address.split("/")[0]
            if packet.header["destination_ip"] == node_ip_address:
                self.network_event_scheduler.log_packet_info(
                    packet, "arrived", self.node_id
                )
                packet.set_arrived(self.network_event_scheduler.current_time)

                if packet.header["fragment_flags"]["more_fragments"]:
                    self._store_fragment(packet)
                else:
                    self._reassemble_and_process_packet(packet)
            else:
                pass

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

        # last_fragmentをfragmentsに追加してから再組み立てする
        last_offset = last_fragment.header["fragment_offset"]
        fragments[last_offset] = last_fragment

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

    def send_packet(self, destination_mac, destination_ip, data, header_size):
        payload_size = self.mtu - header_size
        total_size = len(data)
        offset = 0

        original_data_id = str(uuid.uuid4())

        while offset < total_size:
            more_fragments = offset + payload_size < total_size

            fragment_data = data[offset : offset + payload_size]
            fragment_offset = offset

            fragment_flags = {
                "more_fragments": more_fragments,
                "original_data_id": original_data_id,
            }

            node_ip_address = self.ip_address.split("/")[0]
            packet = Packet(
                self.mac_address,
                destination_mac,
                node_ip_address,
                destination_ip,
                64,
                fragment_flags,
                fragment_offset,
                header_size,
                len(fragment_data),
                self.network_event_scheduler,
            )
            packet.payload = fragment_data

            self._send_packet(packet)

            offset += payload_size

    def _send_packet(self, packet):
        if self.default_route:
            self.default_route.enqueue_packet(packet, self)
        else:
            for link in self.links:
                link.enqueue_packet(packet, self)

    def create_packet(self, destination_mac, destination_ip, header_size, payload_size):
        # send_packetに委譲することでフラグメンテーションも適切に処理される
        data = b"X" * payload_size
        self.send_packet(destination_mac, destination_ip, data, header_size)

    def set_traffic(
        self,
        destination_mac,
        destination_ip,
        bitrate,
        start_time,
        duration,
        header_size,
        payload_size,
        burstiness=1.0,
    ):
        end_time = start_time + duration

        def generate_packet():
            if self.network_event_scheduler.current_time < end_time:
                data = b"X" * payload_size
                self.send_packet(destination_mac, destination_ip, data, header_size)

                packet_size = header_size + payload_size
                interval = (packet_size * 8) / bitrate * burstiness
                self.network_event_scheduler.schedule_event(
                    self.network_event_scheduler.current_time + interval,
                    generate_packet,
                )

        self.network_event_scheduler.schedule_event(start_time, generate_packet)

    def __str__(self):
        connected_nodes = [
            link.node_x.node_id if self != link.node_x else link.node_y.node_id
            for link in self.links
        ]
        connected_nodes_str = ",".join(map(str, connected_nodes))
        return f"ノード（ID:{self.node_id}, MACアドレス:{self.mac_address}）, 接続:{connected_nodes_str}"
