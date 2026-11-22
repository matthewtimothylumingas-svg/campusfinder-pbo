# CampusFinder - Sistem Informasi Barang Hilang & Ditemukan Kampus

Aplikasi web untuk melaporkan dan mencari barang hilang atau ditemukan di area kampus.
Proyek Mata Kuliah Pemrograman Berorientasi Objek (PBO).

**Live demo:** https://campusfinder.pythonanywhere.com

## Fitur
- Registrasi, login, dan logout (password terenkripsi)
- Dua peran: **admin** dan **user**
- Lapor barang hilang/ditemukan lengkap dengan foto, tanggal, dan nomor WhatsApp
- Pencarian dan filter berdasarkan kategori dan status
- Halaman detail dengan tombol hubungi pelapor (WhatsApp)
- Tandai laporan "Selesai" dan hapus laporan (pemilik laporan atau admin)
- **Panel Admin** (`/admin`, khusus role admin): statistik pengguna dan laporan, kelola pengguna (ubah role user/admin, hapus akun beserta laporannya), dan kelola semua laporan (tandai selesai / hapus)
- Statistik jumlah barang hilang, ditemukan, dan selesai

## Teknologi
Python 3, Flask, SQLite, Bootstrap 5, Font Awesome.
Penerapan OOP: class `Database`, `User`, dan `Barang` pada folder `models/`.

## Akun uji coba
| Role  | Email             | Password |
|-------|-------------------|----------|
| Admin | admin@kampus.com  | admin123 |
| User  | user@kampus.com   | user123  |

## Cara instalasi lokal
1. Pastikan Python 3 sudah terpasang.
2. Pasang dependensi: `pip install -r requirements.txt`
3. Jalankan aplikasi: `python app.py` (di Windows bisa `py app.py`)
4. Buka `http://127.0.0.1:5000`

Database (`barang_hilang.db`) dan akun uji coba dibuat otomatis saat aplikasi pertama kali dijalankan.

## Struktur proyek
```
app.py            -> route dan logika aplikasi
models/           -> class Database, User, Barang
templates/        -> halaman HTML (Jinja2)
static/uploads/   -> foto yang diunggah
```
