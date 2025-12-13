from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
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
    # Ambil data produk dari form atau JSON
    product_id = request.form.get('product_id') or request.json.get('product_id')
    quantity = int(request.form.get('quantity', 1) or request.json.get('quantity', 1))
    
    # Ambil data produk dari database
    product = ProductsManager.get(product_id)
    if not product:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Produk tidak ditemukan!'})
        flash('Produk tidak ditemukan!', 'error')
        return redirect(request.referrer or url_for('pages.home_page'))
    
    # Cek stok
    stock = ProductsManager.get_stock(product_id)
    if stock < quantity:
        message = f'Stok tidak cukup! Tersisa {stock} item untuk {product["name"]}.'
        if request.is_json:
            return jsonify({'success': False, 'message': message})
        flash(message, 'error')
        return redirect(request.referrer)

    # Kurangi stok lalu tambahkan ke cart
    ok = ProductsManager.change_stock(product_id, -quantity)
    if not ok:
        message = 'Gagal mengupdate stok. Silakan coba lagi.'
        if request.is_json:
            return jsonify({'success': False, 'message': message})
        flash(message, 'error')
        return redirect(request.referrer or url_for('pages.home_page'))

    # Tambahkan ke keranjang
    CartManager.add_to_cart(product_id, product['name'], product['price'], quantity, product.get('phone', ''))
    message = f'✅ {product["name"]} berhasil ditambahkan ke keranjang!'
    
    if request.is_json:
        return jsonify({'success': True, 'message': message})
    
    flash(message, 'success')
    return redirect(url_for('cart.cart_page'))

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
    return redirect(url_for('cart.cart_page'))

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
    
    return render_template('Cart.html', 
                         cart=cart, 
                         cart_count=cart_count, 
                         total=total)