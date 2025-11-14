from flask import Blueprint, render_template, session
from utils.decorators import login_required
from models.cart import CartManager

# Buat blueprint untuk page routes
pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/Home_pages.html')
@login_required
def home_page():
    """
    Halaman utama marketplace yang menampilkan daftar produk.
    Menghitung jumlah item di keranjang untuk navbar.
    """
    cart_count = CartManager.get_cart_count()
    return render_template('Home_pages.html', cart_count=cart_count)

@pages_bp.route('/Dasboard.html')
@login_required
def dashboard_page():
    """
    Halaman dashboard user (untuk melihat profil, riwayat, dll).
    Menghitung jumlah item di keranjang untuk navbar.
    """
    cart_count = CartManager.get_cart_count()
    return render_template('Dasboard.html', cart_count=cart_count)