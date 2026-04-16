import tkinter as tk
import time

from config.theme import C


class ComparisonTab(tk.Frame):
    # Perbandingan kedua model, menerima referensi ke RequestResponseTab dan PubSubTab
    # untuk membaca metrik secara langsung

    # Data tabel perbandingan karakteristik (statis)
    TABLE_HEADERS = ["Karakteristik", "Request-Response", "Pub-Subscribe"]
    TABLE_COLORS  = [C["text_bright"], C["accent1"], C["accent2"]]
    TABLE_ROWS    = [
        ("Coupling",        "Tightly Coupled",   "Loosely Coupled"),
        ("Skalabilitas",    "Rendah–Menengah",   "Tinggi"),
        ("Latency",         "Rendah (sinkron)",  "Menengah (async)"),
        ("Fault Tolerance", "Rendah",            "Tinggi (via broker)"),
        ("Use Case",        "API, Web, RPC",     "Event system, IoT"),
        ("Urutan Pesan",    "Terjamin",          "Tidak terjamin"),
        ("Fan-out",         "1 : 1",             "1 : N"),
        ("Sinkronisasi",    "Synchronous",       "Asynchronous"),
        ("Komponen Kunci",  "Client + Server",   "Publisher + Broker + Subscriber"),
    ]

    def __init__(self, parent, rr_tab, ps_tab):
        super().__init__(parent, bg=C["bg"])
        self.rr_tab = rr_tab
        self.ps_tab = ps_tab
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        # Judul
        tk.Label(
            self, text="PERBANDINGAN MODEL KOMUNIKASI",
            bg=C["bg"], fg=C["accent4"],
            font=("Courier", 12, "bold")
        ).pack(pady=(16, 4))

        self._build_live_metrics()
        self._build_char_table()

    def _build_live_metrics(self):
        # Kartu metrik live untuk setiap model
        live_frame = tk.Frame(self, bg=C["panel"])
        live_frame.pack(fill="x", padx=12, pady=8, ipady=8)

        tk.Label(
            live_frame, text="  LIVE METRICS",
            bg=C["panel"], fg=C["text_dim"],
            font=("Courier", 9, "bold")
        ).pack(anchor="w", padx=8, pady=(8, 4))

        cards_row = tk.Frame(live_frame, bg=C["panel"])
        cards_row.pack(fill="x", padx=8, pady=4)

        card_defs = [
            ("Request-Response", C["accent1"]),
            ("Pub-Subscribe",    C["accent2"]),
        ]

        self.cards = {}
        for model, color in card_defs:
            card = tk.Frame(cards_row, bg=C["border"])
            card.pack(side="left", expand=True, fill="both",
                      padx=6, pady=4, ipadx=12, ipady=10)

            tk.Label(card, text=model, bg=C["border"], fg=color,
                     font=("Courier", 11, "bold")).pack(pady=(4, 10))

            labels = {}
            for key in ["Total Pesan", "Latency / Fan-out", "Throughput / Delivered"]:
                row = tk.Frame(card, bg=C["border"])
                row.pack(fill="x", pady=2, padx=4)
                tk.Label(row, text=f"{key}:", bg=C["border"],
                         fg=C["text_dim"], font=("Courier", 8),
                         width=22, anchor="w").pack(side="left")
                lbl = tk.Label(row, text="—", bg=C["border"],
                               fg=color, font=("Courier", 9, "bold"))
                lbl.pack(side="left")
                labels[key] = lbl
            self.cards[model] = labels

        # Tombol refresh manual
        tk.Button(
            live_frame, text="↻  REFRESH METRICS",
            bg=C["border"], fg=C["accent4"],
            font=("Courier", 9), relief="flat", cursor="hand2",
            command=self._refresh
        ).pack(pady=8)

    def _build_char_table(self):
        # Tabel perbandingan karakteristik statis
        char_frame = tk.Frame(self, bg=C["panel"])
        char_frame.pack(fill="both", expand=True, padx=12, pady=4)

        tk.Label(
            char_frame, text="  KARAKTERISTIK MODEL",
            bg=C["panel"], fg=C["text_dim"],
            font=("Courier", 9, "bold")
        ).pack(anchor="w", padx=8, pady=(8, 4))

        table = tk.Frame(char_frame, bg=C["panel"])
        table.pack(fill="x", padx=8, pady=4)

        # Header
        for j, (h, c) in enumerate(zip(self.TABLE_HEADERS, self.TABLE_COLORS)):
            tk.Label(
                table, text=h, bg=C["border"], fg=c,
                font=("Courier", 8, "bold"), width=26,
                relief="flat", anchor="center", pady=5
            ).grid(row=0, column=j, padx=1, pady=1, sticky="nsew")

        # Baris data
        row_colors = [C["panel"], C["tab_active"]]
        for i, row_data in enumerate(self.TABLE_ROWS):
            bg = row_colors[i % 2]
            for j, cell in enumerate(row_data):
                fg = self.TABLE_COLORS[j] if j > 0 else C["text"]
                tk.Label(
                    table, text=cell, bg=bg, fg=fg,
                    font=("Courier", 8), width=26,
                    relief="flat", anchor="center", pady=4
                ).grid(row=i + 1, column=j, padx=1, pady=1, sticky="nsew")

    def _refresh(self):
        # Ambil metrik terbaru dari kedua tab dan perbarui kartu
        rr = self.rr_tab.get_metrics()
        ps = self.ps_tab.get_metrics()

        # Hitung throughput RR berdasarkan waktu
        times  = self.rr_tab.metrics.get("throughput_times", [])
        recent = [t for t in times if time.time() - t < 10]
        rr_tput = f"{len(recent) / 10:.2f} msg/s"

        # Update kartu Request-Response
        rr_card = self.cards["Request-Response"]
        rr_card["Total Pesan"].config(text=str(rr["total"]))
        rr_card["Latency / Fan-out"].config(text=f"{rr['avg_latency']:.1f} ms")
        rr_card["Throughput / Delivered"].config(text=rr_tput)

        # Update kartu Pub-Subscribe
        ps_card = self.cards["Pub-Subscribe"]
        ps_card["Total Pesan"].config(text=str(ps["total"]))
        ps_card["Latency / Fan-out"].config(text=f"fan-out: {ps['avg_fanout']:.1f}×")
        ps_card["Throughput / Delivered"].config(text=f"{ps['delivered']} delivered")

        # Jadwalkan refresh otomatis berikutnya
        self.after(2000, self._refresh)
