from flask import session

class CartManager:
    """Class untuk mengelola keranjang belanja"""
    
    @staticmethod
    def get_cart():
        """
        Mendapatkan data keranjang dari session
        Returns: List berisi item-item di keranjang
        """
        return session.get('cart', [])
    
    @staticmethod
    def get_cart_count():
        """
        Menghitung jumlah jenis produk di keranjang
        Returns: Integer jumlah jenis produk
        """
        cart = CartManager.get_cart()
        return len(cart)
    
    @staticmethod
    def get_cart_total():
        """
        Menghitung total harga semua item di keranjang
        Returns: Integer total harga
        """
        cart = CartManager.get_cart()
        return sum(item['price'] * item['quantity'] for item in cart)
    
    @staticmethod
    def add_to_cart(product_id, name, price, quantity=1):
        """
        Menambahkan produk ke keranjang
        Args:
            product_id: ID unik produk
            name: Nama produk
            price: Harga produk
            quantity: Jumlah produk (default: 1)
        """
        cart = CartManager.get_cart()
        
        # Cek apakah produk sudah ada di keranjang
        for item in cart:
            if item['product_id'] == product_id:
                # Jika sudah ada, tambahkan quantity
                item['quantity'] += quantity
                break
        else:
            # Jika belum ada, tambahkan produk baru
            cart.append({
                'product_id': product_id,
                'name': name,
                'price': int(price),
                'quantity': quantity
            })
        
        # Simpan kembali ke session
        session['cart'] = cart
    
    @staticmethod
    def remove_from_cart(product_id):
        """
        Menghapus produk dari keranjang
        Args:
            product_id: ID produk yang akan dihapus
        """
        cart = CartManager.get_cart()
        cart = [item for item in cart if item['product_id'] != product_id]
        session['cart'] = cart
    
    @staticmethod
    def clear_cart():
        """
        Mengosongkan keranjang
        """
        session['cart'] = []