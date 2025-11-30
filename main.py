from flask import Flask, redirect, url_for
from config import Config, get_config

# Import blueprints
from routes.auth import auth_bp
from routes.pages import pages_bp
from routes.products import products_bp
from routes.cart import cart_bp
from routes.checkout import checkout_bp

def create_app(config_name=None):
    """
    Application factory untuk membuat instance Flask app.
    """
    app = Flask(__name__)
    
    if config_name:
        from config import config
        app.config.from_object(config[config_name])
    else:
        app.config.from_object(get_config())
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(checkout_bp)
    
    @app.route('/')
    def index():
        """Halaman utama - redirect ke halaman login"""
        return redirect(url_for('auth.login_page'))
    
    # ✅ PERBAIKAN: Error handlers tanpa flash messages berlebihan
    @app.errorhandler(404)
    def page_not_found(error):
        """Handler untuk error 404"""
        from flask import session
        if 'user_name' in session:
            return redirect(url_for('pages.home_page'))
        else:
            return redirect(url_for('auth.login_page'))
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handler untuk error 500"""
        from flask import session
        if 'user_name' in session:
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
