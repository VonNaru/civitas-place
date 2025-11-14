"""
Konfigurasi aplikasi Flask untuk Web Marketplace.
File ini berisi semua pengaturan yang diperlukan untuk menjalankan aplikasi.
"""

import os

class Config:
    """
    Class konfigurasi utama untuk aplikasi Flask.
    Berisi semua pengaturan yang diperlukan seperti secret key, database, dll.
    """
    
    # === FLASK CORE CONFIGURATION ===
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # === DATABASE CONFIGURATION ===
    JSON_FILE = 'user.json'  # File untuk menyimpan data user
    
    # === FLASK SETTINGS ===
    DEBUG = True  # Set ke False di production
    
    # === FOLDER PATHS ===
    STATIC_FOLDER = 'static'
    TEMPLATE_FOLDER = 'templates'
    
    # === SESSION CONFIGURATION ===
    PERMANENT_SESSION_LIFETIME = 3600  # Session berlaku 1 jam (3600 detik)
    SESSION_COOKIE_SECURE = False  # Set ke True jika menggunakan HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Mencegah akses cookie via JavaScript
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    
    # === SECURITY SETTINGS ===
    WTF_CSRF_ENABLED = True  # Enable CSRF protection (jika menggunakan Flask-WTF)
    
    # === APPLICATION SETTINGS ===
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max upload file 16MB
    
    # === CART SETTINGS ===
    MAX_CART_ITEMS = 50  # Maksimal 50 jenis item di keranjang
    MAX_QUANTITY_PER_ITEM = 99  # Maksimal quantity per item
    
    # === PAGINATION SETTINGS ===
    PRODUCTS_PER_PAGE = 12  # Jumlah produk per halaman (untuk pagination)
    
    # === EMAIL SETTINGS (untuk future development) ===
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

class DevelopmentConfig(Config):
    """
    Konfigurasi untuk environment development.
    Inherit dari Config dan override beberapa setting untuk development.
    """
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """
    Konfigurasi untuk environment production.
    Setting yang lebih secure dan optimized untuk production.
    """
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Harus di-set di environment variable
    SESSION_COOKIE_SECURE = True  # Require HTTPS
    
    # Validasi environment variables yang wajib ada di production
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Pastikan SECRET_KEY sudah di-set di production
        if not os.environ.get('SECRET_KEY'):
            raise ValueError('SECRET_KEY environment variable harus di-set di production!')

class TestingConfig(Config):
    """
    Konfigurasi untuk testing/unit tests.
    """
    TESTING = True
    DEBUG = True
    JSON_FILE = 'test_user.json'  # Gunakan file terpisah untuk testing
    WTF_CSRF_ENABLED = False  # Disable CSRF untuk testing

# === CONFIGURATION MAPPING ===
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# === UTILITY FUNCTIONS ===
def get_config():
    """
    Mendapatkan konfigurasi berdasarkan environment variable FLASK_ENV.
    Default ke development jika tidak di-set.
    
    Returns:
        Config class: Kelas konfigurasi yang sesuai
    """
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env, config['default'])