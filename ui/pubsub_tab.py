import tkinter as tk
from tkinter import ttk
import math
import random
import time
from collections import defaultdict

from config.theme import C
from models.node import PublisherNode, SubscriberNode, MessageBroker
from ui.animated_message import AnimatedMessage
from ui.log_panel import LogPanel


class PubSubTab(tk.Frame):
    TOPICS = ["#berita", "#cuaca", "#saham", "#olahraga", "#teknologi"]

    PUB_CONTENTS = {
        "#berita"    : ["Breaking: Gempa Bumi M7.2", "Pemilu Selesai", "Bencana Alam"],
        "#cuaca"     : ["Hujan Lebat Hari Ini", "Cerah Berawan", "Suhu 35°C"],
        "#saham"     : ["BBCA naik 2.3%", "IHSG melemah", "IPO baru terdaftar"],
        "#olahraga"  : ["Timnas Menang 3-0", "Turnamen Bulu Tangkis", "Rekor Baru"],
        "#teknologi" : ["AI Model Baru Dirilis", "Chip 3nm Tersedia", "OS Update"],
    }

    def __init__(self, parent, log_panel: LogPanel):
        super().__init__(parent, bg=C["bg"])
        self.log        = log_panel
        self.animations = []
        self.metrics    = {
            "published" : 0,
            "delivered" : 0,
            "topics_used": defaultdict(int),
        }
        self._auto_running = False

        self._build_nodes()
        self._build_canvas()
        self._build_controls()
        self._build_subscription_manager()
        self._build_metrics_bar()
        self._draw_nodes()
        self._animate_loop()

    # Inisialisasi node 

    def _build_nodes(self):
        self.broker      = MessageBroker()
        self.publishers  = [PublisherNode(f"Pub-{chr(65 + i)}") for i in range(2)]
        self.subscribers = [SubscriberNode(f"Sub-{i + 1}") for i in range(4)]

        # Langganan awal
        for sub in self.subscribers[:2]:
            sub.subscribe_to("#berita", self.broker)
            sub.subscribe_to("#cuaca",  self.broker)
        for sub in self.subscribers[2:]:
            sub.subscribe_to("#saham",     self.broker)
            sub.subscribe_to("#teknologi", self.broker)

    def _build_canvas(self):
        self.canvas = tk.Canvas(
            self, bg=C["canvas_bg"],
            highlightthickness=0, height=300
        )
        self.canvas.pack(fill="x", padx=8, pady=8)
        self._draw_grid()

    def _draw_grid(self):
        for x in range(0, 900, 40):
            self.canvas.create_line(x, 0, x, 300, fill=C["border"], width=1)
        for y in range(0, 300, 40):
            self.canvas.create_line(0, y, 900, y, fill=C["border"], width=1)

    def _build_controls(self):
        ctrl = tk.Frame(self, bg=C["panel"])
        ctrl.pack(fill="x", padx=8, pady=(0, 2))

        tk.Label(
            ctrl, text=" CONTROLLER",
            bg=C["panel"], fg=C["accent2"],
            font=("Courier", 10, "bold")
        ).pack(side="left", pady=8)

        tk.Label(ctrl, text="Publisher:", bg=C["panel"],
                 fg=C["text_dim"], font=("Courier", 9)).pack(side="left", padx=(12, 4))
        self.pub_var = tk.StringVar(value="Pub-A")
        ttk.Combobox(
            ctrl, textvariable=self.pub_var,
            values=[p.name for p in self.publishers],
            width=8, state="readonly"
        ).pack(side="left", padx=4)

        tk.Label(ctrl, text="Topik:", bg=C["panel"],
                 fg=C["text_dim"], font=("Courier", 9)).pack(side="left", padx=(12, 4))
        self.topic_var = tk.StringVar(value=self.TOPICS[0])
        ttk.Combobox(
            ctrl, textvariable=self.topic_var,
            values=self.TOPICS, width=14, state="readonly"
        ).pack(side="left", padx=4)

        tk.Button(
            ctrl, text="  PUBLISH  ",
            bg=C["btn2"], fg="white",
            font=("Courier", 9, "bold"),
            relief="flat", cursor="hand2", padx=8,
            command=self._publish
        ).pack(side="left", padx=12)

        self.auto_btn = tk.Button(
            ctrl, text="▶ AUTO",
            bg=C["border"], fg=C["text"],
            font=("Courier", 9),
            relief="flat", cursor="hand2",
            command=self._toggle_auto
        )
        self.auto_btn.pack(side="left", padx=4)

    # Manage subscription

    def _build_subscription_manager(self):
        sub_frame = tk.Frame(self, bg=C["panel"])
        sub_frame.pack(fill="x", padx=8, pady=2)

        tk.Label(sub_frame, text="  Manage Subscription:",
                 bg=C["panel"], fg=C["text_dim"],
                 font=("Courier", 8)).pack(side="left", pady=4)

        self.sub_sel_var = tk.StringVar(value="Sub-1")
        ttk.Combobox(
            sub_frame, textvariable=self.sub_sel_var,
            values=[s.name for s in self.subscribers],
            width=7, state="readonly"
        ).pack(side="left", padx=4)

        self.sub_topic_var = tk.StringVar(value=self.TOPICS[0])
        ttk.Combobox(
            sub_frame, textvariable=self.sub_topic_var,
            values=self.TOPICS, width=14, state="readonly"
        ).pack(side="left", padx=4)

        tk.Button(
            sub_frame, text="+ Subscribe",
            bg=C["border"], fg=C["accent2"],
            font=("Courier", 8), relief="flat", cursor="hand2",
            command=self._subscribe_action
        ).pack(side="left", padx=4)

        tk.Button(
            sub_frame, text="− Unsubscribe",
            bg=C["border"], fg="#F78166",
            font=("Courier", 8), relief="flat", cursor="hand2",
            command=self._unsubscribe_action
        ).pack(side="left", padx=4)

    # Metrik

    def _build_metrics_bar(self):
        bar = tk.Frame(self, bg=C["panel"])
        bar.pack(fill="x", padx=8, pady=2)
        self.metric_labels = {}
        for key, label in [
            ("published", "PESAN DITERBITKAN"),
            ("delivered", "TOTAL DIKIRIM"),
            ("fanout",    "AVG FAN-OUT"),
        ]:
            card = tk.Frame(bar, bg=C["border"])
            card.pack(side="left", padx=4, pady=4, ipadx=12, ipady=6)
            tk.Label(card, text=label, bg=C["border"],
                     fg=C["text_dim"], font=("Courier", 7, "bold")).pack()
            lbl = tk.Label(card, text="0", bg=C["border"],
                           fg=C["accent2"], font=("Courier", 14, "bold"))
            lbl.pack()
            self.metric_labels[key] = lbl

    # Gambar node dan koneksi

    def _draw_nodes(self):
        self.canvas.delete("nodes")
        self.node_positions = {
            "Pub-A" : (80,  100),
            "Pub-B" : (80,  210),
            "Broker": (360, 155),
            "Sub-1" : (620,  55),
            "Sub-2" : (620, 120),
            "Sub-3" : (620, 195),
            "Sub-4" : (620, 260),
        }

        # Garis koneksi latar (putus-putus)
        bx, by = self.node_positions["Broker"]
        for pub in self.publishers:
            px, py = self.node_positions[pub.name]
            self.canvas.create_line(px, py, bx, by,
                                     fill=C["border"], dash=(3, 5), tags="nodes")
        for sub in self.subscribers:
            sx, sy = self.node_positions[sub.name]
            self.canvas.create_line(bx, by, sx, sy,
                                     fill=C["border"], dash=(3, 5), tags="nodes")

        # Publisher nodes
        for name in [p.name for p in self.publishers]:
            x, y = self.node_positions[name]
            self.canvas.create_rectangle(x - 36, y - 20, x + 36, y + 20,
                                          fill=C["node_pub"], outline="#FFFFFF",
                                          width=1.5, tags="nodes")
            self.canvas.create_text(x, y, text=name, fill="white",
                                     font=("Courier", 8, "bold"), tags="nodes")

        # Broker (hexagon)
        self._draw_hexagon(bx, by, 44, C["node_broker"], "Broker")

        # Subscriber nodes
        for name in [s.name for s in self.subscribers]:
            x, y = self.node_positions[name]
            self.canvas.create_rectangle(x - 36, y - 20, x + 36, y + 20,
                                          fill=C["node_sub"], outline="#FFFFFF",
                                          width=1.5, tags="nodes")
            self.canvas.create_text(x, y, text=name, fill="white",
                                     font=("Courier", 8, "bold"), tags="nodes")

        # Label grup
        self.canvas.create_text(80,  30,  text="PUBLISHERS",   fill=C["node_pub"],
                                 font=("Courier", 8, "bold"), tags="nodes")
        self.canvas.create_text(360, 95,  text="BROKER",       fill=C["node_broker"],
                                 font=("Courier", 8, "bold"), tags="nodes")
        self.canvas.create_text(620, 22,  text="SUBSCRIBERS",  fill=C["node_sub"],
                                 font=("Courier", 8, "bold"), tags="nodes")

    def _draw_hexagon(self, cx, cy, r, color, label):
        pts = []
        for i in range(6):
            a = math.pi / 3 * i - math.pi / 6
            pts.extend([cx + r * math.cos(a), cy + r * math.sin(a)])
        self.canvas.create_polygon(pts, fill=color, outline="#FFFFFF",
                                    width=2, tags="nodes")
        self.canvas.create_text(cx, cy, text=label, fill="white",
                                 font=("Courier", 9, "bold"), tags="nodes")

    # Communication logic

    def _publish(self):
        pub_name  = self.pub_var.get()
        topic     = self.topic_var.get()
        publisher = next(p for p in self.publishers if p.name == pub_name)
        content   = random.choice(self.PUB_CONTENTS.get(topic, ["Data baru"]))

        msg = publisher.publish(topic, content)
        self.metrics["published"] += 1
        self.metrics["topics_used"][topic] += 1

        px, py = self.node_positions[pub_name]
        bx, by = self.node_positions["Broker"]
        self.log.log(f"{pub_name} menerbitkan ke {topic}: '{content}'", "pub")

        def on_broker_arrive():
            subscribers = self.broker.route(msg)
            self.log.log(
                f"Broker routing {topic} ke {len(subscribers)} subscriber(s)", "info"
            )
            for i, sub_name in enumerate(subscribers):
                sx, sy = self.node_positions[sub_name]

                def make_delivery(sn, sm):
                    def deliver():
                        anim = AnimatedMessage(
                            self.canvas, bx, by, sx, sy,
                            C["msg_pub"], topic[:4],
                            on_arrive=lambda: self._on_delivered(sn, sm)
                        )
                        self.animations.append(anim)
                    return deliver

                self.after(i * 200, make_delivery(sub_name, msg))
            self._update_metrics()

        anim = AnimatedMessage(
            self.canvas, px, py, bx, by,
            C["msg_pub"], "PUB",
            on_arrive=on_broker_arrive
        )
        self.animations.append(anim)

    def _on_delivered(self, sub_name: str, msg):
        sub = next(s for s in self.subscribers if s.name == sub_name)
        sub.receive_publication(msg)
        self.metrics["delivered"] += 1
        self.log.log(f"✓ {sub_name} menerima '{msg.topic}': {msg.content}", "res")
        self._update_metrics()

    def _subscribe_action(self):
        sub_name = self.sub_sel_var.get()
        topic    = self.sub_topic_var.get()
        sub = next(s for s in self.subscribers if s.name == sub_name)
        sub.subscribe_to(topic, self.broker)
        self.log.log(f"{sub_name} subscribe ke {topic}", "ok")

    def _unsubscribe_action(self):
        sub_name = self.sub_sel_var.get()
        topic    = self.sub_topic_var.get()
        sub = next(s for s in self.subscribers if s.name == sub_name)
        sub.unsubscribe_from(topic, self.broker)
        self.log.log(f"{sub_name} unsubscribe dari {topic}", "err")

    # Metrik dan update

    def _update_metrics(self):
        pub    = self.metrics["published"]
        dlv    = self.metrics["delivered"]
        fanout = f"{dlv / pub:.1f}" if pub > 0 else "0.0"
        self.metric_labels["published"].config(text=str(pub))
        self.metric_labels["delivered"].config(text=str(dlv))
        self.metric_labels["fanout"].config(text=fanout)

    def get_metrics(self) -> dict:
        # mengembalikan ringkasan metrik untuk tab Perbandingan
        pub = self.metrics["published"]
        dlv = self.metrics["delivered"]
        return {
            "model"     : "Publish-Subscribe",
            "total"     : pub,
            "avg_fanout": dlv / pub if pub > 0 else 0,
            "delivered" : dlv,
        }

    # Mode auto
    def _toggle_auto(self):
        self._auto_running = not self._auto_running
        if self._auto_running:
            self.auto_btn.config(text="⏹ STOP", bg=C["btn3"])
            self._auto_publish()
        else:
            self.auto_btn.config(text="▶ AUTO", bg=C["border"])

    def _auto_publish(self):
        if self._auto_running:
            self.pub_var.set(random.choice([p.name for p in self.publishers]))
            self.topic_var.set(random.choice(self.TOPICS))
            self._publish()
            self.after(1800, self._auto_publish)

    # Animasi loop

    def _animate_loop(self):
        self.animations = [a for a in self.animations if a.update()]
        self.after(30, self._animate_loop)
