import uuid


class Packet:
    def __init__(
        self,
        source_mac,
        destination_mac,
        source_ip,
        destination_ip,
        ttl,
        fragment_flags,
        fragment_offset,
        header_size,
        payload_size,
        network_event_scheduler,
    ):
        self.network_event_scheduler = network_event_scheduler
        self.id = str(uuid.uuid4())
        self.mac_header = {"source_mac": source_mac, "destination_mac": destination_mac}
        self.ip_header = {
            "source_ip": source_ip,
            "destination_ip": destination_ip,
            "ttl": ttl,
            "fragment_flags": fragment_flags,
            "fragment_offset": fragment_offset,
        }

        self.size = header_size + payload_size
        self.creation_time = self.network_event_scheduler.current_time
        self.arrival_time = None

    @property
    def header(self):
        return {**self.mac_header, **self.ip_header}

    def remove_mac_header(self):
        self.mac_header = {}

    def add_mac_header(self, source_mac, destination_mac):
        self.mac_header = {"source_mac": source_mac, "destination_mac": destination_mac}

    def set_arrived(self, arrival_time):
        self.arrival_time = arrival_time

    def __lt__(self, other):
        return False

    def __str__(self):
        source_mac = self.mac_header.get("source_mac", "不明")
        destination_mac= self.mac_header.get("destination_mac", "不明")
        return f"パケット(送信元MAC: {self.header['source_mac']}, 宛先MAC: {self.header['destination_mac']}, 送信元IP: {self.header['source_ip']}, 宛先IP: {self.header['destination_ip']}, TTL: {self.header['ttl']}, フラグメントフラグ: {self.header['fragment_flags']}, フラグメントオフセット: {self.header['fragment_offset']}, ペイロード: {self.payload})"

class TCPPacket(Packet):
    def __init__(
        self,
        source_port,
        destination_port,
        sequence_number,
        acknowledgment_number,
        flags,
        data=b"",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.tcp_header = {
            "source_port": source_port,
            "destination_port": destination_port,
            "sequence_number": sequence_number,
            "acknowledgment_number": acknowledgment_number,
            "flags": flags
        }
        self.payload = data

    @property
    def header(self):
        return {**self.mac_header, **self.ip_header, **self.tcp_header}

class UDPPacket(Packet):
    def __init__(self, source_port, destination_port, data=b"", **kwargs):
        super().__init__(**kwargs)
        self.udp_header = {
            "source_port": source_port,
            "destination_port": destination_port,
        }
        self.payload = data

    @property
    def header(self):
        return {**self.mac_header, **self.ip_header, **self.udp_header}

class ARPPacket(Packet):
    def __init__(
        self,
        source_mac,
        destination_mac,
        source_ip,
        destination_ip,
        operation,
        network_event_scheduler,
    ):
        super().__init__(
            source_mac=source_mac,
            destination_mac=destination_mac,
            source_ip=source_ip,
            destination_ip=destination_ip,
            ttl=1,
            fragment_flags={},
            fragment_offset=0,
            header_size=28,
            payload_size=28,
            network_event_scheduler=network_event_scheduler,
        )

        self.payload = {
            "operation": operation,
            "source_mac": source_mac,
            "destination_mac": destination_mac,
            "source_ip": source_ip,
            "destination_ip": destination_ip,
        }

        def __str__(self):
            return f"ARPPacket(送信元MAC: {self.mac_header['source_mac']}, 宛先MAC: {self.mac_header['destination_mac']}, 操作: {self.payload['operation']})"


class DNSPacket(Packet):
    def __init__(
        self,
        source_mac,
        destination_mac,
        source_ip,
        destination_ip,
        query_domain,
        query_type,
        network_event_scheduler,
    ):
        super().__init__(
            source_mac=source_mac,
            destination_mac=destination_mac,
            source_ip=source_ip,
            destination_ip=destination_ip,
            ttl=64,
            fragment_flags={},
            fragment_offset=0,
            header_size=0,
            payload_size=0,
            network_event_scheduler=network_event_scheduler,
        )
        self.query_domain = query_domain
        self.query_type = query_type
        self.dns_data = {}

    def __str__(self):
        source_mac = self.mac_header.get("source_mac", "不明")
        destination_mac = self.mac_header.get("destination_mac", "不明")
        return f"DNSPacket(送信元MAC: {source_mac}, 宛先MAC: {destination_mac}, 送信元IP: {self.ip_header['source_ip']}, 宛先IP: {self.ip_header['destination_ip']}, Query Domain: {self.query_domain}, Query Type: {self.query_type})"

class DHCPPacket(Packet):
    def __init__(
        self,
        source_mac,
        destination_mac,
        source_ip,
        destination_ip,
        message_type,
        network_event_scheduler,
    ):
        super().__init__(
            source_mac=source_mac,
            destination_mac=destination_mac,
            source_ip=source_ip,
            destination_ip=destination_ip,
            ttl=255,
            fragment_flags={},
            fragment_offset=0,
            header_size=240,
            payload_size=0,
            network_event_scheduler=network_event_scheduler,
        )
        self.message_type = (
            message_type
        )
        self.dhcp_data = {}

    def __str__(self):
        source_mac = self.mac_header.get("source_mac", "不明")
        destination_mac = self.mac_header.get("destination_mac", "不明")
        return f"DHCPPacket(送信元MAC: {source_mac}, 宛先MAC: {destination_mac}, 送信元IP: {self.ip_header['source_ip']}, 宛先IP: {self.ip_header['destination_ip']}, Message Type: {self.message_type})"


class BPDU(Packet):
    def __init__(
        self,
        source_mac,
        destination_mac,
        root_id,
        bridge_id,
        path_cost,
        network_event_scheduler,
    ):
        super().__init__(
            source_mac=source_mac,
            destination_mac=destination_mac,
            source_ip="0.0.0.0/24",
            destination_ip="0.0.0.0/24",
            ttl=1,
            fragment_flags={},
            fragment_offset=0,
            header_size=20,
            payload_size=50,
            network_event_scheduler=network_event_scheduler,
        )
        self.payload = {
            "root_id": root_id,
            "bridge_id": bridge_id,
            "path_cost": path_cost,
        }

    def __str__(self):
        return f"BPDU(送信元: {self.header['source_mac']}, 宛先: {self.header['destination_mac']}, ルートID: {self.payload['root_id']}, ブリッジID: {self.payload['bridge_id']}, パスコスト: {self.payload['path_cost']})"


class HelloPacket(Packet):
    def __init__(
        self,
        source_mac,
        source_ip,
        network_mask,
        router_id,
        hello_interval,
        neighbors,
        network_event_scheduler,
    ):
        super().__init__(
            source_mac=source_mac,
            destination_mac="FF:FF:FF:FF:FF:FF",
            source_ip=source_ip,
            destination_ip="224.0.0.5",
            ttl=1,
            fragment_flags={},
            fragment_offset=0,
            header_size=24,
            payload_size=20,
            network_event_scheduler=network_event_scheduler,
        )
        self.payload = {
            "network_mask": network_mask,
            "router_id": router_id,
            "hello_interval": hello_interval,
            "neighbors": neighbors,
        }

    def __str__(self):
        return f"HelloPacket(送信元MAC: {self.header['source_mac']}, 宛先MAC: {self.header['destination_mac']}, 送信元IP: {self.header['source_ip']}, ネットワークマスク: {self.payload['network_mask']}, ルータID: {self.payload['router_id']}, Helloインターバル: {self.payload['hello_interval']}, 隣接ルータ: {self.payload['neighbors']})"


class LSAPacket(Packet):
    def __init__(
        self,
        source_mac,
        source_ip,
        router_id,
        sequence_number,
        link_state_info,
        network_event_scheduler,
    ):
        super().__init__(
            source_mac=source_mac,
            destination_mac="FF:FF:FF:FF:FF:FF",
            source_ip=source_ip,
            destination_ip="224.0.0.5",
            ttl=1,
            fragment_flags={},
            fragment_offset=0,
            header_size=24,
            payload_size=100,
            network_event_scheduler=network_event_scheduler,
        )
        self.payload = {
            "router_id": router_id,
            "sequence_number": sequence_number,
            "link_state_info": link_state_info,
        }

    def __str__(self):
        return f"LSAPacket(送信元MAC: {self.header['source_mac']}, 送信元IP: {self.header['source_ip']}, トポロジ情報: {self.payload['link_state_info']})"
