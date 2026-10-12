# Pilihin — Asisten Belanja Elektronik

Chatbot rekomendasi smartphone, laptop, dan komponen PC (CPU, RAM, kartu grafis) berbasis Gemini dan Streamlit.
Rekomendasi menyesuaikan kategori, budget maksimal, tujuan penggunaan, prioritas, dan preferensi merek yang diisi di panel kiri.

## Menjalankan

```powershell
# 1. Buat virtual environment (Python 3.10+)
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# 2. Atur API key
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
#    lalu isi GEMINI_API_KEY (dapatkan di https://aistudio.google.com/apikey)

# 3. Jalankan
streamlit run app.py
```

## Konfigurasi

Atur di `.streamlit/secrets.toml` atau sebagai environment variable:

| Nama | Default | Keterangan |
|---|---|---|
| `GEMINI_API_KEY` | — | Wajib |
| `GEMINI_MODEL` | `gemini-flash-latest` | Model Gemini yang dipakai |
| `GEMINI_SEARCH` | `true` | Cek harga terkini via Google Search. Jika gagal, otomatis lanjut tanpa pencarian |

## Struktur

| File | Isi |
|---|---|
| `app.py` | UI Streamlit: panel profil, chat, streaming jawaban |
| `catalog.py` | Pilihan tujuan, prioritas, budget, dan contoh pertanyaan per kategori |
| `prompt.py` | System instruction (batasan topik, aturan budget, format jawaban) |
| `gemini_client.py` | Pemanggilan Gemini, streaming, sumber pencarian, pesan error |
| `assets/style.css`, `.streamlit/config.toml` | Tema dan gaya tampilan |
