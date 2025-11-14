from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.decorators import login_required
from models.cart import CartManager

# Buat blueprint untuk cart routes
cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    """
    Menambahkan produk ke keranjang belanja.
    """
    # Ambil data produk dari form
    product_id = request.form.get('product_id')
    name = request.form.get('name')
    price = request.form.get('price')
    quantity = int(request.form.get('quantity', 1))
    
    # Validasi data produk
    if not product_id or not name or not price:
        flash('Data produk tidak lengkap.')
        return redirect(request.referrer or url_for('pages.home_page'))
    
    # Tambahkan ke keranjang
    CartManager.add_to_cart(product_id, name, price, quantity)
    
    # Berikan feedback dan redirect ke halaman keranjang
    flash('Produk berhasil ditambahkan ke keranjang!')
    return redirect(url_for('cart.cart_page'))

@cart_bp.route('/remove_from_cart', methods=['POST'])
@login_required
def remove_from_cart():
    """
    Menghapus produk dari keranjang belanja.
    """
    product_id = request.form.get('product_id')
    
    # Hapus dari keranjang
    CartManager.remove_from_cart(product_id)
    
    flash('Produk berhasil dihapus dari keranjang.')
    return redirect(url_for('cart.cart_page'))

@cart_bp.route('/clear_cart', methods=['POST'])
@login_required
def clear_cart():
    """
    Mengosongkan seluruh keranjang belanja.
    """
    CartManager.clear_cart()
    flash('Keranjang berhasil dikosongkan.')
    return redirect(url_for('cart.cart_page'))

@cart_bp.route('/Cart.html')
@login_required
def cart_page():
    """
    Halaman keranjang belanja.
    Menampilkan semua item di keranjang dan menghitung total harga.
    """
    cart = CartManager.get_cart()
    cart_count = CartManager.get_cart_count()
    total = CartManager.get_cart_total()
    
    return render_template('Cart.html', cart=cart, cart_count=cart_count, total=total)