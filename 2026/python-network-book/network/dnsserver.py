import uuid
from .packet import ARPPacket, DNSPacket


class DNSServer:
    def __init__(self, node_id, ip_address, network_event_scheduler, mac_address=None):
        self.node_id = node_id
        self.links = []
        if mac_address is None:
            self.mac_address = self.generate_mac_address()
        else:
            self.mac_address = mac_address
        self.ip_address = ip_address
        self.network_event_scheduler = network_event_scheduler
        self.dns_records = {}
        label = f"DNSServer {node_id}"
        self.network_event_scheduler.add_node(
            node_id, label, ip_addresses=[ip_address]
        )

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

    def mark_ip_as_used(self, ip_address):
        pass

    def add_dns_record(self, domain_name, ip_address):
        self.dns_records[domain_name] = ip_address

    def receive_packet(self, packet, received_link):
        if packet.arrival_time == -1:
            self.network_event_scheduler.log_packet_info(packet, "lost", self.node_id)
            return

        if (
            packet.header["destination_mac"] == "FF:FF:FF:FF:FF:FF"
            or packet.header["destination_mac"] == self.mac_address
        ):
            if isinstance(packet, ARPPacket):
                if (
                    packet.payload.get("operation") == "request"
                    and packet.payload["destination_ip"] == self.ip_address
                ):
                    self._send_arp_reply(packet)

            if isinstance(packet, DNSPacket):
                if packet.header["destination_ip"] == self.ip_address:
                    self.network_event_scheduler.log_packet_info(
                        packet, "arrived", self.node_id
                    )
                    packet.set_arrived(self.network_event_scheduler.current_time)

                    self.network_event_scheduler.log_packet_info(
                        packet, "DNS query received", self.node_id
                    )
                    dns_response_packet = self.handle_dns_query(packet)
                    if dns_response_packet is not None:
                        self.network_event_scheduler.log_packet_info(
                            dns_response_packet, "DNS response", self.node_id
                        )
                        self._send_packet(dns_response_packet)

            elif not isinstance(packet, ARPPacket):
                self.network_event_scheduler.log_packet_info(
                    packet, "dropped", self.node_id
                )

    def handle_dns_query(self, dns_packet):
        query_domain = dns_packet.query_domain
        if query_domain in self.dns_records:
            resolved_ip = self.dns_records[query_domain]
            dns_response_packet = DNSPacket(
                source_mac=self.mac_address,
                destination_mac=dns_packet.header["source_mac"],
                source_ip=self.ip_address,
                destination_ip=dns_packet.header["source_ip"],
                query_domain=query_domain,
                query_type="A",
                network_event_scheduler=self.network_event_scheduler,
            )
            dns_response_packet.dns_data = {"resolved_ip": resolved_ip}
            return dns_response_packet
        else:
            return None

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

    def _send_packet(self, packet):
        for link in self.links:
            link.enqueue_packet(packet, self)
