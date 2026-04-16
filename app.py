import tkinter as tk
from tkinter import ttk

from config.theme import C
from ui.log_panel             import LogPanel
from ui.request_response_tab  import RequestResponseTab
from ui.pubsub_tab            import PubSubTab
from ui.comparison_tab        import ComparisonTab


class DistributedSimApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulasi Model Komunikasi Sistem Terdistribusi")
        self.geometry("860x720")
        self.minsize(800, 660)
        self.configure(bg=C["bg"])
        self.resizable(True, True)

        self._apply_ttk_style()
        self._build_header()
        self._build_main()

    # Tema
    def _apply_ttk_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # Notebook
        style.configure("TNotebook",
                         background=C["bg"],
                         borderwidth=0,
                         tabmargins=[2, 4, 0, 0])
        style.configure("TNotebook.Tab",
                         background=C["tab_inactive"],
                         foreground=C["text_dim"],
                         font=("Courier", 9, "bold"),
                         padding=[14, 6],
                         borderwidth=0)
        style.map("TNotebook.Tab",
                   background=[("selected", C["tab_active"]),
                                ("active",   C["border"])],
                   foreground=[("selected", C["text_bright"]),
                                ("active",   C["text"])])

        # Combobox
        style.configure("TCombobox",
                         fieldbackground=C["border"],
                         background=C["border"],
                         foreground=C["text"],
                         selectbackground=C["border"],
                         arrowcolor=C["text"],
                         font=("Courier", 9))
        style.map("TCombobox",
                   fieldbackground=[("readonly", C["border"])],
                   foreground=[("readonly",   C["text"])])

    # Header

    def _build_header(self):
        header = tk.Frame(self, bg=C["panel"])
        header.pack(fill="x", side="top")

        # Judul kiri
        title_frame = tk.Frame(header, bg=C["panel"])
        title_frame.pack(side="left", padx=16, pady=10)
        tk.Label(
            title_frame,
            text="◉ DISTRIBUTED COMM SIMULATOR",
            bg=C["panel"], fg=C["accent4"],
            font=("Courier", 13, "bold")
        ).pack(anchor="w")
        tk.Label(
            title_frame,
            text="Request-Response  ·  Publish-Subscribe",
            bg=C["panel"], fg=C["text_dim"],
            font=("Courier", 8)
        ).pack(anchor="w")

    def _build_main(self):
        main = tk.Frame(self, bg=C["bg"])
        main.pack(fill="both", expand=True)

        # Notebook (tabs) di bagian atas
        self.notebook = ttk.Notebook(main)
        self.notebook.pack(fill="both", expand=True, padx=4, pady=(4, 0))

        # Log panel di bagian bawah
        self.log_panel = LogPanel(main, height=140)
        self.log_panel.pack(fill="x", padx=4, pady=(0, 4))

        # Inisialisasi tab
        self.rr_tab  = RequestResponseTab(self.notebook, self.log_panel)
        self.ps_tab  = PubSubTab(self.notebook, self.log_panel)
        self.cmp_tab = ComparisonTab(self.notebook, self.rr_tab, self.ps_tab)

        # Daftarkan tab ke Notebook
        self.notebook.add(self.rr_tab,  text=" Request-Response ")
        self.notebook.add(self.ps_tab,  text=" Pub-Subscribe ")
        self.notebook.add(self.cmp_tab, text=" Perbandingan ")

        # Pesan sambutan di log
        self.log_panel.log("Sistem terdistribusi diinisialisasi.", "ok")
        self.log_panel.log("Pilih tab untuk mulai simulasi model komunikasi.", "info")
        self.log_panel.log(
            "Gunakan tombol SEND REQUEST / PUBLISH / AUTO untuk mengaktifkan pesan.", "info"
        )
