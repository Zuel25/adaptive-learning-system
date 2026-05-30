# Sistem Pembelajaran Adaptif Numerasi

Sistem pembelajaran online yang menggunakan AI untuk menyesuaikan materi pembelajaran berdasarkan kemampuan siswa.

## 🎯 Fitur Utama

- ✅ Login Siswa & Guru
- ✅ Pre-test Numerasi Otomatis
- ✅ Pengelompokan Kemampuan (Dasar, Menengah, Mahir)
- ✅ Materi Pembelajaran Adaptif
- ✅ Latihan Interaktif dengan Feedback AI
- ✅ Dashboard Guru untuk Monitoring
- ✅ Tracking Perkembangan Real-time

## 🚀 Cara Menjalankan

### Frontend
```bash
# Buka folder frontend dan jalankan server lokal
cd frontend
# Gunakan Live Server atau buka index.html di browser
```

### Backend
```bash
# Install dependencies
pip install -r requirements.txt

# Jalankan server
python app.py
```

Server akan berjalan di `http://localhost:5000`

## 📁 Struktur Project

```
adaptive-learning-system/
├── frontend/
│   ├── index.html          # Halaman login
│   ├── student/
│   │   ├── pretest.html    # Halaman pre-test
│   │   ├── learning.html   # Halaman pembelajaran
│   │   └── practice.html   # Halaman latihan
│   ├── teacher/
│   │   └── dashboard.html  # Dashboard guru
│   ├── css/
│   │   └── style.css       # Styling
│   └── js/
│       ├── app.js          # Main app logic
│       ├── api.js          # API integration
│       └── utils.js        # Utility functions
├── backend/
│   ├── app.py              # Flask server
│   ├── database.py         # Database operations
│   ├── ai_model.py         # AI/ML logic
│   └── requirements.txt    # Dependencies
└── README.md
```

## 🔐 Login Default

**Siswa:**
- Email: tajulaziz110@gmail.com

**Guru:**
- Email: tajulgimang@gmail.com

## 📝 Teknologi

- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Backend:** Python Flask
- **Database:** SQLite
- **AI/Adaptif:** Logika algoritma berbasis rule

---

