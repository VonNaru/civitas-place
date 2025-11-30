from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import UserManager

# Buat blueprint untuk authentication routes
auth_bp = Blueprint('auth', __name__)

# Initialize user manager
user_manager = UserManager()

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Proses login user dengan validasi email dan password.
    """
    # Ambil data dari form login
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    
    # Validasi: pastikan email dan password tidak kosong
    if not email or not password:
        session['login_form'] = {'email': email}
        flash('Email dan password harus diisi')
        return redirect(url_for('auth.login_page'))
    
    # Autentikasi user
    success, user = user_manager.authenticate_user(email, password)
    if not success:
        session['login_form'] = {'email': email}
        flash('Email atau password salah')
        return redirect(url_for('auth.login_page'))
    
    # Login berhasil - simpan data user ke session
    session['user_id'] = email
    session['user_name'] = user.get('full_name', 'User')
    session['user_email'] = email  # ← TAMBAHAN: Simpan email untuk checkout
    
    # Tampilkan pesan selamat datang
    flash(f'Selamat datang, {user.get("full_name", "User")}!')
    
    # Redirect ke halaman utama
    return redirect(url_for('pages.home_page'))

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Proses registrasi user baru dengan validasi ketat.
    """
    # Ambil data dari form registrasi
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    
    # Validasi input
    errors = []
    if not name or len(name) < 3:
        errors.append('Nama lengkap minimal 3 karakter.')
    if not email or '@' not in email or '.' not in email:
        errors.append('Format email tidak valid.')
    if not password or len(password) < 6:
        errors.append('Password minimal 6 karakter.')
    
    # Jika ada error, tampilkan dan kembali ke form
    if errors:
        session['register_form'] = {'name': name, 'email': email}
        for error in errors:
            flash(error)
        return redirect(url_for('auth.register_page'))
    
    # Buat user baru
    success, message = user_manager.create_user(email, password, name)
    if not success:
        session['register_form'] = {'name': name, 'email': email}
        flash(message)
        return redirect(url_for('auth.register_page'))
    
    # Registrasi berhasil
    flash('Registrasi berhasil! Silakan login dengan akun Anda.')
    return redirect(url_for('auth.login_page'))

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    Proses logout user - menghapus data user tapi pertahankan keranjang.
    """
    # Simpan keranjang sebelum clear session
    cart_backup = session.get('cart', [])
    
    # Hapus semua session
    session.clear()
    
    # Restore keranjang setelah logout
    session['cart'] = cart_backup
    
    flash('Anda berhasil logout.')
    return redirect(url_for('auth.login_page'))

@auth_bp.route('/Login.html')
def login_page():
    """
    Halaman login dengan form data yang preserved jika ada error.
    """
    form_data = session.pop('login_form', {})
    return render_template('Login.html', form_data=form_data)

@auth_bp.route('/Register.html')
def register_page():
    """
    Halaman registrasi dengan form data yang preserved jika ada error.
    """
    form_data = session.pop('register_form', {})
    return render_template('Register.html', form_data=form_data)