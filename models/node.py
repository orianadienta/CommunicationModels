import queue
import time
from collections import defaultdict
from models.message import Message

# BASE NODE
class Node:
    def __init__(self, name: str, node_type: str):
        self.name      = name
        self.node_type = node_type
        self.inbox     = queue.Queue()
        self.sent      = 0
        self.received  = 0
        self.active    = True

    def send(self, msg: Message):
        self.sent += 1

    def receive(self, msg: Message):
        self.inbox.put(msg)
        self.received += 1

# REQUEST-RESPONSE 

class ClientNode(Node):
    # Membuat request dan melacak latency saat response tiba
    def __init__(self, name: str):
        super().__init__(name, "client")
        self.pending_requests: dict = {}   # msg_id → timestamp

    def make_request(self, content: str) -> Message:
        # Membuat pesan request baru
        msg = Message("request", self.name, "Server", content)
        self.pending_requests[msg.id] = msg.timestamp
        self.send(msg)
        return msg

    def receive_response(self, msg: Message) -> Message:
        # Terima response dan hitung latency round-trip
        self.receive(msg)
        if msg.id in self.pending_requests:
            msg.latency = (time.time() - self.pending_requests[msg.id]) * 1000
            del self.pending_requests[msg.id]
        return msg


class ServerNode(Node):
    # Menerima request dan mengembalikan response yang sesuai
    RESPONSES = {
        "GET /data"  : "200 OK: {users:[A,B,C], count:3}",
        "POST /login": "200 OK: token=abc123xyz",
        "DELETE /item": "204 No Content",
        "GET /status": "200 OK: {status:running, uptime:99.9%}",
        "PUT /update": "200 OK: record updated",
    }

    def __init__(self, name: str):
        super().__init__(name, "server")
        self.processed = 0

    def handle_request(self, req_msg: Message) -> Message:
        # Proses request dan buat pesan response
        self.receive(req_msg)
        self.processed += 1
        content = self.RESPONSES.get(
            req_msg.content,
            f"200 OK: processed '{req_msg.content}'"
        )
        res_msg = Message("response", self.name, req_msg.source, content)
        res_msg.id = req_msg.id   # gunakan ID yang sama untuk tracking latency
        self.send(res_msg)
        return res_msg


# PUBLISH-SUBSCRIBE 

class MessageBroker(Node):
    # Broker untuk mengelola daftar langganan (subscriptions) dan meneruskan pesan dari publisher ke subscriber yang relevan
    def __init__(self):
        super().__init__("Broker", "broker")
        self.subscriptions: dict = defaultdict(list)   # topic:subscriber names
        self.message_count: dict = defaultdict(int)    # topic: jumlah pesan

    def subscribe(self, subscriber_name: str, topic: str):
        # Daftarkan subscriber ke topik tertentu
        if subscriber_name not in self.subscriptions[topic]:
            self.subscriptions[topic].append(subscriber_name)

    def unsubscribe(self, subscriber_name: str, topic: str):
        # Batalkan langganan subscriber dari topik tertentu
        if subscriber_name in self.subscriptions[topic]:
            self.subscriptions[topic].remove(subscriber_name)

    def route(self, pub_msg: Message) -> list:
        # Terima pesan dari publisher dan kembalikan daftar nama subscriber yang perlu menerima pesan ini
        self.receive(pub_msg)
        self.message_count[pub_msg.topic] += 1
        return list(self.subscriptions.get(pub_msg.topic, []))


class PublisherNode(Node):
    # Menerbitkan pesan ke topik tertentu melalui broker.
    def __init__(self, name: str):
        super().__init__(name, "publisher")

    def publish(self, topic: str, content: str) -> Message:
        # Buat pesan publish dengan topik yang tersedia
        msg = Message("publish", self.name, "Broker", content, topic=topic)
        self.send(msg)
        return msg


class SubscriberNode(Node):
    # Berlangganan ke topik tertentu dan menerima pesan dari broker.
    def __init__(self, name: str):
        super().__init__(name, "subscriber")
        self.subscribed_topics: list = []

    def subscribe_to(self, topic: str, broker: MessageBroker):
        # Mendaftar ke topik
        if topic not in self.subscribed_topics:
            self.subscribed_topics.append(topic)
            broker.subscribe(self.name, topic)

    def unsubscribe_from(self, topic: str, broker: MessageBroker):
        # Batalkan langganan dari topik dari broker
        if topic in self.subscribed_topics:
            self.subscribed_topics.remove(topic)
            broker.unsubscribe(self.name, topic)

    def receive_publication(self, msg: Message):
        # Terima pesan yang dari broker
        self.receive(msg)
