from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.decorators import login_required
from models.cart import CartManager
from models.products import ProductsManager

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
        flash('Data produk tidak lengkap!', 'error')
        return redirect(request.referrer or url_for('pages.home_page'))
    
    # Cek stok
    stock = ProductsManager.get_stock(product_id)
    if stock < quantity:
        flash(f'Stok tidak cukup! Tersisa {stock} item untuk {name}.', 'error')
        return redirect(request.referrer)

    # Kurangi stok lalu tambahkan ke cart
    ok = ProductsManager.change_stock(product_id, -quantity)
    if not ok:
        flash('Gagal mengupdate stok. Silakan coba lagi.', 'error')
        return redirect(request.referrer or url_for('pages.home_page'))

    # Tambahkan ke keranjang
    CartManager.add_to_cart(product_id, name, price, quantity)
    flash(f'✅ {name} berhasil ditambahkan ke keranjang!', 'success')
    return redirect(url_for('cart.cart_page'))  # ← HARUS ke cart_page

@cart_bp.route('/remove_from_cart', methods=['POST'])
@login_required
def remove_from_cart():
    """
    Menghapus produk dari keranjang belanja.
    """
    product_id = request.form.get('product_id')
    
    if not product_id:
        flash('Data produk tidak valid!', 'error')
        return redirect(url_for('cart.cart_page'))
    
    # Restore stok sebelum hapus
    cart = CartManager.get_cart()
    qty = 0
    product_name = "Produk"
    
    for item in cart:
        if item['product_id'] == product_id:
            qty = item.get('quantity', 0)
            product_name = item.get('name', 'Produk')
            break
    
    if qty > 0:
        ProductsManager.change_stock(product_id, qty)
    
    # Hapus dari keranjang
    CartManager.remove_from_cart(product_id)
    flash(f'🗑️ {product_name} berhasil dihapus dari keranjang.', 'success')
    return redirect(url_for('cart.cart_page'))  # ← HARUS ke cart_page

@cart_bp.route('/clear_cart', methods=['POST'])
@login_required
def clear_cart():
    """
    Mengosongkan seluruh keranjang belanja.
    """
    cart = CartManager.get_cart()
    
    if not cart:
        flash('Keranjang sudah kosong!', 'info')
        return redirect(url_for('cart.cart_page'))
    
    # Restore semua stok
    for item in cart:
        ProductsManager.change_stock(item['product_id'], item.get('quantity', 0))
    
    item_count = len(cart)
    CartManager.clear_cart()
    flash(f'🗑️ Berhasil menghapus {item_count} jenis produk dari keranjang!', 'success')
    return redirect(url_for('cart.cart_page'))  # ← HARUS ke cart_page

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
    
    return render_template('Cart.html', 
                         cart=cart, 
                         cart_count=cart_count, 
                         total=total)