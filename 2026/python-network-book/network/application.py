import random

from .packet import DNSPacket, DHCPPacket, TCPPacket, UDPPacket


class ApplicationManager:
    def __init__(self, node):
        self.node = node

        self.dns_client = DnsClient(node)
        self.dhcp_client = None

        self.ftp_client = None
        self.ftp_server = None
        self.udp_app = None

        self.connection_app_map = {}

    def register_ftp_client(self, ftp_client):
        self.ftp_client = ftp_client

    def register_ftp_server(self, ftp_server):
        self.ftp_server = ftp_server

    def register_udp_app(self, udp_app):
        self.udp_app = udp_app

    def register_dhcp_client(self):
        self.dhcp_client = DhcpClient(self.node)
        if self.node.is_network_address(self.node.ip_address):
            self.dhcp_client.schedule_dhcp_discover()

    def map_connection_to_app(self, connection_key, app_type):
        self.connection_app_map[connection_key] = app_type

    def on_dns_packet_received(self, packet):
        self.dns_client.on_dns_packet_received(packet)

    def on_dhcp_packet_received(self, packet):
        self.dhcp_client.on_dhcp_packet_received(packet)

    def on_packet_received(self, packet):
        protocol = (
            "TCP"
            if isinstance(packet, TCPPacket)
            else ("UDP" if isinstance(packet, UDPPacket) else None)
        )
        if not protocol:
            return

        app_type = self.connection_app_map.get(
            (packet.header.get("source_ip"), packet.header.get("source_port"))
        )

        if app_type == "FTP" and self.ftp_client:
            self.ftp_client.on_dns_packet_received(packet)
        elif app_type == "FTPSERVER" and self.ftp_server:
            self.ftp_server.on_dns_packet_received(packet)
        elif app_type == None and self.ftp_server:
            self.ftp_server.on_packet_received(packet)
        elif app_type == "UDP" and self.udp_app:
            self.udp_app.on_packet_received(packet)
        else:
            pass

    def on_connection_established(self, connection_key):
        app_type = self.connection_app_map.get((connection_key[0], connection_key[1]))
        print("on_connection_established", connection_key, app_type)
        if app_type == "FTP" and self.ftp_client:
            self.ftp_client.on_connection_established(connection_key)
        elif app_type == "FTPSERVER" and self.ftp_server:
            self.ftp_server.on_connection_established(connection_key)
        elif app_type == None and self.ftp_server:
            self.connection_app_map[connection_key] = "FTPSERVER"
            self.ftp_server.on_connection_established(connection_key)

    def get_traffic_info(self, connection_key):
        conn = self.node.tcp_connections.get(connection_key)
        if conn and "transfer_info" in conn:
            return conn["transfer_info"]
        return None

    def get_data_chunk(self, connection_key, payload_size):
        app_type = self.connection_app_map.get(connection_key)
        if app_type == "FTP" and self.ftp_client:
            return self.ftp_client.get_data_chunk(connection_key, payload_size)
        elif app_type == "FTPSERVER" and self.ftp_server:
            return self.ftp_server.get_data_chunk(connection_key, payload_size)
        return None

    def update_data_after_send(self, connection_key, sent_bytes):
        key = (connection_key[0], connection_key[1])
        app_type = self.connection_app_map.get(key)

        print(
            f"[DEBUG update_data_after_send] connection_key={connection_key}, app_type={app_type}"
        )

        if app_type == "FTPSERVER" and self.ftp_server:
            transfer_info = self.node.tcp_connections.get(connection_key, {}).get(
                "transfer_info", {}
            )

            print(
                f"[DEBUG update_data_after_send] transfer_info for {connection_key}: {app_type}"
            )

            if transfer_info.get("file_size", 0) > 0 and not transfer_info.get(
                "transfer_done", False
            ):
                self.ftp_server.update_data_after_send(connection_key, sent_bytes)
                client_ip, client_port = connection_key
                server_port = 21
                self.ftp_server.check_transfer_complete(
                    connection_key, client_ip, client_port, server_port
                )
            else:
                pass

        elif app_type == "FTP" and self.ftp_client:
            transfer_info = self.node.tcp_connections.get(connection_key, {}).get(
                "transfer_info", {}
            )
            print(
                f"[DEBUG update_data_after_send] transfer_info for {connection_key}: {transfer_info}"
            )

            if transfer_info.get("file_size", 0) > 0:
                self.ftp_client.update_data_after_send(connection_key, sent_bytes)
        else:
            print(
                "[DEBUG update_data_after_send] No FTP client/server associated with this connection_key."
            )

    def resolve_destination_url(self, destination_url, callback=None):
        if self.node.is_valid_cidr_notation(destination_url):
            if callback:
                callback(destination_url)
            return destination_url

        if destination_url in self.dns_client.url_to_ip_mapping:
            resolved_ip = self.dns_client.url_to_ip_mapping[destination_url]
            if callback:
                callback(resolved_ip)
            return resolved_ip
        else:
            self.dns_client.resolve_domain(destination_url, callback)
            return None

    def check_dns_resolution(self):
        self.dns_client.check_pending_queries()


class DnsClient:
    def __init__(self, node):
        self.node = node
        self.url_to_ip_mapping = {}
        self.pending_queries = {}

    def resolve_domain(self, domain, callback=None):
        if domain in self.url_to_ip_mapping:
            if callback:
                callback(self.url_to_ip_mapping[domain])
            return
        if not self.node.dns_server_ip:
            print("No DNS server IP set. Cannot resolve domain.")
            return

        print(f"Node {self.node.node_id} sending DNS query for {domain}")
        dns_query_packet = DNSPacket(
            source_mac=self.node.mac_address,
            destination_mac="FF:FF:FF:FF:FF:FF",
            source_ip=self.node.ip_address,
            destination_ip=self.node.dns_server_ip,
            query_domain=domain,
            query_type="A",
            network_event_scheduler=self.node.network_event_scheduler,
        )
        self.pending_queries[domain] = callback
        self.node._send_packet(dns_query_packet)

    def on_dns_packet_received(self, packet):
        if packet.query_domain and "resolved_ip" in packet.dns_data:
            domain = packet.query_domain
            resolved_ip = packet.dns_data["resolved_ip"]
            self.url_to_ip_mapping[domain] = resolved_ip
            print(f"DNS resolved: {domain} -> {resolved_ip}")
            if domain in self.pending_queries and self.pending_queries[domain]:
                self.pending_queries[domain](resolved_ip)
            if domain in self.pending_queries:
                del self.pending_queries[domain]

    def check_pending_queries(self):
        pass

class DhcpClient:
    def __init__(self, node):
        self.node = node
        self.state = "INIT"
        self.resolved_ip = None
        self.retries = 0
        self.max_retries = 3
        self.retry_timeout = 2.0

    def schedule_dhcp_discover(self):
        initial_delay = random.uniform(0.5, 0.6)
        self.node.network_event_scheduler.schedule_event(
            self.node.network_event_scheduler.current_time + initial_delay,
            self.send_dhcp_discover,
        )

    def send_dhcp_discover(self):
        print(
            f"Node {self.node.node_id} sending DHCP DISCOVER (attempt {self.retries + 1}/{self.max_retries})"
        )

        dhcp_discover_packet = DHCPPacket(
            source_mac=self.node.mac_address,
            destination_mac="FF:FF:FF:FF:FF:FF",
            source_ip="0.0.0.0/32",
            destination_ip="255.255.255.255/32",
            message_type="DISCOVER",
            network_event_scheduler=self.node.network_event_scheduler,
        )

        self.node._send_packet(dhcp_discover_packet)
        self.node.network_event_scheduler.log_packet_info(
            dhcp_discover_packet, "DHCP Discover sent", self.node.node_id
        )
        self.state = "DISCOVER_SENT"

        if self.retries < self.max_retries:
            self.node.network_event_scheduler.schedule_event(
                self.node.network_event_scheduler.current_time + self.retry_timeout,
                self.retry_discover,
            )

    def retry_discover(self):
        if self.state == "DISCOVER_SENT":
            self.retries += 1
            if self.retries < self.max_retries:
                self.send_dhcp_discover()
            else:
                print(
                    f"Node {self.node.node_id} failed to get DHCP response after {self.max_retries} attempts"
                )

    def on_dhcp_packet_received(self, packet):
        self.node.network_event_scheduler.log_packet_info(
            packet, "arrived", self.node.node_id
        )
        packet.set_arrived(self.node.network_event_scheduler.current_time)

        if packet.message_type == "OFFER" and self.state == "DISCOVER_SENT":
            self.node.network_event_scheduler.log_packet_info(
                packet, "DHCP Offer received", self.node.node_id
            )
            offered_ip = packet.dhcp_data.get("offered_ip")
            if offered_ip:
                self.send_dhcp_request(offered_ip)
                self.state = "REQUEST_SENT"

        elif packet.message_type == "ACK" and self.state == "REQUEST_SENT":
            self.node.network_event_scheduler.log_packet_info(
                packet, "DHCP ACK received", self.node.node_id
            )
            assigned_ip = packet.dhcp_data.gtet("assigned_ip")
            dns_server_ip = packet.dhcp_data.get("dns_server_ip")
            if assigned_ip:
                self.node.set_ip_address(assigned_ip)
                print(
                    f"Node {self.node.node_id} has been assigned the IP address {assigned_ip}."
                )
            if dns_server_ip:
                self.node.set_dns_server_ip(dns_server_ip)
                print(
                    f"Node {self.node.node_id} has been assigned the DNS server IP address {dns_server_ip}."
                )
            self.state = "BOUND"

    def send_dhcp_request(self, requested_ip):
        print(f"Node {self.node.node_id} sending DHCP REQUEST for IP {requested_ip}")
        
        dhcp_request_packet = DHCPPacket(
            source_mac=self.node.mac_address,
            destination_mac="FF:FF:FF:FF:FF:FF",
            source_ip="0.0.0.0/32",
            destination_mac="255.255.255.255/32",
            message_type="REQUEST",
            network_event_scheduler=self.node.network_event_scheduler,
        )
        dhcp_request_packet.dhcp_data = {"requested_ip", requested_ip}

        self.node._send_packet(dhcp_request_packet)
        self.node.network_event_scheduler.log_packet_info(
            dhcp_request_packet, "DHCP Request sent", self.node.node_id
        )
        self.state = "REQUEST_SENT"

        self.node.network_event_scheduler.schedule_event(
            self.node.network_event_scheduler.current_time + self.retry_timeout,
            lambda: self.retry_request(requested_ip),
        )

    def retry_request(self, requested_ip):
        if self.state == "REQUEST_SENT":
            self.retries += 1
            if self.retries < self.max_retries:
                self.send_dhcp_request(requested_ip)
            else:
                print(
                    f"Node {self.node.node_id} failed to get DHCP ACK after {self.max_retries} attempts"
                )


class UDPApp:
    def __init__(self, node, protocol="UDP"):
        self.node = node
        self.app_manager = node.application_layer
        self.protocol = None
        self.bitrate = None
        self.header_size = None
        self.payload_size = None
        self.dscp = 0
        self.destination_ip = None
        self.destination_port = None
        self.source_port = None
        self.end_time = None

    def start_traffic(
        self,
        destination_url,
        bitrate,
        start_time,
        duration,
        header_size,
        payload_size,
        burstiness=1.0,
        dscp=0,
    ):
        self.bitrate = bitrate
        self.header_size = header_size
        self.payload_size = payload_size
        self.burstiness = burstiness
        self.dscp  = dscp
        self.end_time = self.node.network_event_scheduler.current_time + duration

        self.source_port = self.node.select_random_port()
        self.destination_port = self.node.select_random_port()

        def on_resolved(ip):
            self.destination_ip = ip
            current_time = self.node.network_event_scheduler.current_time
            delay = max(0, start_time - current_time)
            self.node.network_event_scheduler.schedule_event(
                current_time + delay, sself.schedule_traffic
            )
            self.app_manager.map_connection_to_app((ip, self.destination_port), "UDP")

        resolved_ip = self.app_manager.resolve_destination_url(
            destination_url, callback=on_resolved
        )
        if resolved_ip is not None:
            self.destination_ip = resolved_ip
            self.node.network_event_scheduler.schedule_event(
                start_time, self.schedule_traffic
            )
            self.app_manager.map_connection_to_app(
                (resolved_ip, self.destination_port), "UDP"
            )

    def schedule_traffic(self):
        self.send_packet_event()

    def send_packet_event(self):
        current_time = self.node.network_event_scheduler.current_time
        if current_time > self.end_time:
            return

        data = b"X" * self.payload_size
        self.node.send_app_data(
            self.destination_ip,
            data,
            protocol=self.protocol,
            dscp=self.dscp,
            source_port=self.source_port,
            destination_port=self.destination_port,
        )
        packet_size = self.header_size + self.payload_size
        interval = (packet_size * 8) / self.bitrate * self.burstiness
        next_time = current_time + interval
        self.node.network_event_scheduler.schedule_event(
            next_time, self.send_packet_event
        )

    def on_packet_received(self, packet):
        pass


class FTPClient:
    def __init__(self, node, verbose=False):
        self.node = node
        self.app_manager = (
            node.application_layer
        )
        self.verbose = verbose
        self.state = "NOT_CONNECTED"
        self.file_to_retrieve = None
        self.outgoing_data = {}

    def connect(self, server_ip=None, server_url=None, server_port=21):
        if server_ip:
            self._initiate_connection(server_ip, server_port)
        elif server_url:
            self.server_url = server_url
            if self.verbose:
                print("[FTPClient] サーバURLからIPを解決しています:", server_url)
            
            def on_resolved(ip):
                if ip:
                    if self.verbose:
                        print("[FTPClient] 解決されたIP:", ip)
                    self._initiate_connection(ip, server_port)
                else:
                    if self.verbose:
                        print("[FTPClient] サーバURLの解決に失敗しました:", server_url)

            resolved_ip = self.app_manager.resolve_destination_url(
                server_url, callback=on_resolved
            )
            if resolved_ip is not None:
                on_resolved(resolved_ip)
        else:
            if self.verbose:
                print(
                    "[FTPClient] 接続情報が不足しています。server_ipまたはserver_urlを指定してください。"
                )

    def _initiate_connection(self, server_ip, server_port):
        if self.verbose:
            print("[FTPClient] TCP接続を要求しています:", server_ip, server_port)
        self.server_ip = server_ip
        self.server_port = server_port
        self.state = "CONNECTING"
        self.node.initiate_tcp_handshake(
            server_ip, server_port
        )
        self.app_manager.map_connection_to_app(
            (server_ip, server_port), "FTP"
        )

    def on_packet_received(self, packet):
        data = packet.payload.decode(
            "utf-8", errors="ignore"
        )
        if self.verbose:
            print("[FTPClient] 受信データ:", data.strip())

        if data.startswith("220"):
            self.state = "LOGGED_OUT"
            self.send_ftp_command("USER anonymous\r\n")
        elif data.startswith("331"):
            self.send_ftp_command("PASS anonymous@\r\n")
        elif data.startswith("230"):
            self.state = "LOGGED_IN"
            if self.file_to_retrieve:
                self.send_ftp_command(f"RETR {self.file_to_retrieve}\r\n")
        elif data.startswith("150"):
            pass
        elif data.startswith("226"):
            pass
        elif data.startswith("226"):
            pass

    def on_connection_established(self, connection_key):
        self.set_traffic_info(connection_key)
        if self.verbose:
            print(
                "[FTPClient] Connection established. Waiting for server greeting (220)..."
            )

    def send_ftp_command(self, command):
        if self.verbose:
            print("[FTPClient] 送信コマンド:", command.strip())
        self.node.send_app_data(
            self.server_ip,
            command.encode("utf-8"),
            protocol="TCP",
            destination_port=self.server_port,
        )

    def retrieve_file(self, filename):
        self.file_to_retrieve = filename
        if self.verbose:
            print("[FTPClient] Will retrieve file after login:", filename)

    def set_traffic_info(self, connection_key):
        end_time = self.node.network_event_scheduler.current_time + 3600
        payload_size = 1460
        self.node.tcp_connections[connection_key]["transfer_info"] = {
            "end_time": end_time,
            "payload_size": payload_size,
            "bytes_transferred": 0,
            "progress": [],
            "file_size": 0,
            "transfer_done": False,
        }

    def get_traffic_info(self, connection_key):
        return self.node.tcp_connections[connection_key].get("transfer_info", None)

    def get_data_chunk(self, connection_key, payload_size):
        data = self.outgoing_data.get(connection_key, b"")
        chunk = data[:payload_size]
        return chunk

    def update_data_after_send(self, connection_key, sent_bytes):
        data = self.outgoing_data.get(connection_key, b"")
        self.outgoing_data[connection_key] = data[sent_bytes:]


class FTPServer:
    def __init__(self, node, shared_files, verbose=False):
        self.node = node
        self.app_manager = node.application_layer
        self.shared_files = shared_files
        self.verbose = verbose
        self.state = "READY"
        self.outgoing_data = {}

    def on_connection_established(self, connection_key);
        self.set_traffic_info(connection_key)
        client_ip, client_port = connection_key
        server_port = 21
        if self.verbose:
            print("[FTPServer] Connection established. Sending 220 greeting.")
        self.send_ftp_response(
            client_ip, client_port, server_port, "220 Service ready\r\n"
        )
        self.state = "WAIT_USER"

    def on_packet_received(self, packet):
        data = packet.payload.decode("utf-8", errors="ignore")
        if self.verbose:
            print("[FTPServer] Received: ", data.strip())

        client_ip = packet.header["source_ip"]
        client_port = packet.header["source_port"]
        server_port = packet.header["destination_port"]
        connection_key = (client_ip, client_port)

        if self.state == "WAIT_USER":
            if data.startswith("USER"):
                self.send_ftp_response(
                    client_ip,
                    client_port,
                    server_port,
                    "331 User name okay, need password.\r\n",
                )
            elif data.startswith("PASS"):
                self.send_ftp_response(
                    client_ip,
                    client_port,
                    server_port,
                    "230 User logged in, proceed.\r\n",
                )
                self.state = "LOGGED_IN"

        elif self.state == "LOGGED_IN":
            if data.startswith("RETR"):
                parts = data.strip().split(" ", 1)
                if len(parts) < 2:
                    self.send_ftp_response(
                        client_ip,
                        client_port,
                        server_port,
                        "501 Syntax error in parameters or arguments.\r\n",
                    )
                    return
                filename = parts[1]
                file_data = self.shared_files.get(filename, None)
                if file_data is None:
                    self.send_ftp_response(
                        client_ip, client_port, server_port, "550 file not found.\r\n"
                    )
                    return

                file_size = len(file_data)
                transfer_info = {
                    "end_time": self.node.network_event_scheduler.current_time + 3600,
                    "payload_size": 1460,
                    "bytes_transferred": 0,
                    "progress": [],
                    "file_size":file_size,
                    "transfer_done": False,
                }

                self.node.tcp_connections[connection_key]["transfer_info"] = (
                    transfer_info
                )
                self.outgoing_data[connection_key] = file_data

                self.send_ftp_response(
                    client_ip,
                    client_port,
                    server_port,
                    "150 File status okay; about to open data connection.\r\n",
                )
                self.send_next_chunk(
                    connection_key, client_ip, client_port, server_port
                )

    def send_next_chunk(self, connection_key, client_ip, client_port, server_port):
        chunk = self.get_data_chunk(
            connection_key,
            self.node.tcp_connections[connection_key]["transfer_info"]["payload_size"],
        )
        if chunk:
            self.node.send_app_data(
                client_ip,
                chunk,
                protocol="TCP",
                source_port=server_port,
                destination_port=client_port,
            )
        else:
            pass

    def get_data_chunk(self, connection_key, payload_size):
        if connection_key not in self.outgoing_data:
            return b""
        data = self.outgoing_data[connection_key]
        if not data:
            return b""
        chunk = data[:payload_size]
        self.outgoing_data[connection_key] = data[payload_size:]
        return chunk

    def update_data_after_send(self, connection_key, bytes_sent):
        ti = self.node.tcp_connections[connection_key]["transfer_info"]
        self.check_transfer_complete(connection_key, *connection_key, 21)

    def check_transfer_complete(
        self, connection_key, client_ip, client_port, server_port
    ):
        ti = self.node.tcp_connections[connection_key]["transfer_info"]
        if ti["bytes_transferred"] >= ti["file_size"] and not self.outgoing_data.get(
            connection_key, b""
        ):
            if not ti["transfer_done"]:
                ti["transfer_done"] = True
                self.send_ftp_response(
                    client_ip,
                    client_port,
                    server_port,
                    "226 Closing data connection.\r\n",
                )
                if self.verbose:
                    print(
                        f"[FTPServer] Transfer complete for {connection_key}. Sent 226 response."
                    )

    def send_ftp_response(self, dst_ip, client_port, server_port, response):
        if self.verbose:
            print("[FTPServer] Sending response:", response.strip())
        self.node.send_control_tcp_packet(
            dst_ip=dst_ip,
            data=response.encode("utf-8"),
            dscp=0,
            source_port=server_port,
            destination_port=client_port,
            flags="ACK",
        )

    def set_traffic_info(self, connection_key):
        end_time = self.node.network_event_scheduler.current_time + 3600
        payload_size = 1460
        self.node.tcp_connections[connection_key]["transfer_info"] = {
            "end_time": end_time,
            "payload_size": payload_size,
            "bytes_transferred": 0,
            "progress": [],
            "file_size": 0,
            "transfer_done": False,
        }

    def get_traffic_info(self, connection_key):
        return self.node.tcp_connections[connection_key].get("transfer_info", None)
