from flask import session, flash, redirect, url_for  # Flask utilities untuk session management dan routing
from functools import wraps  # Untuk preserve metadata fungsi asli saat menggunakan decorator

def login_required(f):
    """
    Security decorator untuk melindungi route yang memerlukan autentikasi.
    
    Fungsi decorator ini akan:
    1. Mengecek apakah user sudah login (ada 'user_id' di session)
    2. Jika belum login: redirect ke halaman login dengan pesan error
    3. Jika sudah login: lanjutkan eksekusi fungsi route yang diminta
    
    Usage:
        @app.route('/protected-page')
        @login_required
        def protected_page():
            return "Halaman ini hanya untuk user yang sudah login"
    
    Args:
        f (function): Fungsi route yang akan dilindungi
        
    Returns:
        function: Decorated function dengan proteksi login
        
    Security Features:
        - Session-based authentication check
        - Automatic redirect untuk unauthorized access
        - User-friendly flash message
        - Centralized access control
    """
    
    @wraps(f)  # Preserve metadata fungsi asli (nama, docstring, dll)
    def decorated_function(*args, **kwargs):
        """
        Wrapper function yang melakukan pengecekan autentikasi.
        
        Flow Logic:
        1. Cek session untuk 'user_id'
        2. Jika tidak ada -> user belum login -> redirect ke login
        3. Jika ada -> user sudah login -> lanjut ke fungsi asli
        """
        
        # === SECURITY CHECK ===
        # Cek apakah user sudah login dengan mengecek keberadaan 'user_id' di session
        if 'user_id' not in session:
            
            # === UNAUTHORIZED ACCESS HANDLING ===
            # Berikan feedback kepada user mengapa akses ditolak
            flash('Anda harus login terlebih dahulu untuk mengakses halaman ini.')
            
            # Redirect ke halaman login menggunakan blueprint routing
            # 'auth.login_page' merujuk ke login_page() function di auth blueprint
            return redirect(url_for('auth.login_page'))
        
        # === AUTHORIZED ACCESS ===
        # Jika user sudah login, lanjutkan eksekusi fungsi route asli
        # *args, **kwargs memungkinkan fungsi menerima parameter apapun
        return f(*args, **kwargs)
    
    # Return decorated function untuk digunakan sebagai route handler
    return decorated_function

# === PENGGUNAAN DECORATOR INI ===
"""
Decorator ini digunakan di routes yang memerlukan login, contoh:

Di routes/pages.py:
    @pages_bp.route('/Home_pages.html')
    @login_required  # ← Proteksi applied di sini
    def home_page():
        return render_template('Home_pages.html')

Di routes/cart.py:
    @cart_bp.route('/Cart.html')
    @login_required  # ← Keranjang hanya untuk user login
    def cart_page():
        return render_template('Cart.html')

Keuntungan:
- ✅ Reusable: Bisa dipakai di banyak routes
- ✅ Centralized: Logic security di satu tempat
- ✅ Maintainable: Mudah update jika ada perubahan
- ✅ Consistent: Semua protected routes punya behavior sama
"""