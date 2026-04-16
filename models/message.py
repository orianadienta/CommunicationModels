import time
import itertools

class Message:
    _counter = itertools.count(1)

    def __init__(self, msg_type: str, source: str, destination: str,
                 content: str, topic: str = None):
        self.id          = next(Message._counter)
        self.msg_type    = msg_type
        self.source      = source
        self.destination = destination
        self.content     = content
        self.topic       = topic
        self.timestamp   = time.time()
        self.latency     = None

    def __str__(self) -> str:
        t = time.strftime("%H:%M:%S", time.localtime(self.timestamp))
        return (f"[{t}] MSG#{self.id} {self.msg_type.upper()} "
                f"{self.source}→{self.destination}: {self.content}")
