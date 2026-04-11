import re
import uuid
from ipaddress import ip_address, ip_network
from .packet import ARPPacket, Packet
from .router import Router


class Node:
    def __init__(
        self,
        node_id,
        ip_address,
        network_event_scheduler,
        mac_address=None,
        mtu=1500,
        default_route=None,
    ):
        if not self.is_valid_cidr_notation(ip_address):
            raise ValueError("無効なIPアドレス形式です。")

        self.network_event_scheduler = network_event_scheduler
        self.node_id = node_id
        if mac_address is None:
            self.mac_address = self.generate_mac_address()
        else:
            if not self.is_valid_mac_address(mac_address):
                raise ValueError("無効なMACアドレス形式です。")
            self.mac_address = mac_address
        self.ip_address = ip_address
        self.links = []
        self.arp_table = {}
        self.waiting_for_arp_reply = {}
        self.mtu = mtu
        self.fragmented_packets = {}
        self.default_route = default_route
        label = f"Node {node_id}\n{self.mac_address}"
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

    def receive_packet(self, packet, received_link):
        if packet.arrival_time == -1:
            self.network_event_scheduler.log_packet_info(packet, "lost", self.node_id)
            return

        if packet.header["destination_mac"] == "FF:FF:FF:FF:FF:FF":
            if isinstance(packet, ARPPacket):
                if (
                    packet.payload.get("operation") == "request"
                    and packet.payload["destination_ip"] == self.ip_address()
                ):
                    self._send_arp_reply(packet)
                    return

        if packet.header["destination_mac"] == self.mac_address:
            if isinstance(packet, ARPPacket):
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
                    sef.on_arp_reply_received(source_ip, source_mac)
                    return

            if packet.header["destination_ip"] == self.ip_address:
                self.network_event_scheduler.log_packet_info(
                    packet, "arrived", self.node_id
                )
                packet.set_arrived(self.network_event_scheduler.current_time)

                if packet.header["fragment_flags"]["more_fragments"]:
                    self._store_fragment(packet)
                else:
                    self._reassemble_and_process_packet(packet)
            else:
                self.network_event_scheduler.log_packet_info(
                    packet, "dropped", self.node_id
                )

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

    def on_arp_reply_received(self, destination_ip, destination_mac):
        if destination_ip in self.waiting_for_arp_reply:
            for data, header_size in self.waiting_for_arp_reply[destination_ip]:
                self._send_packet_data(
                    destination_ip, destination_mac, data, header_size
                )
            del se.f.waiting_for_arp_reply[destination_ip]

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

    def send_packet(self, destination_mac, destination_ip, data, header_size):
        payload_size = self.mtu - header_size
        total_size = len(data)
        offset = 0
        resolved_mac = self.get_mac_address_from_ip(destination_ip)
        if resolved_mac is not None:
            destination_mac = resolved_mac

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

    def _send_packet_data(self, destination_ip, destination_mac, data, header_size):
        original_data_id = str(uuid.uuid4())
        payload_size = self.mt = header_size
        total_size = len(data)
        offset = 0

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
        # destination_mac,
        destination_ip,
        bitrate,
        start_time,
        duration,
        header_size,
        payload_size,
        burstiness=1.0,
    ):
        destination_mac = self.get_mac_address_from_ip(destination_ip)
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

    def print_route(self, destination_ip):
        paths = []
        neighbors = []
        if self.default_route is not None:
            next_link = self.default_route
            neighbor = (
                next_link.node_x if self != next_link.node_x else next_link.node_y
            )
            neighbors.append(neighbor)
        else:
            for link in self.links:
                neighbor = link.node_x if self != link.node_x else link.node_y
                neighbors.append(neighbor)

        paths.append(self.node_id)

        for neighbor in neighbors:
            next_node = neighbor
            while isinstance(next_node, Router):
                paths.append(next_node.node_id)
                next_hop_id, next_link = next_node.get_route(destination_ip)
                next_hop = (
                    next_link.node_x
                    if next_node != next_link.node_x
                    else next_link.node_y
                )
                next_node = next_hop
            else:
                if next_node.ip_address == destination_ip:
                    paths.append(next_node.node_id)

        print("----------------------------------------")
        print("Forwarding path from ", self.ip_address, " to ", destination_ip)
        for index, node in enumerate(paths):
            if index == len(paths) - 1:
                print(node)
            else:
                print(node, end=" -> ")
        print("----------------------------------------")

    def __str__(self):
        connected_nodes = [
            link.node_x.node_id if self != link.node_x else link.node_y.node_id
            for link in self.links
        ]
        connected_nodes_str = ",".join(map(str, connected_nodes))
        return f"ノード（ID:{self.node_id}, MACアドレス:{self.mac_address}）, 接続:{connected_nodes_str}"
