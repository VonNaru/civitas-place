from flask import Blueprint, render_template, session
from utils.decorators import login_required
from models.cart import CartManager

# Buat blueprint untuk product routes
products_bp = Blueprint('products', __name__, url_prefix='/barang')

@products_bp.route('/Barang1.html')
@login_required
def barang1_page():
    """
    Halaman detail untuk Produk Keren 1.
    Menghitung jumlah item di keranjang untuk navbar.
    """
    cart_count = CartManager.get_cart_count()
    return render_template('barang/Barang1.html', cart_count=cart_count)

@products_bp.route('/barang2.html')
@login_required
def barang2_page():
    """
    Halaman detail untuk Sepatu Lari Cepat.
    Menghitung jumlah item di keranjang untuk navbar.
    """
    cart_count = CartManager.get_cart_count()
    return render_template('barang/barang2.html', cart_count=cart_count)

@products_bp.route('/barang3.html')
@login_required
def barang3_page():
    """
    Halaman detail untuk Headphone Super Bass.
    Menghitung jumlah item di keranjang untuk navbar.
    """
    cart_count = CartManager.get_cart_count()
    return render_template('barang/barang3.html', cart_count=cart_count)

@products_bp.route('/barang4.html')
@login_required
def barang4_page():
    """
    Halaman detail untuk Laptop Gaming.
    Menghitung jumlah item di keranjang untuk navbar.
    """
    cart_count = CartManager.get_cart_count()
    return render_template('barang/barang4.html', cart_count=cart_count)