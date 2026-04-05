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
        self.header = {
            "source_mac": source_mac,
            "destination_mac": destination_mac,
            "source_ip": source_ip,
            "destination_ip": destination_ip,
            "ttl": ttl,
            "fragment_flags": fragment_flags,
            "fragment_offset": fragment_offset,
        }
        self.payload = b"X" * payload_size
        self.size = header_size + payload_size
        self.creation_time = self.network_event_scheduler.current_time
        self.arrival_time = None

    def set_arrived(self, arrival_time):
        self.arrival_time = arrival_time

    def __lt__(self, other):
        return False

    def __str__(self):
        return f"パケット(送信元MAC: {self.header['source_mac']}, 宛先MAC: {self.header['destination_mac']}, 送信元IP: {self.header['source_ip']}, 宛先IP: {self.header['destination_ip']}, TTL: {self.header['ttl']}, フラグメントフラグ: {self.header['fragment_flags']}, フラグメントオフセット: {self.header['fragment_offset']}, ペイロード: {self.payload})"


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
            source_mac,
            destination_mac,
            source_ip="0.0.0.0/24",
            destination_ip="0.0.0.0/24",
            ttl=64,
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
