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
        
        # Validasi stok tidak boleh negatif
        if new_stock < 0:
            flash('Stok tidak boleh negatif')
            return redirect(url_for('pages.dashboard_page'))
            
    except ValueError:
        flash('Nilai stock tidak valid')
        return redirect(url_for('pages.dashboard_page'))
    ok = ProductsManager.set_stock(product_id, new_stock)
    flash('Stok berhasil diperbarui' if ok else 'Gagal memperbarui stok')
    return redirect(url_for('pages.dashboard_page'))

@pages_bp.route('/add_product', methods=['POST'])
@login_required
def add_product():
    """Route untuk menambahkan produk baru"""
    name = request.form.get('name')
    price_str = request.form.get('price')
    stock_str = request.form.get('stock')
    image = request.form.get('image')
    phone = request.form.get('phone')
    
    # Validasi input
    if not name or not price_str or not stock_str:
        flash('Semua field wajib diisi')
        return redirect(url_for('pages.dashboard_page'))
    
    try:
        price = int(price_str)
        stock = int(stock_str)
        
        # Validasi harga dan stok tidak boleh negatif
        if price < 0:
            flash('Harga tidak boleh negatif')
            return redirect(url_for('pages.dashboard_page'))
        if stock < 0:
            flash('Stok tidak boleh negatif')
            return redirect(url_for('pages.dashboard_page'))
            
    except ValueError:
        flash('Harga dan stok harus berupa angka')
        return redirect(url_for('pages.dashboard_page'))
    
    # Generate ID produk baru
    product_id = ProductsManager.generate_product_id()
    
    # Data produk baru
    product_data = {
        'id': product_id,
        'name': name,
        'price': price,
        'stock': stock,
        'image': image or '/static/picture/default.svg',
        'phone': phone or '081234567890'
    }
    
    # Tambahkan produk
    success = ProductsManager.add_product(product_data)
    if success:
        flash('Produk berhasil ditambahkan!')
    else:
        flash('Gagal menambahkan produk')
    
    return redirect(url_for('pages.dashboard_page'))

@pages_bp.route('/product/<product_id>')
@login_required
def product_detail(product_id):
    """
    Halaman detail produk dinamis berdasarkan ID
    """
    cart_count = CartManager.get_cart_count()
    product = ProductsManager.get(product_id)
    
    if not product:
        flash('Produk tidak ditemukan')
        return redirect(url_for('pages.home_page'))
    
    # Menggunakan template product detail yang dinamis
    return render_template('barang/product_detail.html', product=product, cart_count=cart_count)