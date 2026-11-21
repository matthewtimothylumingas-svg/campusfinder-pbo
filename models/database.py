import os
import sqlite3
from datetime import datetime

from werkzeug.security import generate_password_hash

# Lokasi file database (otomatis dibuat di folder proyek)
LOKASI_DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "barang_hilang.db")

# Agar kolom tanggal otomatis menjadi objek tanggal Python (dipakai di template)
sqlite3.register_converter("TIMESTAMP", lambda b: datetime.strptime(b.decode(), "%Y-%m-%d %H:%M:%S"))
sqlite3.register_converter("DATE", lambda b: datetime.strptime(b.decode(), "%Y-%m-%d").date())


class Database:
    """Class untuk koneksi dan eksekusi query SQLite."""

    def __init__(self):
        self.lokasi = LOKASI_DB
        self._buat_tabel()

    def connect(self):
        try:
            koneksi = sqlite3.connect(self.lokasi, detect_types=sqlite3.PARSE_DECLTYPES)
            koneksi.row_factory = sqlite3.Row
            return koneksi
        except sqlite3.Error as e:
            print(f"Koneksi database gagal: {e}")
            return None

    def _buat_tabel(self):
        """Membuat tabel otomatis kalau belum ada, lalu mengisi akun demo."""
        koneksi = self.connect()
        if not koneksi:
            return
        try:
            koneksi.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user'
                );
                CREATE TABLE IF NOT EXISTS barang (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama_barang TEXT NOT NULL,
                    kategori TEXT NOT NULL,
                    deskripsi TEXT,
                    lokasi TEXT,
                    tanggal_kejadian DATE,
                    foto TEXT,
                    kontak TEXT,
                    status TEXT NOT NULL DEFAULT 'Aktif',
                    user_id INTEGER NOT NULL,
                    tanggal TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
            """)
            # Akun demo (hanya dibuat kalau tabel users masih kosong)
            if koneksi.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
                koneksi.executemany(
                    "INSERT INTO users (nama, email, password, role) VALUES (?, ?, ?, ?)",
                    [("Admin Demo", "admin@kampus.com", generate_password_hash("admin123"), "admin"),
                     ("User Demo", "user@kampus.com", generate_password_hash("user123"), "user")])
            koneksi.commit()
        finally:
            koneksi.close()

    def jalankan(self, query, params=(), mode="none"):
        """
        Helper agar kode di model tidak berulang.
        mode: 'none' -> INSERT/UPDATE/DELETE (return True/False)
              'one'  -> ambil 1 baris (dict)
              'all'  -> ambil semua baris (list of dict)
        """
        gagal = False if mode == "none" else ([] if mode == "all" else None)
        koneksi = self.connect()
        if not koneksi:
            return gagal
        try:
            hasil = koneksi.execute(query.replace("%s", "?"), params)
            if mode == "one":
                baris = hasil.fetchone()
                return dict(baris) if baris else None
            if mode == "all":
                return [dict(b) for b in hasil.fetchall()]
            koneksi.commit()
            return True
        except Exception as e:
            print(f"Error query: {e}")
            return gagal
        finally:
            koneksi.close()
