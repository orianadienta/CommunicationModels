import queue
from collections import defaultdict
from .message import Message

class Node:
    """Node dasar dalam sistem terdistribusi."""
    def __init__(self, name, node_type):
        self.name      = name
        self.node_type = node_type
        self.inbox     = queue.Queue()
        self.sent      = 0
        self.received  = 0
        self.active    = True

    def send(self, msg):
        self.sent += 1

    def receive(self, msg):
        self.inbox.put(msg)
        self.received += 1

# Request-Response Nodes
class ClientNode(Node):
    def __init__(self, name):
        super().__init__(name, "client")
        self.pending_requests = {}

    def make_request(self, content):
        msg = Message("request", self.name, "Server", content)
        self.pending_requests[msg.id] = msg.timestamp
        self.send(msg)
        return msg

    def receive_response(self, msg):
        self.receive(msg)
        if msg.id in self.pending_requests:
            msg.latency = (time.time() - self.pending_requests[msg.id]) * 1000
            del self.pending_requests[msg.id]
        return msg

class ServerNode(Node):
    def __init__(self, name):
        super().__init__(name, "server")
        self.processed = 0

    def handle_request(self, req_msg):
        self.receive(req_msg)
        self.processed += 1
        responses = {
            "GET /data": "200 OK: {users:[A,B,C], count:3}",
            "POST /login": "200 OK: token=abc123xyz",
            "DELETE /item": "204 No Content",
            "GET /status": "200 OK: {status:running, uptime:99.9%}",
            "PUT /update": "200 OK: record updated",
        }
        content = responses.get(req_msg.content, f"200 OK: processed '{req_msg.content}'")
        res_msg = Message("response", self.name, req_msg.source, content)
        res_msg.id = req_msg.id
        self.send(res_msg)
        return res_msg

# Publish-Subscribe Nodes
class MessageBroker(Node):
    def __init__(self):
        super().__init__("Broker", "broker")
        self.subscriptions = defaultdict(list)
        self.message_count = defaultdict(int)

    def subscribe(self, subscriber_name, topic):
        if subscriber_name not in self.subscriptions[topic]:
            self.subscriptions[topic].append(subscriber_name)

    def unsubscribe(self, subscriber_name, topic):
        if subscriber_name in self.subscriptions[topic]:
            self.subscriptions[topic].remove(subscriber_name)

    def route(self, pub_msg):
        self.receive(pub_msg)
        self.message_count[pub_msg.topic] += 1
        return list(self.subscriptions.get(pub_msg.topic, []))

class PublisherNode(Node):
    def __init__(self, name):
        super().__init__(name, "publisher")

    def publish(self, topic, content):
        msg = Message("publish", self.name, "Broker", content, topic=topic)
        self.send(msg)
        return msg

class SubscriberNode(Node):
    def __init__(self, name):
        super().__init__(name, "subscriber")
        self.subscribed_topics = []

    def subscribe_to(self, topic, broker):
        if topic not in self.subscribed_topics:
            self.subscribed_topics.append(topic)
            broker.subscribe(self.name, topic)

    def receive_publication(self, msg):
        self.receive(msg)