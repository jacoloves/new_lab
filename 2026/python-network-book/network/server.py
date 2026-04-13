import uuid
from ipaddress import ip_network

from .packet import ARPPacket, DNSPacket, DHCPPacket


class Server:
    def __init__(self, node_id, ip_address, network_event_scheduler, mac_address=None):
        self.node_id = node_id
        self.ip_address = ip_address
        self.network_event_scheduler = network_event_scheduler
        self.mac_address = mac_address if mac_address else self.generate_mac_address()
        self.links = []

    def generate_mac_address(self):
        return ":".join(
            [
                "{:02x}".format(uuid.uuid4().int >> elements & 0xFF)
                for elements in range(0, 12, 2)
            ]
        )

    def add_link(self, link, ip_address=None):
        if link not in self.links:
            self.links.append(link)

    def mark_ip_as_used(self, ip_address):
        pass

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


class DNSServer(Server):
    def __init__(self, node_id, ip_address, network_event_scheduler, mac_address=None):
        super().__init__(node_id, ip_address, network_event_scheduler, mac_address)
        self.dns_records = {}
        label = f"DNSServer {node_id}"
        self.network_event_scheduler.add_node(node_id, label, ip_addresses=[ip_address])

    def add_dns_record(self, domain_name, ip_address):
        self.dns_records[domain_name] = ip_address

    def receive_packet(self, packet, received_link):
        super().receive_packet(packet, received_link)

        if (
            packet.header["destination_mac"] == "FF:FF:FF:FF:FF:FF"
            or packet.header["destination_mac"] == self.mac_address
        ):
            if (
                isinstance(packet, DNSPacket)
                and packet.header["destination_ip"] == self.ip_address
            ):
                self.network_event_scheduler.log_packet_info(
                    packet, "arrived", self.node_id
                )
                packet.set_arrived(self.network_event_scheduler.current_time)

                self.network_event_scheduler.log_packet_info(
                    packet, "DNS query received", self.node_id
                )
                dns_response_packet = self.handle_dns_query(packet)
                self.network_event_scheduler.log_packet_info(
                    dns_response_packet, "DNS response", self.node_id
                )
                self._send_packet(dns_response_packet)

            else:
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


class DHCPServer(Server):
    def __init__(
        self,
        node_id,
        ip_address,
        dns_server_ip,
        network_event_scheduler,
        start_cidr,
        mac_address=None,
    ):
        super().__init__(node_id, ip_address, network_event_scheduler, mac_address)
        self.ip_pool = self.initialize_ip_pool(start_cidr)
        self.used_ips = set()
        self.dns_server_ip = dns_server_ip
        label = f"DHCPServer {node_id}"
        self.network_event_scheduler.add_node(node_id, label, ip_addresses=[ip_address])

    def initialize_ip_pool(self, start_cidr):
        network = ip_network(start_cidr, strict=False)
        ip_pool = [f"{ip}/{network.prefixlen}" for ip in network.hosts()]
        return ip_pool

    def get_available_ip(self):
        for ip in self.ip_pool:
            if ip not in self.used_ips:
                self.used_ips.add(ip)
                return ip
        return None

    def mark_ips_as_used(self, ips):
        for ip in ips:
            self.used_ips.add(ip)

    def receive_packet(self, packet, received_link):
        super().receive_packet(packet, received_link)

        if (
            packet.header["destination_mac"] == "FF:FF:FF:FF:FF:FF"
            and packet.header["destination_ip"] == "255.255.255.255/32"
        ):
            if isinstance(packet, DHCPPacket):
                if packet.message_type == "DISCOVER":
                    self.handle_dhcp_discover(packet)
                elif packet.message_type == "REQUEST":
                    self.handle_dhcp_request(packet)
                else:
                    pass

    def handle_dhcp_discover(self, discover_packet):
        if self.ip_pool:
            assigned_ip = self.get_available_ip()
            offer_packet = self.create_dhcp_offer_packet(discover_packet, assigned_ip)
            self.network_event_scheduler.log_packet_info(
                offer_packet, "DHCP Offer", self.node_id
            )
            self._send_packet(offer_packet)

    def handle_dhcp_request(self, request_packet):
        ack_packet = self.create_dhcp_ack_packet(request_packet)
        self._send_packet(ack_packet)

    def create_dhcp_offer_packet(self, discover_packet, offered_ip):
        dhcp_offer_packet = DHCPPacket(
            source_mac=self.mac_address,
            destination_mac=discover_packet.header["source_mac"],
            source_ip=self.ip_address,
            destination_ip=offered_ip,
            message_type="OFFER",
            network_event_scheduler=self.network_event_scheduler,
        )
        dhcp_offer_packet.dhcp_data = {"offered_ip": offered_ip}
        return dhcp_offer_packet

    def create_dhcp_ack_packet(self, request_packet):
        assigned_ip = request_packet.dhcp_data["requested_ip"]
        dhcp_ack_packet = DHCPPacket(
            source_mac=self.mac_address,
            destination_mac=request_packet.header["source_mac"],
            source_ip=self.ip_address,
            destination_ip=assigned_ip,
            message_type="ACK",
            network_event_scheduler=self.network_event_scheduler,
        )
        dhcp_ack_packet.dhcp_data = {
            "assigned_ip": assigned_ip,
            "dns_server_ip": self.dns_server_ip,
        }
        return dhcp_ack_packet
