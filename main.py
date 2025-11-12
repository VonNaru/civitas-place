from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, render_template_string, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json

# === INISIALISASI APLIKASI FLASK ===
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'dev-secret'  # Kunci rahasia untuk session dan flash message

# === KONFIGURASI FILE DATA USER ===
JSON_FILE = 'user.json'  # File untuk menyimpan data user yang terdaftar

# === FUNGSI UNTUK MENGELOLA DATA USER ===

def load_users_from_file(path=JSON_FILE):
    """
    Fungsi untuk memuat data user dari file JSON
    Returns: Dictionary berisi data semua user yang terdaftar
    """
    try:
        # Cek apakah file JSON ada
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Pastikan data yang dibaca adalah dictionary
                if isinstance(data, dict):
                    return data
    except Exception as e:
        print(f"Gagal memuat data user dari {path}: {e}")
    
    # Jika file tidak ada atau error, kembalikan dictionary kosong
    return {}

def save_users_to_file(users_dict, path=JSON_FILE):
    """
    Fungsi untuk menyimpan data user ke file JSON
    Args:
        users_dict: Dictionary berisi data user
        path: Lokasi file untuk menyimpan data
    """
    try:
        # Buat direktori jika belum ada
        dirpath = os.path.dirname(path)
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)
        
        # Simpan ke file temporary dulu untuk keamanan
        tmp_path = path + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(users_dict, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        
        # Pindahkan file temporary ke file asli (atomic operation)
        os.replace(tmp_path, path)
        
    except Exception as e:
        print(f"Gagal menyimpan data user ke {path}: {e}")

# === LOAD DATA USER SAAT APLIKASI DIMULAI ===
users = load_users_from_file()

# === ROUTE UTAMA ===

@app.route('/')
def index():
    """
    Halaman utama - redirect ke halaman login
    """
    return redirect('/Login.html')

# =========================
# === SISTEM AUTENTIKASI ===
# =========================

@app.route('/login', methods=['POST'])
def login():
    """
    Proses login user dengan validasi email dan password.
    Menggunakan session untuk menyimpan data user yang berhasil login.
    
    Fitur:
    - Validasi input email dan password
    - Pengecekan kredensial dengan database user
    - Session management untuk user yang login
    - Flash message untuk feedback ke user
    """
    # Ambil data dari form login
    form = request.form
    email = form.get('email', '').strip()
    password = form.get('password', '').strip()
    
    # Validasi: pastikan email dan password tidak kosong
    if not email or not password:
        session['login_form'] = {'email': email}  # Simpan email untuk ditampilkan kembali
        flash('Email dan password harus diisi')
        return redirect(url_for('login_page'))
    
    # Cari user berdasarkan email
    user = users.get(email)
    
    # Validasi: cek apakah user ada dan password benar
    if not user or not check_password_hash(user['password_hash'], password):
        session['login_form'] = {'email': email}  # Simpan email untuk ditampilkan kembali
        flash('Email atau password salah')
        return redirect(url_for('login_page'))

    # Login berhasil - simpan data user ke session
    session['user_id'] = email
    session['user_name'] = user.get('full_name', 'User')
    
    # Tampilkan pesan selamat datang yang dipersonalisasi
    flash(f'Selamat datang, {user.get("full_name", "User")}!')
    
    # Redirect ke halaman utama
    return redirect('/Home_pages.html')

@app.route('/register', methods=['POST'])
def register():
    """
    Proses registrasi user baru dengan validasi ketat.
    
    Fitur validasi:
    - Nama minimal 3 karakter
    - Email harus valid (mengandung @ dan .)
    - Password minimal 6 karakter
    - Email tidak boleh duplikat
    - Password di-hash untuk keamanan
    """
    # Ambil data dari form registrasi
    form = request.form
    name = form.get('name', '').strip()
    email = form.get('email', '').strip()
    password = form.get('password', '').strip()
    
    # List untuk menyimpan pesan error
    errors = []
    
    # Validasi nama
    if not name:
        errors.append('Nama lengkap harus diisi.')
    elif len(name) < 3:
        errors.append('Nama lengkap minimal 3 karakter.')
    
    # Validasi email
    if not email:
        errors.append('Email harus diisi.')
    elif '@' not in email or '.' not in email:
        errors.append('Format email tidak valid.')
    
    # Validasi password
    if not password:
        errors.append('Password harus diisi.')
    elif len(password) < 6:
        errors.append('Password minimal 6 karakter.')

    # Jika ada error, tampilkan dan kembali ke form
    if errors:
        session['register_form'] = {'name': name, 'email': email}  # Simpan data untuk ditampilkan kembali
        for error in errors:
            flash(error)
        return redirect(url_for('register_page'))

    # Cek apakah email sudah terdaftar
    if email in users:
        session['register_form'] = {'name': name, 'email': email}
        flash('Email sudah terdaftar. Silakan gunakan email lain.')
        return redirect(url_for('register_page'))

    # Hash password untuk keamanan (tidak menyimpan password plain text)
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    
    # Simpan user baru ke database
    users[email] = {
        "username": email,
        "password_hash": hashed_password,
        "full_name": name
    }
    
    # Simpan perubahan ke file JSON
    save_users_to_file(users)
    
    # Berikan feedback sukses dan redirect ke login
    flash('Registrasi berhasil! Silakan login dengan akun Anda.')
    return redirect('/Login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    Proses logout user.
    
    Fitur:
    - Menghapus semua data session user
    - Redirect ke halaman login
    - Flash message konfirmasi logout
    """
    session.clear()  # Hapus semua data session
    flash('Anda berhasil logout.')
    return redirect('/Login.html')

# =========================
# === SISTEM KERANJANG ====
# =========================

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    """
    Menambahkan produk ke keranjang belanja.
    
    Fitur:
    - Validasi data produk yang dikirim
    - Update quantity jika produk sudah ada di keranjang
    - Tambah produk baru jika belum ada
    - Simpan ke session untuk persistensi
    """
    # Ambil data produk dari form
    product_id = request.form.get('product_id')
    name = request.form.get('name')
    price = request.form.get('price')
    quantity = int(request.form.get('quantity', 1))
    
    # Validasi data produk
    if not product_id or not name or not price:
        flash('Data produk tidak lengkap.')
        return redirect(request.referrer or url_for('home_page'))
    
    # Ambil data keranjang dari session (default list kosong)
    cart = session.get('cart', [])
    
    # Cek apakah produk sudah ada di keranjang
    for item in cart:
        if item['product_id'] == product_id:
            # Jika sudah ada, tambahkan quantity
            item['quantity'] += quantity
            break
    else:
        # Jika belum ada, tambahkan produk baru ke keranjang
        cart.append({
            'product_id': product_id,
            'name': name,
            'price': int(price),
            'quantity': quantity
        })
    
    # Simpan keranjang yang sudah diupdate ke session
    session['cart'] = cart
    
    # Berikan feedback dan redirect ke halaman keranjang
    flash('Produk berhasil ditambahkan ke keranjang!')
    return redirect(url_for('cart_page'))

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    """
    Menghapus produk dari keranjang belanja.
    """
    product_id = request.form.get('product_id')
    
    # Ambil keranjang dan hapus produk berdasarkan product_id
    cart = session.get('cart', [])
    cart = [item for item in cart if item['product_id'] != product_id]
    
    # Simpan keranjang yang sudah diupdate
    session['cart'] = cart
    
    flash('Produk berhasil dihapus dari keranjang.')
    return redirect(url_for('cart_page'))

@app.route('/Cart.html')
def cart_page():
    """
    Halaman keranjang belanja.
    
    Fitur:
    - Menampilkan semua item di keranjang
    - Menghitung total harga (harga × quantity untuk setiap item)
    """
    cart = session.get('cart', [])
    
    # Hitung total harga: jumlah dari (harga × quantity) untuk setiap item
    total = sum(item['price'] * item['quantity'] for item in cart)
    
    return render_template('Cart.html', cart=cart, total=total)

# =========================
# === HALAMAN STATIS ======
# =========================

@app.route('/Login.html')
def login_page():
    """
    Halaman login dengan form data yang preserved jika ada error.
    """
    form_data = session.pop('login_form', {})  # Ambil dan hapus data form dari session
    return render_template('Login.html', form_data=form_data)

@app.route('/Register.html')
def register_page():
    """
    Halaman registrasi dengan form data yang preserved jika ada error.
    """
    form_data = session.pop('register_form', {})  # Ambil dan hapus data form dari session
    return render_template('Register.html', form_data=form_data)

@app.route('/Home_pages.html')
def home_page():
    """
    Halaman utama marketplace yang menampilkan daftar produk.
    """
    return render_template('Home_pages.html')

@app.route('/Dasboard.html')
def dashboard_page():
    """
    Halaman dashboard user (untuk melihat profil, riwayat, dll).
    """
    return render_template('Dasboard.html')

# =========================
# === HALAMAN DETAIL PRODUK
# =========================

@app.route('/barang/Barang1.html')
def barang1_page():
    """
    Halaman detail untuk Produk Keren 1.
    Menghitung jumlah item di keranjang untuk ditampilkan di navbar.
    """
    cart = session.get('cart', [])
    cart_count = len(cart)  # Hitung jumlah jenis produk di keranjang
    return render_template('barang/Barang1.html', cart_count=cart_count)

@app.route('/barang/barang2.html')
def barang2_page():
    """
    Halaman detail untuk Sepatu Lari Cepat.
    """
    cart = session.get('cart', [])
    cart_count = len(cart)
    return render_template('barang/barang2.html', cart_count=cart_count)

@app.route('/barang/barang3.html')
def barang3_page():
    """
    Halaman detail untuk Headphone Super Bass.
    """
    cart = session.get('cart', [])
    cart_count = len(cart)
    return render_template('barang/barang3.html', cart_count=cart_count)

@app.route('/barang/barang4.html')
def barang4_page():
    """
    Halaman detail untuk Laptop Gaming.
    """
    cart = session.get('cart', [])
    cart_count = len(cart)
    return render_template('barang/barang4.html', cart_count=cart_count)

# === MENJALANKAN APLIKASI ===
if __name__ == '__main__':
    """
    Menjalankan aplikasi Flask dalam mode development.
    Debug=True memungkinkan auto-reload saat kode diubah dan menampilkan error detail.
    """
    app.run(debug=True)
