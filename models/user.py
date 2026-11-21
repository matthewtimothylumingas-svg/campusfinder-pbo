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
