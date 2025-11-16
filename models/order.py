import os
import json
from datetime import datetime

class OrderManager:
    """Class untuk mengelola data pesanan/order"""
    
    def __init__(self, json_file='orders.json'):
        self.json_file = json_file
        self.orders = self._load_orders()
    
    def _load_orders(self):
        """
        Memuat data order dari file JSON
        Returns: Dictionary berisi data semua order
        """
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
        except Exception as e:
            print(f"Gagal memuat data order dari {self.json_file}: {e}")
        return {}
    
    def save_orders(self):
        """
        Menyimpan data order ke file JSON dengan atomic operation
        """
        try:
            # Buat direktori jika belum ada
            dirpath = os.path.dirname(self.json_file)
            if dirpath and not os.path.exists(dirpath):
                os.makedirs(dirpath, exist_ok=True)
            
            # Simpan ke file temporary dulu untuk keamanan
            tmp_path = self.json_file + '.tmp'
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump(self.orders, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            
            # Pindahkan file temporary ke file asli (atomic operation)
            os.replace(tmp_path, self.json_file)
            
        except Exception as e:
            print(f"Gagal menyimpan data order ke {self.json_file}: {e}")
    
    def create_order(self, user_email, user_name, items, total, payment_method='COD', shipping_address=''):
        """
        Membuat order baru
        Args:
            user_email: Email user yang melakukan order
            user_name: Nama user
            items: List item yang dibeli
            total: Total harga
            payment_method: Metode pembayaran (default: COD)
            shipping_address: Alamat pengiriman
        Returns:
            str: Order ID yang baru dibuat
        """
        # Generate order ID dengan format ORDER-timestamp
        order_id = f"ORDER-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Simpan order baru
        self.orders[order_id] = {
            "order_id": order_id,
            "user_email": user_email,
            "user_name": user_name,
            "items": items,
            "total": total,
            "payment_method": payment_method,
            "shipping_address": shipping_address,
            "status": "pending",  # Status: pending, confirmed, delivered, cancelled
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Simpan ke file
        self.save_orders()
        return order_id
    
    def get_order(self, order_id):
        """
        Mendapatkan data order berdasarkan order_id
        Args:
            order_id: ID order
        Returns:
            dict: Data order atau None jika tidak ditemukan
        """
        return self.orders.get(order_id)
    
    def get_user_orders(self, user_email):
        """
        Mendapatkan semua order dari user tertentu
        Args:
            user_email: Email user
        Returns:
            list: List order user
        """
        user_orders = []
        for order_id, order_data in self.orders.items():
            if order_data.get('user_email') == user_email:
                user_orders.append(order_data)
        
        # Sort berdasarkan tanggal (newest first)
        user_orders.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return user_orders
