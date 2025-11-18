from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.decorators import login_required
from models.cart import CartManager
from models.products import ProductsManager

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
    products = ProductsManager.get_all()
    return render_template('Home_pages.html', cart_count=cart_count, products=products)

@pages_bp.route('/Dasboard.html')
@login_required
def dashboard_page():
    """
    Halaman dashboard user (untuk melihat profil, riwayat, dll).
    Menghitung jumlah item di keranjang untuk navbar.
    """
    cart_count = CartManager.get_cart_count()
    products = ProductsManager.get_all()
    return render_template('Dasboard.html', cart_count=cart_count, products=products)

@pages_bp.route('/update_stock', methods=['POST'])
@login_required
def update_stock():
    product_id = request.form.get('product_id')
    try:
        new_stock = int(request.form.get('stock', 0))
    except ValueError:
        flash('Nilai stock tidak valid')
        return redirect(url_for('pages.dashboard_page'))
    ok = ProductsManager.set_stock(product_id, new_stock)
    flash('Stok berhasil diperbarui' if ok else 'Gagal memperbarui stok')
    return redirect(url_for('pages.dashboard_page'))