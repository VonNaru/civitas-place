from flask import Flask, redirect, url_for
from config import Config, get_config

# Import blueprints
from routes.auth import auth_bp
from routes.pages import pages_bp
from routes.products import products_bp
from routes.cart import cart_bp

def create_app(config_name=None):
    """
    Application factory untuk membuat instance Flask app.
    Menggunakan pattern ini memudahkan testing dan deployment.
    
    Args:
        config_name (str): Nama konfigurasi ('development', 'production', 'testing')
                          Jika None, akan menggunakan environment variable FLASK_ENV
    
    Returns:
        Flask: Instance aplikasi Flask yang sudah dikonfigurasi
    """
    # Inisialisasi aplikasi Flask
    app = Flask(__name__)
    
    # Load konfigurasi sesuai environment
    if config_name:
        from config import config
        app.config.from_object(config[config_name])
    else:
        # Gunakan konfigurasi otomatis berdasarkan FLASK_ENV
        app.config.from_object(get_config())
    
    # Register blueprints (modular routing)
    app.register_blueprint(auth_bp)        # Routes untuk authentication
    app.register_blueprint(pages_bp)       # Routes untuk halaman statis
    app.register_blueprint(products_bp)    # Routes untuk halaman produk
    app.register_blueprint(cart_bp)        # Routes untuk keranjang
    
    # Route utama - redirect ke halaman login
    @app.route('/')
    def index():
        """Halaman utama - redirect ke halaman login"""
        return redirect(url_for('auth.login_page'))
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(error):
        """Handler untuk error 404 (halaman tidak ditemukan)"""
        from flask import session, flash
        flash('Halaman yang Anda cari tidak ditemukan.')
        if 'user_id' in session:
            return redirect(url_for('pages.home_page'))
        else:
            return redirect(url_for('auth.login_page'))
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handler untuk error 500 (server error)"""
        from flask import session, flash
        flash('Terjadi kesalahan server. Silakan coba lagi.')
        if 'user_id' in session:
            return redirect(url_for('pages.home_page'))
        else:
            return redirect(url_for('auth.login_page'))
    
    return app

# Entry point aplikasi
if __name__ == '__main__':
    """
    Menjalankan aplikasi Flask dalam mode development.
    Bisa dijalankan dengan:
    - python main.py (development mode)
    - FLASK_ENV=production python main.py (production mode)
    """
    app = create_app()
    
    # Jalankan server development
    app.run(
        debug=app.config.get('DEBUG', True),
        host='0.0.0.0',  # Allow external connections
        port=5000
    )
