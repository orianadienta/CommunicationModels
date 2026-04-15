import time
import itertools

class Message:
    """Representasi sebuah pesan dalam sistem komunikasi."""
    _counter = itertools.count(1)

    def __init__(self, msg_type, source, destination, content, topic=None):
        self.id          = next(Message._counter)
        self.msg_type    = msg_type
        self.source      = source
        self.destination = destination
        self.content     = content
        self.topic       = topic
        self.timestamp   = time.time()
        self.latency     = None

    def __str__(self):
        t = time.strftime("%H:%M:%S", time.localtime(self.timestamp))
        return f"[{t}] MSG#{self.id} {self.msg_type.upper()} {self.source}→{self.destination}: {self.content}"