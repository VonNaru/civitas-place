from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.decorators import login_required
from models.cart import CartManager
from models.order import OrderManager

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

@cart_bp.route('/Checkout.html')
@login_required
def checkout_page():
    """
    Halaman checkout untuk menyelesaikan pembelian.
    Menampilkan ringkasan order dan form alamat pengiriman.
    """
    cart = CartManager.get_cart()
    cart_count = CartManager.get_cart_count()
    total = CartManager.get_cart_total()
    
    # Redirect ke cart jika keranjang kosong
    if not cart:
        flash('Keranjang Anda kosong. Silakan tambahkan produk terlebih dahulu.')
        return redirect(url_for('cart.cart_page'))
    
    return render_template('Checkout.html', cart=cart, cart_count=cart_count, total=total)

@cart_bp.route('/process_checkout', methods=['POST'])
@login_required
def process_checkout():
    """
    Memproses checkout dan membuat order baru dengan metode pembayaran COD.
    """
    cart = CartManager.get_cart()
    
    # Validasi keranjang tidak kosong
    if not cart:
        flash('Keranjang Anda kosong.')
        return redirect(url_for('cart.cart_page'))
    
    # Ambil data dari form
    shipping_address = request.form.get('shipping_address', '').strip()
    
    # Validasi alamat pengiriman
    if not shipping_address:
        flash('Alamat pengiriman harus diisi.')
        return redirect(url_for('cart.checkout_page'))
    
    # Ambil data user dari session
    user_email = session.get('user_id')
    user_name = session.get('user_name')
    total = CartManager.get_cart_total()
    
    # Buat order baru
    order_manager = OrderManager()
    order_id = order_manager.create_order(
        user_email=user_email,
        user_name=user_name,
        items=cart,
        total=total,
        payment_method='COD',
        shipping_address=shipping_address
    )
    
    # Kosongkan keranjang setelah order dibuat
    CartManager.clear_cart()
    
    # Redirect ke halaman konfirmasi order
    flash('Pesanan berhasil dibuat!')
    return redirect(url_for('cart.order_confirmation', order_id=order_id))

@cart_bp.route('/OrderConfirmation.html/<order_id>')
@login_required
def order_confirmation(order_id):
    """
    Halaman konfirmasi order setelah checkout berhasil.
    Menampilkan detail order yang baru dibuat.
    """
    order_manager = OrderManager()
    order = order_manager.get_order(order_id)
    
    # Redirect jika order tidak ditemukan
    if not order:
        flash('Order tidak ditemukan.')
        return redirect(url_for('pages.home_page'))
    
    # Validasi order adalah milik user yang sedang login
    if order.get('user_email') != session.get('user_id'):
        flash('Anda tidak memiliki akses ke order ini.')
        return redirect(url_for('pages.home_page'))
    
    cart_count = CartManager.get_cart_count()
    return render_template('OrderConfirmation.html', order=order, cart_count=cart_count)