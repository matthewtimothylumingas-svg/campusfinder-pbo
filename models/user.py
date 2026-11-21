from werkzeug.security import generate_password_hash, check_password_hash
from models.database import Database


class User:
    """Class User untuk mengelola data pengguna (Registrasi & Login)."""

    def __init__(self):
        self.db = Database()

    def register(self, nama, email, password, role="user"):
        hashed = generate_password_hash(password)  # password disimpan terenkripsi
        query = "INSERT INTO users (nama, email, password, role) VALUES (%s, %s, %s, %s)"
        return self.db.jalankan(query, (nama, email, hashed, role))

    def login(self, email, password):
        user = self.db.jalankan("SELECT * FROM users WHERE email = %s", (email,), "one")
        if not user:
            return None
        tersimpan = user["password"]
        # Akun lama (password teks biasa) tetap bisa login
        if tersimpan == password or check_password_hash(tersimpan, password):
            return user
        return None

    # ---------- Fitur admin ----------
    def ambil_semua(self):
        """Daftar semua user beserta jumlah laporan masing-masing."""
        query = """SELECT users.id, users.nama, users.email, users.role,
                          COUNT(barang.id) AS jumlah_laporan
                   FROM users LEFT JOIN barang ON barang.user_id = users.id
                   GROUP BY users.id ORDER BY users.id"""
        return self.db.jalankan(query, (), "all")

    def ambil_by_id(self, id_user):
        return self.db.jalankan("SELECT id, nama, email, role FROM users WHERE id = %s",
                                (id_user,), "one")

    def ubah_role(self, id_user, role):
        return self.db.jalankan("UPDATE users SET role = %s WHERE id = %s", (role, id_user))

    def hapus(self, id_user):
        return self.db.jalankan("DELETE FROM users WHERE id = %s", (id_user,))

    def hitung(self):
        hasil = self.db.jalankan(
            "SELECT COUNT(*) AS total, COALESCE(SUM(role = 'admin'), 0) AS admin FROM users",
            (), "one")
        return hasil or {"total": 0, "admin": 0}
