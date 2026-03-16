class Node:
    def __init__(self, node_id, address=None):
        self.node_id = node_id
        self.address = address
        self.links = []

    def add_link(self, link):
        if link not in self.links:
            self.links.append(link)


    def __str__(self):
        connected_nodes = [link.node_x.node_id if self != link.node_x else link.node_y.node_id for link in self.links]
        connected_nodes_str = ','.join(map(str, connected_nodes))
        return f"ノード（ID:{self.node_id}, アドレス:{self.address}）, 接続:{connected_nodes_str}"

class Link:
    def __init__(self, node_x, node_y, bandwidth=10000, delay=0.001, packet_loss=0.0):
        self.node_x = node_x
        self.node_y = node_y
        self.bandwidth = bandwidth
        self.delay = delay
        self.packet_loss = packet_loss

        node_x.add_link(self)
        node_y.add_link(self)

    def __str__(self):
        return f"リンク（{self.node_x.node_id} <-> {self.node_y.node_id}, 帯域幅:{self.bandwidth}, 遅延:{self.delay}, パケットロス率:{self.packet_loss}）"

class Packet:
    def __init__(self, source, destination, payload)
        self.source = source
        self.destination = destination
        self.palyload = payload

    def __str__(self):
        return f"パケット（送信元:{self.source}, 宛先:{self.destination},ペイロード:{self.payload}）"

node1 = Node(node_id=1, address="00:01")
node2 = Node(node_id=2, address="00:02")
link = Link(node1, node2)

print(node1)
print(node2)
print(link)
