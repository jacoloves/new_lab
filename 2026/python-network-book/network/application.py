import random

from network import server
from .packet import DNSPacket, DHCPPacket, TCPPacket, UDPPacket


class ApplicationManager:
    def __init__(self, node):
        self.node = node

        self.dns_client = DnsClient(node)
        self.dhcp_client = None

        self.ftp_client = None
        self.ftp_server = None
        self.http_client = None
        self.http_server = None
        self.https_client = None
        self.https_server = None
        self.udp_app = None

        self.connection_app_map = {}

    def register_ftp_client(self, ftp_client):
        self.ftp_client = ftp_client

    def register_ftp_server(self, ftp_server):
        self.ftp_server = ftp_server

    def register_http_client(self, http_client):
        self.http_client = http_client

    def register_http_server(self, http_server):
        self.http_server = http_server

    def register_https_client(self, https_client):
        self.https_client = https_client

    def register_https_server(self, https_server):
        self.https_server = https_server

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
            self.ftp_client.on_packet_received(packet)
        elif app_type == "FTPSERVER" and self.ftp_server:
            self.ftp_server.on_packet_received(packet)
        elif app_type == "HTTP" and self.http_client:
            self.http_client.on_packet_received(packet)
        elif app_type == "HTTPSERVER" and self.http_server:
            self.http_server.on_packet_received(packet)
        elif app_type == "HTTPS" and self.https_client:
            self.https_client.on_packet_received(packet)
        elif app_type == "HTTPSSERVER" and self.https_server:
            self.https_server.on_packet_received(packet)
        elif app_type == None and (self.ftp_server or self.http_server or self.https_server):
            if packet.header.get("destination_port") == 443 and self.https_server:
                self.connection_app_map[
                    (packet.header.get("source_ip"), packet.header.get("source_port"))
                ] = "HTTPSSERVER"
                self.https_server.on_packet_received(packet)
            elif packet.header.get("destination_port") == 80 and self.http_server:
                self.connection_app_map[
                    (packet.header.get("source_ip"), packet.header.get("source_port"))
                ] = "HTTPSERVER"
                self.http_server.on_packet_received(packet)
            elif self.ftp_server:
                self.ftp_server.on_packet_received(packet)
        elif app_type == "UDP" and self.udp_app:
            self.udp_app.on_packet_received(packet)
        else:
            pass

    def on_connection_established(self, connection_key):
        app_type = self.connection_app_map.get((connection_key[0], connection_key[1]))
        if app_type == "FTP" and self.ftp_client:
            self.ftp_client.on_connection_established(connection_key)
        elif app_type == "FTPSERVER" and self.ftp_server:
            self.ftp_server.on_connection_established(connection_key)
        elif app_type == "HTTP" and self.http_client:
            self.http_client.on_connection_established(connection_key)
        elif app_type == "HTTPS" and self.https_client:
            self.https_client.on_connection_established(connection_key)
        elif app_type == "HTTPSERVER" and self.http_server:
            self.http_server.on_connection_established(connection_key)
        elif app_type == "HTTPSSERVER" and self.https_server:
            self.https_server.on_connection_established(connection_key)
        elif app_type == None:
            # port_mapping[(client_ip, client_port)] = server_port (サーバー側のポートを取得)
            server_port = self.node.port_mapping.get(connection_key)
            if server_port == 443 and self.https_server:
                self.connection_app_map[connection_key] = "HTTPSSERVER"
                self.https_server.on_connection_established(connection_key)
            elif connection_key[1] == 443 and self.https_client:
                self.connection_app_map[connection_key] = "HTTPS"
                self.https_client.on_connection_established(connection_key)
            elif server_port == 80 and self.http_server:
                self.connection_app_map[connection_key] = "HTTPSERVER"
                self.http_server.on_connection_established(connection_key)
            elif self.ftp_server:
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

        if app_type == "FTPSERVER" and self.ftp_server:
            transfer_info = self.node.tcp_connections.get(connection_key, {}).get(
                "transfer_info", {}
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

        elif app_type == "FTP" and self.ftp_client:
            transfer_info = self.node.tcp_connections.get(connection_key, {}).get(
                "transfer_info", {}
            )
            if transfer_info.get("file_size", 0) > 0:
                self.ftp_client.update_data_after_send(connection_key, sent_bytes)

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
        self.retries += 1
        print(
            f"Node {self.node.node_id} sending DHCP DISCOVER (attempt {self.retries}/{self.max_retries})"
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
            assigned_ip = packet.dhcp_data.get("assigned_ip")
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
            destination_ip="255.255.255.255/32",
            message_type="REQUEST",
            network_event_scheduler=self.node.network_event_scheduler,
        )
        dhcp_request_packet.dhcp_data = {"requested_ip": requested_ip}

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
        self.protocol = protocol
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
        self.dscp = dscp
        self.end_time = self.node.network_event_scheduler.current_time + duration

        self.source_port = self.node.select_random_port()
        self.destination_port = self.node.select_random_port()

        def on_resolved(ip):
            self.destination_ip = ip
            current_time = self.node.network_event_scheduler.current_time
            delay = max(0, start_time - current_time)
            self.node.network_event_scheduler.schedule_event(
                current_time + delay, self.schedule_traffic
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
        self.app_manager = node.application_layer
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
        self.node.initiate_tcp_handshake(server_ip, server_port)
        self.app_manager.map_connection_to_app((server_ip, server_port), "FTP")

    def on_packet_received(self, packet):
        data = packet.payload.decode("utf-8", errors="ignore")
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

    def on_connection_established(self, connection_key):
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
                    "file_size": file_size,
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


class HTTPClient:
    def __init__(self, node, server_url=None, verbose=False):
        self.node = node
        self.app_manager = node.application_layer
        self.server_url = server_url
        self.verbose = verbose
        self.state = "NOT_CONNECTED"
        self.file_to_retrieve = None
        self.response_data = {}

    def connect(self, server_ip=None, server_url=None, server_port=80):
        if server_ip:
            self._initiate_connection(server_ip, server_port)
        elif server_url:
            self.server_url = server_url
            if self.verbose:
                print("[HTTPClient] サーバURLからIPを解決しています:", server_url)

            def on_resolved(ip):
                if ip:
                    if self.verbose:
                        print("[HTTPClient] 解決されたIP:", ip)
                    self._initiate_connection(ip, server_port)
                else:
                    if self.verbose:
                        print("[HTTPClient] サーバURLの解決に失敗しました:", server_url)

            resolved_ip = self.app_manager.resolve_destination_url(
                server_url, callback=on_resolved
            )
            if resolved_ip is not None:
                on_resolved(resolved_ip)
        else:
            if self.verbose:
                print(
                    "[HTTPClient] 接続情報が不足しています。server_ipまたはserver_urlを指定してください。"
                )

    def _initiate_connection(self, server_ip, server_port):
        if self.verbose:
            print("[HTTPClient] TCP接続を要求しています:", server_ip, server_port)
        self.server_ip = server_ip
        self.server_port = server_port
        self.state = "CONNECTING"
        self.node.initiate_tcp_handshake(server_ip, server_port)
        self.app_manager.map_connection_to_app((server_ip, server_port), "HTTP")

    def get_file(self, filename):
        self.file_to_retrieve = filename
        if self.state == "CONNECTED":
            self.send_http_request(f"GET /{filename} HTTP/1.0\r\n\r\n")
        elif self.verbose:
            print("[HTTPClient] 接続後にファイルを取得します:", filename)

    def send_http_request(self, request):
        if self.verbose:
            print("[HTTPClient] 送信リクエスト:", request.strip())
        self.node.send_app_data(
            self.server_ip,
            request.encode("utf-8"),
            protocol="TCP",
            destination_port=self.server_port,
        )

    def on_connection_established(self, connection_key):
        self.state = "CONNECTED"
        if self.verbose:
            print("[HTTPClient] 接続が確立しました。")
        if self.file_to_retrieve:
            self.get_file(self.file_to_retrieve)

    def on_packet_received(self, packet):
        data = packet.payload.decode("utf-8", errors="ignore")
        if self.verbose:
            print("[HTTPClient] 受信データ:", data.strip())

        if data.startswith("HTTP/1.0 200 OK"):
            if self.verbose:
                print("[HTTPClient] ファイルの取得に成功しました")
        elif data.startswith("HTTP/1.0 404"):
            if self.verbose:
                print("[HTTPClient] ファイルが見つかりませんでした")


class HTTPServer:
    def __init__(self, node, shared_files, verbose=False):
        self.node = node
        self.app_manager = node.application_layer
        self.shared_files = shared_files
        self.verbose = verbose
        self.state = "READY"

    def on_connection_established(self, connection_key):
        if self.verbose:
            print("[HTTPServer] Connection established.")
        self.state = "READY"

    def on_packet_received(self, packet):
        data = packet.payload.decode("utf-8", errors="ignore")
        if self.verbose:
            print("[HTTPServer] Received:", data.strip())

        client_ip = packet.header["source_ip"]
        client_port = packet.header["source_port"]
        server_port = packet.header["destination_port"]

        if data.startswith("GET"):
            parts = data.split(" ")
            if len(parts) < 2:
                self.send_http_response(
                    client_ip,
                    client_port,
                    server_port,
                    "HTTP/1.0 400 Bad Request\r\n\r\n",
                )
                return

            filename = parts[1].lstrip("/").split()[0]
            file_data = self.shared_files.get(filename, None)

            if file_data is None:
                self.send_http_response(
                    client_ip,
                    client_port,
                    server_port,
                    "HTTP/1.0 404 Not Found\r\n\r\n",
                )
                return

            header = f"HTTP/1.0 200 OK\r\nContent-Length: {len(file_data)}\r\n\r\n"
            response_bytes = header.encode("utf-8") + file_data

            if self.verbose:
                print(f"[HTTPServer] Sending file {filename} ({len(file_data)} bytes)")

            self.send_http_response(client_ip, client_port, server_port, response_bytes)

    def send_http_response(self, client_ip, client_port, server_port, response):
        if isinstance(response, str):
            response = response.encode("utf-8")
        if self.verbose:
            print("[HTTPServer] Sending response:", response[:50])
        self.node.send_app_data(
            client_ip,
            response,
            protocol="TCP",
            source_port=server_port,
            destination_port=client_port,
        )


class TLSClient:
    def __init__(self, node, verbose=False):
        self.node = node
        self.verbose = verbose
        self.handshake_state = {}
        self.shared_keys = {}

    def get_state(self, connection_key):
        return self.handshake_state.get(connection_key, "IDLE")

    def is_established(self, connection_key):
        return self.get_state(connection_key) == "ESTABLISHED"

    def start_handshake(self, connection_key):
        if self.verbose:
            print(
                f"[TLSClient] start_handshake: Sending ClientHello for {connection_key}"
            )

        self.handshake_state[connection_key] = "WAIT_SERVER_HELLO"
        self.shared_keys[connection_key] = None

        self._send_tls_message(connection_key, b"ClientHello")

    def on_packet_received(self, packet):
        data = packet.payload
        if not data:
            if self.verbose:
                print("[TLSClient] Received empty payload (likely ACK). Ignoring.")
            return

        src_ip = packet.header["source_ip"]
        src_port = packet.header["source_port"]
        connection_key = (src_ip, src_port)

        state = self.get_state(connection_key)
        if state.startswith("WAIT"):
            self._handle_handshake_message(connection_key, data)
        else:
            if self.is_established(connection_key):
                if self.verbose:
                    print(
                        f"[TLSClient] Received encrypted data in established state: {data[:50]} ..."
                    )

    def _handle_handshake_message(self, connection_key, data):
        state = self.get_state(connection_key)

        if state == "WAIT_SERVER_HELLO":
            if data.startswith(b"ServerHello"):
                if self.verbose:
                    print(f"[TLSClient] Received ServerHello from {connection_key}")
                self._send_tls_message(connection_key, b"ClientKeyExchange")
                self.handshake_state[connection_key] = "WAIT_SERVER_FINISHED"

        elif state == "WAIT_SERVER_FINISHED":
            if data.startswith(b"ServerFinished"):
                self._send_tls_message(connection_key, b"ClientFinished")
                self.handshake_state[connection_key] = "ESTABLISHED"
                if self.verbose:
                    print(
                        f"[TLSClient] TLS Handshake finished for {connection_key}"
                    )
            else:
                if self.verbose:
                    print(
                        f"[TLSClient] Unexpected handshake message. Received: {data}"
                    )

    def _send_tls_message(self, connection_key, msg: bytes):
        dst_ip, dst_port = connection_key
        if self.verbose:
            print(
                f"[TLSClient] Sending TLS message {msg[:30]}... to {dst_ip}:{dst_port}"
            )
            print(
                f"[TLSClient] Current handshake state for {connection_key}: {self.get_state(connection_key)}"
            )
        self.node.send_app_data(
            dst_ip,
            msg,
            protocol="TCP",
            destination_port=dst_port,
        )

    def encrypt(self, connection_key, plaintext: bytes) -> bytes:
        if not self.is_established(connection_key):
            return plaintext

        return b"ENC(" + plaintext + b")"

    def decrypt(self, connection_key, ciphertext: bytes) -> bytes:
        if not self.is_established(connection_key):
            return ciphertext

        if ciphertext.startswith(b"ENC(") and ciphertext.endswith(b")"):
            return ciphertext[4:-1]
        return ciphertext


class TLSServer:
    def __init__(self, node, verbose=False):
        self.node = node
        self.verbose = verbose
        self.handshake_state = {}
        self.shared_keys = {}

    def get_state(self, connection_key):
        return self.handshake_state.get(connection_key, "IDLE")

    def is_established(self, connection_key):
        return self.get_state(connection_key) == "ESTABLISHED"

    def accept_handshake(self, connection_key):
        self.handshake_state[connection_key] = "WAIT_CLIENT_HELLO"
        self.shared_keys[connection_key] = None
        if self.verbose:
            print(f"[TLSServer] Ready to accept TLS handshake from {connection_key}")

    def on_packet_received(self, packet):
        data = packet.payload
        if not data:
            if self.verbose:
                print("[TLSServer] Received empty payload (likely ACK). Ignoring.")
            return

        src_ip = packet.header["source_ip"]
        src_port = packet.header["source_port"]
        dst_port = packet.header["destination_port"]
        connection_key = (src_ip, src_port)

        if self.verbose:
            print(
                f"[TLSServer] Received packet from {src_ip}:{src_port} to port {dst_port}"
            )
            print(f"[TLSServer] Payload: {data[:50]}...")
            print(
                f"[TLSServer] Current handshake state for {connection_key}: {self.get_state(connection_key)}"
            )

        state = self.get_state(connection_key)
        if state.startswith("WAIT"):
            self._handle_handshake_message(connection_key, data)
        else:
            if self.is_established(connection_key):
                if self.verbose:
                    print(
                        f"[TLSServer] Received encrypted data in established state: {data[:50]} ..."
                    )

    def _handle_handshake_message(self, connection_key, data):
        state = self.get_state(connection_key)

        if state == "WAIT_CLIENT_HELLO":
            if data.startswith(b"ClientHello"):
                if self.verbose:
                    print(f"[TLSServer] Received ClientHello, sending ServerHello")
                self._send_tls_message(connection_key, b"ServerHello")
                self.handshake_state[connection_key] = "WAIT_CLIENT_KEYEXCHANGE"

        elif state == "WAIT_CLIENT_KEYEXCHANGE":
            if data.startswith(b"ClientKeyExchange"):
                if self.verbose:
                    print(
                        f"[TLSServer] Received ClientKeyExchange, sending ServerFinished"
                    )
                self._send_tls_message(connection_key, b"ServerFinished")
                self.handshake_state[connection_key] = "WAIT_CLIENT_FINISHED"

        elif state == "WAIT_CLIENT_FINISHED":
            if data.startswith(b"ClientFinished"):
                if self.verbose:
                    print(f"[TLSServer] Received ClientFinished, handshake complete")
                self.handshake_state[connection_key] = "ESTABLISHED"
                self.shared_keys[connection_key] = b"MySharedKey"
                if self.verbose:
                    print(f"[TLSServer] TLS Handshake finished for {connection_key}")
            else:
                if self.verbose:
                    print(f"[TLSServer] Unexpected handshake message. Received: {data}")

    def _send_tls_message(self, connection_key, msg: bytes):
        dst_ip, dst_port = connection_key
        if self.verbose:
            print(
                f"[TLSServer] Sending TLS message {msg[:30]}... to {dst_ip}:{dst_port}"
            )
            print(
                f"[TLSServer] Current handshake state for {connection_key}: {self.get_state(connection_key)}"
            )
        self.node.send_app_data(
            dst_ip,
            msg,
            protocol="TCP",
            destination_port=dst_port,
        )

    def encrypt(self, connection_key, plaintext: bytes) -> bytes:
        if not self.is_established(connection_key):
            return plaintext
        return b"ENC(" + plaintext + b")"

    def decrypt(self, connection_key, ciphertext: bytes) -> bytes:
        if not self.is_established(connection_key):
            return ciphertext
        if ciphertext.startswith(b"ENC(") and ciphertext.endswith(b")"):
            return ciphertext[4:-1]
        return ciphertext


class HTTPSClient(HTTPClient):
    def __init__(self, node, server_url=None, verbose=False):
        super().__init__(node, server_url=server_url, verbose=verbose)
        self.tls_client = TLSClient(node, verbose=verbose)
        self._https_connection_key = None
        self.request_sent = False
        self.bytes_received = 0
        self.content_length = None
        self.transfer_done = False

    def _initiate_connection(self, server_ip, server_port):
        if self.verbose:
            print(
                "[HTTPSClient] TCP接続を要求しています(HTTPS):", server_ip, server_port
            )
        self.server_ip = server_ip
        self.server_port = server_port
        self.state = "CONNECTING"

        self.node.initiate_tcp_handshake(server_ip, server_port)

        if self.verbose:
            print(
                f"[HTTPSClient] Mapping HTTPS接続 -> {server_ip}:{server_port}"
            )
        self.app_manager.map_connection_to_app(
            (server_ip, server_port), "HTTPS"
        )

    def on_connection_established(self, connection_key):
        self.state = "CONNECTED"
        self._https_connection_key = connection_key
        self.request_sent = False
        self.bytes_received = 0
        self.content_length = None
        self.transfer_done = False
        if self.verbose:
            print(
                "[HTTPSClient] TCP接続が確立しました。TLSハンドシェイクを開始します。"
            )

        self.tls_client.start_handshake(connection_key)

    def on_packet_received(self, packet):
        self.tls_client.on_packet_received(packet)

        connection_key = (packet.header["source_ip"], packet.header["source_port"])
        if self.tls_client.is_established(connection_key):
            if (
                self.file_to_retrieve
                and self.state == "CONNECTED"
                and not self.request_sent
            ):
                request = f"GET /{self.file_to_retrieve} HTTP/1.0\r\n\r\n"
                self.send_http_request(request)
                self.request_sent = True
                if self.verbose:
                    print("[HTTPSClient] HTTPSリクエストを送信しました。")

            decrypted = self.tls_client.decrypt(connection_key, packet.payload)
            if not self.transfer_done:
                if decrypted.startswith(b"HTTP/1.0 200 OK"):
                    if self.content_length is None and b"Content-Length:" in decrypted:
                        header_end = decrypted.find(b"\r\n\r\n")
                        if header_end != -1:
                            headers = decrypted[:header_end].decode(
                                "utf-8", errors="ignore"
                            )
                            for line in headers.split("\r\n"):
                                if line.startswith("Content-Length:"):
                                    self.content_length = int(
                                        line.split(":")[1].strip()
                                    )
                                    if self.verbose:
                                        print(
                                            f"[HTTPSClient] Content-Length: {self.content_length}"
                                        )

                            body = decrypted[header_end + 4 :]
                            self.bytes_received += len(body)
                    else:
                        self.bytes_received += len(decrypted)

                    if (
                        self.content_length is not None
                        and self.bytes_received >= self.content_length
                    ):
                        self.transfer_done = True
                        if self.verbose:
                            print(
                                f"[HTTPSClient] ファイル転送が完了しました。(受信: {self.bytes_received} bytes)"
                            )
                        self.node.terminate_TCP_connection(
                            (connection_key[0], connection_key[1])
                        )
                        if self.verbose:
                            print("[HTTPSClient] TCPコネクションを閉じました。")

                    if self.verbose:
                        print(
                            "[HTTPSClient] (TLS) ファイルの取得に成功しました。進捗: {}/{}".format(
                                self.bytes_received,
                                self.content_length if self.content_length else "不明",
                            )
                        )

                elif decrypted.startswith(b"HTTP/1.0 404"):
                    if self.verbose:
                        print(
                            "[HTTPSClient] (TLS) ファイルが見つかりません:",
                            decrypted.decode("utf-8", errors="ignore"),
                        )
                    self.transfer_done = True
                    self.node.terminate_TCP_connection(connection_key)
                    if self.verbose:
                        print("[HTTPSClient] TCPコネクションを閉じました。")
            return

    def send_https_request(self, request: str):
        if self._https_connection_key is None:
            if self.verbose:
                print("[HTTPSClient] Error: TCP接続がまだ確立されていません。")
            return
        if not self.tls_client.is_established(self._https_connection_key):
            if self.verbose:
                print("[HTTPSClient] Error: TLSハンドシェイクが完了していません。")
            return

        request_bytes = request.encode("utf-8")
        enc_data = self.tls_client.encrypt(self._https_connection_key, request_bytes)
        dst_ip, dst_port = self._https_connection_key
        self.node.send_app_data(
            dst_ip, enc_data, protocol="TCP", destination_port=dst_port
        )


class HTTPSServer(HTTPServer):
    def __init__(self, node, shared_files, verbose=False):
        super().__init__(node, shared_files, verbose=verbose)
        self.tls_server = TLSServer(node, verbose=verbose)
        self.https_outgoing_data = {}

    def on_connection_established(self, connection_key):
        if self.verbose:
            print(
                "[HTTPSServer] TCP接続を受け付けました。TLSハンドシェイクを開始します。"
            )
        super().on_connection_established(connection_key)

        self.tls_server.accept_handshake(connection_key)

    def on_packet_received(self, packet):
        self.tls_server.on_packet_received(packet)

        connection_key = (packet.header["source_ip"], packet.header["source_port"])
        if not self.tls_server.is_established(connection_key):
            if self.verbose:
                print(
                    "[HTTPSServer] TLSハンドシェイク中です。状態:",
                    self.tls_server.get_state(connection_key),
                )
            return

        decrypted = self.tls_server.decrypt(connection_key, packet.payload)
        if self.verbose and decrypted:
            print(f"[HTTPSServer] (TLS) 復号されたHTTPリクエスト: {decrypted[:60]} ...")

        fake_packet = self._create_fake_http_packet(packet, decrypted)
        super().on_packet_received(fake_packet)

    def get_data_chunk(self, connection_key, payload_size):
        data = self.https_outgoing_data.get(connection_key, b"")
        chunk = data[:payload_size]
        return chunk

    def update_data_after_send(self, connection_key, sent_bytes):
        data = self.https_outgoing_data.get(connection_key, b"")
        self.https_outgoing_data[connection_key] = data[sent_bytes:]

    def _create_fake_http_packet(self, original_packet, new_payload):
        from copy import deepcopy

        new_packet = deepcopy(original_packet)
        new_packet.payload = new_payload
        return new_packet

    def send_http_response(self, client_ip, client_port, server_port, response):
        connection_key = (client_ip, client_port)
        if not self.tls_server.is_established(connection_key):
            super().send_http_response(client_ip, client_port, server_port, response)
            return

        if isinstance(response, str):
            response_bytes = response.encode("utf-8")
        else:
            response_bytes = response

        enc_data = self.tls_server.encrypt(connection_key, response_bytes)
        if self.verbose:
            print(f"[HTTPSServer] (TLS) 暗号化されたレスポンスを送信: {len(enc_data)} バイト")
        self.node.send_app_data(
            client_ip,
            enc_data,
            protocol="TCP",
            source_port=server_port,
            destination_port=client_port,
        )
