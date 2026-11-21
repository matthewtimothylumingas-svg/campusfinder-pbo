import os
import uuid
import webbrowser
from datetime import date
from functools import wraps
from threading import Timer

from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, abort)
from werkzeug.utils import secure_filename

from models.user import User
from models.barang import Barang

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'kunci_rahasia_pbo_ganti_saat_deploy')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # maks 5 MB
EKSTENSI_BOLEH = {'png', 'jpg', 'jpeg', 'webp'}

# Pastikan static/uploads berupa FOLDER (bukan file). Dibuat otomatis jika belum ada.
folder_upload = app.config['UPLOAD_FOLDER']
if os.path.isfile(folder_upload):  # kalau salah buat sebagai file, hapus dulu
    os.remove(folder_upload)
os.makedirs(folder_upload, exist_ok=True)

user_model = User()
barang_model = Barang()


# ---------- Helper ----------
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper


def simpan_foto(file):
    """Simpan foto upload dengan nama unik, return nama file (atau None)."""
    if not file or file.filename == '':
        return None
    ekstensi = file.filename.rsplit('.', 1)[-1].lower()
    if ekstensi not in EKSTENSI_BOLEH:
        return None
    nama_file = f"{uuid.uuid4().hex}.{ekstensi}"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(nama_file)))
    return nama_file


def boleh_kelola(laporan):
    """Hanya pemilik laporan atau admin yang boleh mengubah/menghapus."""
    return laporan['user_id'] == session.get('user_id') or session.get('role') == 'admin'


# ---------- Halaman publik ----------
@app.route('/')
def index():
    stat = barang_model.statistik()
    terbaru = barang_model.ambil_semua_laporan(status='Aktif')[:3]
    return render_template('index.html', stat=stat, terbaru=terbaru)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nama = request.form['nama'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        if len(password) < 6:
            flash('Password minimal 6 karakter.', 'danger')
        elif user_model.register(nama, email, password):
            flash('Registrasi berhasil, silakan login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Registrasi gagal, email mungkin sudah terdaftar.', 'danger')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = user_model.login(request.form['email'].strip(), request.form['password'])
        if user:
            session['user_id'] = user['id']
            session['nama'] = user['nama']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        flash('Email atau password salah.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Kamu sudah logout.', 'success')
    return redirect(url_for('login'))


# ---------- Halaman setelah login ----------
@app.route('/dashboard')
@login_required
def dashboard():
    keyword = request.args.get('q', '').strip()
    kategori = request.args.get('kategori', '')
    status = request.args.get('status', '')
    laporan = barang_model.ambil_semua_laporan(keyword, kategori, status)
    return render_template('dashboard.html', laporan=laporan,
                           stat=barang_model.statistik(),
                           q=keyword, kategori=kategori, status=status)


@app.route('/lapor', methods=['GET', 'POST'])
@login_required
def lapor():
    if request.method == 'POST':
        foto = simpan_foto(request.files.get('foto'))
        sukses = barang_model.tambah_laporan(
            request.form['nama_barang'].strip(),
            request.form['kategori'],
            request.form['deskripsi'].strip(),
            request.form['lokasi'].strip(),
            request.form['tanggal_kejadian'] or None,
            foto,
            request.form['kontak'].strip(),
            session['user_id'],
        )
        flash('Laporan berhasil dikirim!' if sukses else 'Gagal menyimpan laporan.',
              'success' if sukses else 'danger')
        return redirect(url_for('dashboard'))
    return render_template('form_laporan.html', hari_ini=date.today().isoformat())


@app.route('/barang/<int:id_barang>')
@login_required
def detail(id_barang):
    laporan = barang_model.ambil_by_id(id_barang)
    if not laporan:
        abort(404)
    return render_template('detail.html', b=laporan, bisa_kelola=boleh_kelola(laporan))


@app.route('/barang/<int:id_barang>/selesai', methods=['POST'])
@login_required
def selesai(id_barang):
    laporan = barang_model.ambil_by_id(id_barang)
    if not laporan or not boleh_kelola(laporan):
        abort(403)
    barang_model.ubah_status(id_barang, 'Selesai')
    flash('Laporan ditandai selesai.', 'success')
    return redirect(url_for('detail', id_barang=id_barang))


@app.route('/barang/<int:id_barang>/hapus', methods=['POST'])
@login_required
def hapus(id_barang):
    laporan = barang_model.ambil_by_id(id_barang)
    if not laporan or not boleh_kelola(laporan):
        abort(403)
    barang_model.hapus(id_barang)
    flash('Laporan dihapus.', 'success')
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    def open_browser():
        webbrowser.open('http://127.0.0.1:5000/')

    # use_reloader=False agar browser tidak terbuka dua kali
    Timer(1, open_browser).start()
    app.run(debug=True, use_reloader=False)
