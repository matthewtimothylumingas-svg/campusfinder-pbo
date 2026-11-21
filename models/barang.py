from models.database import Database


class Barang:
    """Class Barang untuk mengelola laporan barang hilang / ditemukan."""

    def __init__(self):
        self.db = Database()

    def tambah_laporan(self, nama_barang, kategori, deskripsi, lokasi,
                       tanggal_kejadian, foto, kontak, user_id):
        query = """INSERT INTO barang
                   (nama_barang, kategori, deskripsi, lokasi, tanggal_kejadian, foto, kontak, user_id)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        return self.db.jalankan(query, (nama_barang, kategori, deskripsi, lokasi,
                                        tanggal_kejadian, foto, kontak, user_id))

    def ambil_semua_laporan(self, keyword=None, kategori=None, status=None):
        query = """SELECT barang.*, users.nama AS pelapor
                   FROM barang JOIN users ON barang.user_id = users.id WHERE 1=1"""
        params = []
        if keyword:
            query += " AND (nama_barang LIKE %s OR deskripsi LIKE %s OR lokasi LIKE %s)"
            params += [f"%{keyword}%"] * 3
        if kategori:
            query += " AND kategori = %s"
            params.append(kategori)
        if status:
            query += " AND status = %s"
            params.append(status)
        query += " ORDER BY barang.tanggal DESC"
        return self.db.jalankan(query, tuple(params), "all")

    def ambil_by_id(self, id_barang):
        query = """SELECT barang.*, users.nama AS pelapor
                   FROM barang JOIN users ON barang.user_id = users.id
                   WHERE barang.id = %s"""
        return self.db.jalankan(query, (id_barang,), "one")

    def ubah_status(self, id_barang, status):
        return self.db.jalankan("UPDATE barang SET status = %s WHERE id = %s",
                                (status, id_barang))

    def hapus(self, id_barang):
        return self.db.jalankan("DELETE FROM barang WHERE id = %s", (id_barang,))

    def statistik(self):
        query = """SELECT COUNT(*) AS total,
                          COALESCE(SUM(kategori='Hilang' AND status='Aktif'), 0) AS hilang,
                          COALESCE(SUM(kategori='Ditemukan' AND status='Aktif'), 0) AS ditemukan,
                          COALESCE(SUM(status='Selesai'), 0) AS selesai
                   FROM barang"""
        hasil = self.db.jalankan(query, (), "one")
        return hasil or {"total": 0, "hilang": 0, "ditemukan": 0, "selesai": 0}

    def ambil_foto_by_user(self, id_user):
        """Nama file foto milik satu user (untuk dibersihkan saat user dihapus)."""
        hasil = self.db.jalankan("SELECT foto FROM barang WHERE user_id = %s AND foto IS NOT NULL",
                                 (id_user,), "all")
        return [h["foto"] for h in hasil]

    def hapus_by_user(self, id_user):
        return self.db.jalankan("DELETE FROM barang WHERE user_id = %s", (id_user,))
