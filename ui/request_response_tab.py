import tkinter as tk
from tkinter import ttk
import math
import random
import time

from config.theme import C
from models.node import ClientNode, ServerNode
from ui.animated_message import AnimatedMessage
from ui.log_panel import LogPanel


class RequestResponseTab(tk.Frame):
    REQUESTS = [
        "GET /data",
        "POST /login",
        "DELETE /item",
        "GET /status",
        "PUT /update",
    ]

    def __init__(self, parent, log_panel: LogPanel):
        super().__init__(parent, bg=C["bg"])
        self.log        = log_panel
        self.animations = []
        self.metrics    = {
            "total"            : 0,
            "latencies"        : [],
            "throughput_times" : [],
        }
        self._auto_running = False

        self._build_nodes()
        self._build_canvas()
        self._build_controls()
        self._build_metrics_bar()
        self._draw_nodes()
        self._animate_loop()

    # Inisialisasi node
    def _build_nodes(self):
        self.clients = [ClientNode(f"Client-{chr(65 + i)}") for i in range(3)]
        self.server  = ServerNode("Server")

    # canvas
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
        ctrl.pack(fill="x", padx=8, pady=(0, 4))

        tk.Label(
            ctrl, text=" CONTROLLER",
            bg=C["panel"], fg=C["accent1"],
            font=("Courier", 10, "bold")
        ).pack(side="left", pady=8)

        # Pilihan client
        tk.Label(ctrl, text="Client:", bg=C["panel"],
                 fg=C["text_dim"], font=("Courier", 9)).pack(side="left", padx=(16, 4))
        self.client_var = tk.StringVar(value="Client-A")
        ttk.Combobox(
            ctrl, textvariable=self.client_var,
            values=[c.name for c in self.clients],
            width=10, state="readonly"
        ).pack(side="left", padx=4)

        # Pilihan jenis request
        tk.Label(ctrl, text="Request:", bg=C["panel"],
                 fg=C["text_dim"], font=("Courier", 9)).pack(side="left", padx=(12, 4))
        self.req_var = tk.StringVar(value=self.REQUESTS[0])
        ttk.Combobox(
            ctrl, textvariable=self.req_var,
            values=self.REQUESTS, width=16, state="readonly"
        ).pack(side="left", padx=4)

        # Tombol kirim
        tk.Button(
            ctrl, text="  SEND REQUEST  ",
            bg=C["btn1"], fg="white",
            font=("Courier", 9, "bold"),
            relief="flat", cursor="hand2", padx=8,
            command=self._send_request
        ).pack(side="left", padx=12)

        # Tombol AUTO
        self.auto_btn = tk.Button(
            ctrl, text="▶ AUTO",
            bg=C["border"], fg=C["text"],
            font=("Courier", 9),
            relief="flat", cursor="hand2",
            command=self._toggle_auto
        )
        self.auto_btn.pack(side="left", padx=4)

    # Metriks

    def _build_metrics_bar(self):
        bar = tk.Frame(self, bg=C["panel"])
        bar.pack(fill="x", padx=8, pady=2)
        self.metric_labels = {}
        for key, label in [
            ("total",      "TOTAL REQUESTS"),
            ("avg_lat",    "AVG LATENCY (ms)"),
            ("throughput", "THROUGHPUT (msg/s)"),
        ]:
            card = tk.Frame(bar, bg=C["border"])
            card.pack(side="left", padx=4, pady=4, ipadx=12, ipady=6)
            tk.Label(card, text=label, bg=C["border"],
                     fg=C["text_dim"], font=("Courier", 7, "bold")).pack()
            lbl = tk.Label(card, text="0", bg=C["border"],
                           fg=C["accent1"], font=("Courier", 14, "bold"))
            lbl.pack()
            self.metric_labels[key] = lbl

    # Gamabar node pesan

    def _draw_nodes(self):
        self.canvas.delete("nodes")
        self.node_positions = {
            "Client-A": (120, 75),
            "Client-B": (120, 150),
            "Client-C": (120, 225),
            "Server"  : (520, 150),
        }
        # Client nodes (persegi panjang)
        for name in ["Client-A", "Client-B", "Client-C"]:
            x, y = self.node_positions[name]
            self.canvas.create_rectangle(
                x - 40, y - 22, x + 40, y + 22,
                fill=C["node_client"], outline="#FFFFFF",
                width=1.5, tags="nodes"
            )
            self.canvas.create_text(x, y, text=name, fill="white",
                                     font=("Courier", 9, "bold"), tags="nodes")

        # Server node (hexagon)
        sx, sy = self.node_positions["Server"]
        self._draw_hexagon(sx, sy, 42, C["node_server"], "Server", tags="nodes")

        # Label grup
        self.canvas.create_text(120, 30, text="CLIENTS",
                                 fill=C["node_client"],
                                 font=("Courier", 8, "bold"), tags="nodes")
        self.canvas.create_text(520, 95, text="SERVER",
                                 fill=C["node_server"],
                                 font=("Courier", 8, "bold"), tags="nodes")

        # Legend warna pesan
        self.canvas.create_rectangle(620, 60, 640, 75, fill=C["msg_req"], outline="")
        self.canvas.create_text(645, 67, text="REQUEST",
                                 fill=C["msg_req"], anchor="w", font=("Courier", 8))
        self.canvas.create_rectangle(620, 82, 640, 97, fill=C["msg_res"], outline="")
        self.canvas.create_text(645, 89, text="RESPONSE",
                                 fill=C["msg_res"], anchor="w", font=("Courier", 8))

    def _draw_hexagon(self, cx, cy, r, color, label, tags=""):
        pts = []
        for i in range(6):
            a = math.pi / 3 * i - math.pi / 6
            pts.extend([cx + r * math.cos(a), cy + r * math.sin(a)])
        self.canvas.create_polygon(pts, fill=color, outline="#FFFFFF",
                                    width=2, tags=tags)
        self.canvas.create_text(cx, cy, text=label, fill="white",
                                 font=("Courier", 9, "bold"), tags=tags)

    # Logic
    def _send_request(self):
        client_name = self.client_var.get()
        req_content = self.req_var.get()
        client = next(c for c in self.clients if c.name == client_name)
        msg = client.make_request(req_content)

        self.metrics["total"] += 1
        self.metrics["throughput_times"].append(time.time())

        cx, cy = self.node_positions[client_name]
        sx, sy = self.node_positions["Server"]

        self.log.log(f"➜ {client_name} mengirim REQUEST: '{req_content}'", "req")

        def on_request_arrive():
            res_msg = self.server.handle_request(msg)
            self.log.log("⚡ Server memproses → mengirim RESPONSE", "info")
            anim_res = AnimatedMessage(
                self.canvas, sx, sy, cx, cy,
                C["msg_res"], "RES",
                on_arrive=lambda: self._on_response_arrive(client, res_msg)
            )
            self.animations.append(anim_res)

        anim_req = AnimatedMessage(
            self.canvas, cx, cy, sx, sy,
            C["msg_req"], "REQ",
            on_arrive=on_request_arrive
        )
        self.animations.append(anim_req)

    def _on_response_arrive(self, client: ClientNode, msg):
        client.receive_response(msg)
        latency = msg.latency if msg.latency else random.uniform(10, 80)
        self.metrics["latencies"].append(latency)
        self.log.log(
            f"✓ {client.name} menerima RESPONSE (latency: {latency:.1f} ms)", "res"
        )
        self._update_metrics()

    # Metriks dan update

    def _update_metrics(self):
        total = self.metrics["total"]
        lats  = self.metrics["latencies"]
        times = self.metrics["throughput_times"]

        avg_lat = f"{sum(lats) / len(lats):.1f}" if lats else "0"
        now     = time.time()
        recent  = [t for t in times if now - t < 10]
        tput    = f"{len(recent) / 10:.2f}" if recent else "0.00"

        self.metric_labels["total"].config(text=str(total))
        self.metric_labels["avg_lat"].config(text=avg_lat)
        self.metric_labels["throughput"].config(text=tput)

    def get_metrics(self) -> dict:
        lats  = self.metrics["latencies"]
        times = self.metrics["throughput_times"]
        now   = time.time()
        recent = [t for t in times if now - t < 10]
        return {
            "model"      : "Request-Response",
            "total"      : self.metrics["total"],
            "avg_latency": sum(lats) / len(lats) if lats else 0,
            "throughput" : len(recent) / 10 if recent else 0,
        }

    # MOde auto
    def _toggle_auto(self):
        self._auto_running = not self._auto_running
        if self._auto_running:
            self.auto_btn.config(text="⏹ STOP", bg=C["btn3"])
            self._auto_send()
        else:
            self.auto_btn.config(text="▶ AUTO", bg=C["border"])

    def _auto_send(self):
        if self._auto_running:
            self.client_var.set(random.choice([c.name for c in self.clients]))
            self.req_var.set(random.choice(self.REQUESTS))
            self._send_request()
            self.after(1500, self._auto_send)

    # Animasi loop
    def _animate_loop(self):
        self.animations = [a for a in self.animations if a.update()]
        self.after(30, self._animate_loop)
