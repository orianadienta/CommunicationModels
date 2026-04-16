# Simulasi Model Komunikasi Sistem Terdistribusi
# Deskripsi
   Proyek ini adalah simulator interaktif model komunikasi sistem terdistribusi berbasis Python dan Tkinter. Simulator ini memvisualisasikan dua model komunikasi utama secara animatif dan real time, sehingga pengguna dapat mengamati, berinteraksi, serta membandingkan perilaku masing-masing model secara langsung.
## Tujuan Utama
- Mendemonstrasikan model **Request-Response** dan **Publish-Subscribe**
- Memvisualisasikan aliran pesan antar node
- Menyediakan perbandingan metrik secara live
- Memberikan UI interaktif untuk eksperimen sistem terdistribusi
# Struktur Program

```
CommunicationModels/
├── main.py
├── app.py
├── config/
│   └── theme.py
├── models/
│   ├── message.py
│   └── node.py
└── ui/
    ├── animated_message.py
    ├── log_panel.py
    ├── request_response_tab.py
    ├── pubsub_tab.py
    └── comparison_tab.py
```

## Penjelasan Struktur

| File / Folder | Tipe | Deskripsi |
|---|---|---|
| `main.py` | Entry Point | Menjalankan aplikasi |
| `app.py` | App Layer | Window utama + notebook tab |
| `config/theme.py` | Config | Warna & tema visual |
| `models/message.py` | Model | Data class Message |
| `models/node.py` | Model | Implementasi node sistem |
| `ui/animated_message.py` | UI | Animasi partikel pesan |
| `ui/log_panel.py` | UI | Panel log real-time |
| `ui/request_response_tab.py` | UI | Simulasi Request-Response |
| `ui/pubsub_tab.py` | UI | Simulasi Publish-Subscribe |
| `ui/comparison_tab.py` | UI | Tab perbandingan metrik |

---

# Cara Menjalankan Program
## Persyaratan
- Python **3.8+** (disarankan 3.10+)
## Instalasi & Run
### Clone repo
```bash
git clone https://github.com/orianadienta/CommunicationModels.git
cd CommunicationModels
```
### Jalankan Program
```bash
python main.py
```
# Komponen Sistem Terdistribusi

| Komponen | Model | Peran |
|---|---|---|
| Client A/B/C | Request-Response | Mengirim HTTP request |
| Server | Request-Response | Memproses & mengirim response |
| Publisher A/B | Publish-Subscribe | Menerbitkan pesan |
| Broker | Publish-Subscribe | Routing pesan |
| Subscriber 1-4 | Publish-Subscribe | Menerima pesan |

---

# Model Komunikasi

## 1. Request-Response
Model sinkron klasik di mana client mengirim request dan menunggu response dari server. Setiap request memiliki pasangan response yang unik. Alur komunikasi:
- Client kirim request ke server
- Server memproses dan membalas response
- Menghasilkan latency (ms)

## 2. Publish-Subscribe
Model asinkron berbasis topik di mana publisher tidak mengetahui identitas subscriber. Broker bertindak sebagai perantara yang mengelola routing pesan. Alur komunikasi:
- Publisher mengirim ke broker
- Broker mendistribusikan ke subscriber
- Menghasilkan fan-out

---

# Metrik Sistem

| Metrik | Request-Response | Publish-Subscribe |
|---|---|---|
| Total | Request masuk | Pesan publish |
| Kinerja | Latency (ms) | Fan-out |
| Throughput | pesan/detik | distribusi pesan |

---

# Panduan Interaksi
## Tab Request-Response
1. Pilih client & request type
2. Klik SEND REQUEST
3. Mode AUTO kirim tiap 1.5 detik
4. Lihat metrik: total pesan, latency, throughput
## Tab Publish-Subscribe
1. Pilih publisher & topik
2. Klik PUBLISH
3. Kelola subscription subscriber
4. Mode AUTO tiap 1.8 detik
5. Lihat metrik fan-out
## Tab Perbandingan
1. Live metrics kedua model
2. Refresh manual / otomatis

# Skenario Pengujian
1. Jalankan AUTO Request-Response
2. Jalankan Publish-Subscribe
3. Bandingkan throughput
4. Tambah subscriber → lihat fan-out naik

---
