from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.decorators import login_required
from models.cart import CartManager
from models.order import OrderManager
from models.pickup_location import PickupLocationManager
import uuid
from datetime import datetime

checkout_bp = Blueprint('checkout', __name__)

@checkout_bp.route('/checkout')  # ✅ ENDPOINT INI HARUS ADA
@login_required
def checkout():
    """Halaman checkout"""
    cart = CartManager.get_cart()
    
    if not cart:
        flash('Keranjang Anda kosong!', 'error')
        return redirect(url_for('cart.cart_page'))
    
    total = CartManager.get_cart_total()
    pickup_locations = PickupLocationManager.get_all_locations()  # ← Pastikan ini mengirim data
    
    print(f"DEBUG: pickup_locations = {pickup_locations}")  # ← Debug
    
    return render_template('Checkout.html', 
                         cart=cart, 
                         total=total, 
                         pickup_locations=pickup_locations)

@checkout_bp.route('/place_order', methods=['POST'])
@login_required
def place_order():
    """Proses pemesanan COD"""
    try:
        # Validasi keranjang tidak kosong
        cart = CartManager.get_cart()
        if not cart:
            flash('Keranjang Anda kosong!', 'error')
            return redirect(url_for('cart.cart_page'))
        
        # Ambil data dari form
        fullname = request.form.get('fullname', '').strip()
        phone = request.form.get('phone', '').strip()
        pickup_location_id = request.form.get('pickup_location', '').strip()
        notes = request.form.get('notes', '').strip()
        terms_agreed = request.form.get('terms_agreed')
        
        # Validasi data wajib
        if not fullname or not phone or not pickup_location_id:
            flash('Mohon lengkapi semua data yang wajib diisi!', 'error')
            return redirect(url_for('checkout.checkout'))
        
        if not terms_agreed:
            flash('Anda harus menyetujui syarat dan ketentuan!', 'error')
            return redirect(url_for('checkout.checkout'))
        
        # Generate order ID unik
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        # Persiapkan data items DENGAN NOMOR TELEPON
        items = []
        total = 0
        
        for item in cart:
            item_data = {
                'name': item['name'],
                'price': item['price'],
                'quantity': item['quantity'],
                'phone': item.get('phone', 'Tidak tersedia')
            }
            items.append(item_data)
            total += item['price'] * item['quantity']
        
        # Buat data pesanan
        order_data = {
            'order_id': order_id,
            'user_id': session.get('user_id', 'unknown'),
            'user_email': session.get('user_email', 'unknown'),
            'fullname': fullname,
            'phone': phone,
            'items': items,
            'total': total,
            'pickup_location': pickup_location_id,
            'status': 'menunggu_pembayaran',
            'payment_status': 'pending',
            'created_at': datetime.now().isoformat(),
            'notes': notes
        }
        
        # Simpan pesanan
        success = OrderManager.create_order(order_data)
        if not success:
            flash('Gagal membuat pesanan. Silakan coba lagi.', 'error')
            return redirect(url_for('checkout.checkout'))
        
        # Kosongkan keranjang
        CartManager.clear_cart()
        
        flash('✅ Pesanan berhasil dibuat!', 'success')
        return redirect(url_for('checkout.order_confirmation', order_id=order_id))
        
    except Exception as e:
        print(f"Error saat place_order: {e}")
        flash('Terjadi kesalahan saat memproses pesanan. Silakan coba lagi.', 'error')
        return redirect(url_for('checkout.checkout'))

@checkout_bp.route('/order/<order_id>')
@login_required
def order_confirmation(order_id):
    """Halaman konfirmasi pesanan"""
    order = OrderManager.get_order_by_id(order_id)
    
    if not order:
        flash('Pesanan tidak ditemukan!', 'error')
        return redirect(url_for('pages.home_page'))
    
    # Ambil data lokasi pickup
    location = PickupLocationManager.get_location_by_id(order.get('pickup_location'))
    
    return render_template('OrderConfirmation.html', 
                         order=order, 
                         location=location)

@checkout_bp.route('/orders')
@login_required
def order_history():
    """Halaman riwayat pesanan"""
    user_id = session.get('user_id')
    orders = OrderManager.get_orders_by_user_id(user_id)
    
    return render_template('OrderHistory.html', orders=orders)