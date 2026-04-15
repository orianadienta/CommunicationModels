import tkinter as tk
import time
from ..config.theme import C

class LogPanel(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=C["log_bg"], **kwargs)
        header = tk.Label(self, text="  SYSTEM LOG", bg=C["log_bg"],
                          fg=C["text_dim"], font=("Courier", 9, "bold"), anchor="w")
        header.pack(fill="x", pady=(4,0))
        self.text = tk.Text(self, bg=C["log_bg"], fg=C["text"], font=("Courier", 8),
                            state="disabled", wrap="word", relief="flat",
                            insertbackground=C["text"], selectbackground=C["border"])
        self.text.pack(fill="both", expand=True, padx=4, pady=4)
        
        # Tag warna
        self.text.tag_config("req", foreground=C["msg_req"])
        self.text.tag_config("res", foreground=C["msg_res"])
        self.text.tag_config("pub", foreground=C["msg_pub"])
        self.text.tag_config("info", foreground=C["text_dim"])
        self.text.tag_config("ok", foreground=C["accent2"])
        self.text.tag_config("err", foreground=C["accent1"])

    def log(self, text, tag="info"):
        self.text.config(state="normal")
        ts = time.strftime("%H:%M:%S")
        self.text.insert("end", f"[{ts}] {text}\n", tag)
        self.text.see("end")
        self.text.config(state="disabled")

    def clear(self):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.config(state="disabled")