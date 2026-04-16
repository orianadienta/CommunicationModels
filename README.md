1. DESKRIPSI PROYEK
   Proyek ini adalah simulator interaktif model komunikasi sistem terdistribusi berbasis Python dan Tkinter. Simulator ini memvisualisasikan dua model komunikasi utama secara animatif dan real-time, sehingga pengguna dapat mengamati, berinteraksi, serta membandingkan perilaku masing-masing model secara langsung.
   Tujuan Utama
    • Mendemonstrasikan cara kerja model Request-Response dan Publish-Subscribe
    • Memvisualisasikan aliran pesan antar node dengan animasi partikel bergerak
    • Menyediakan mekanisme perbandingan metrik antar model secara live
    • Memberikan antarmuka interaktif untuk eksperimen komunikasi terdistribusi
2. STRUKTUR PROYEK
   CommunicationModels/
│
├── main.py
├── app.py
│
├── config/
│   └── theme.py
│
├── models/
│   ├── message.py
│   └── node.py
│
└── ui/
    ├── animated_message.py
    ├── log_panel.py
    ├── request_response_tab.py
    ├── pubsub_tab.py
    └── comparison_tab.py
4. CARA MENJALANKAN PROGRAM
