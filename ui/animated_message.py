import tkinter as tk


class AnimatedMessage:
    # partikel pesan yang bergerak dari satu node ke node lain di atas canvas
    def __init__(self, canvas: tk.Canvas,
                 x1: float, y1: float,
                 x2: float, y2: float,
                 color: str, label: str,
                 on_arrive=None):
        self.canvas    = canvas
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.color     = color
        self.label     = label
        self.on_arrive = on_arrive
        self.progress  = 0.0
        self.speed     = 0.03
        self.active    = True
        self.trails    = []   # list of (canvas_id, life)

        # Gambar lingkaran partikel
        self.circle = canvas.create_oval(
            x1 - 8, y1 - 8, x1 + 8, y1 + 8,
            fill=color, outline="#FFFFFF", width=1.5
        )
        # Label di atas partikel
        self.text = canvas.create_text(
            x1, y1 - 16, text=label,
            fill=color, font=("Courier", 7, "bold")
        )

    def update(self) -> bool:
        # Perbarui posisi partikel satu langkah animasi. Terbalik True jika animasi masih berjalan, False jika sudah selesai
        if not self.active:
            return False

        self.progress = min(1.0, self.progress + self.speed)

        # Easing: ease-in-out (smooth start & end)
        t = self.progress
        ease = t * t * (3 - 2 * t)
        x = self.x1 + (self.x2 - self.x1) * ease
        y = self.y1 + (self.y2 - self.y1) * ease

        # Pindahkan partikel dan label
        self.canvas.coords(self.circle, x - 8, y - 8, x + 8, y + 8)
        self.canvas.coords(self.text, x, y - 16)

        # Tambahkan trail baru jika belum penuh
        if len(self.trails) < 5:
            trail_id = self.canvas.create_oval(
                x - 4, y - 4, x + 4, y + 4,
                fill=self.color, outline="", stipple="gray50"
            )
            self.trails.append((trail_id, 5))

        # Update dan hapus trail yang sudah habis
        new_trails = []
        for (tid, life) in self.trails:
            life -= 1
            if life > 0:
                stipple = "gray25" if life < 3 else "gray50"
                self.canvas.itemconfig(tid, stipple=stipple)
                new_trails.append((tid, life))
            else:
                self.canvas.delete(tid)
        self.trails = new_trails

        # Animasi selesai
        if self.progress >= 1.0:
            self.active = False
            self.canvas.delete(self.circle)
            self.canvas.delete(self.text)
            for (tid, _) in self.trails:
                self.canvas.delete(tid)
            if self.on_arrive:
                self.on_arrive()
            return False

        return True
