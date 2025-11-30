import json
import os
from datetime import datetime

class OrderManager:
    """Class untuk mengelola pesanan"""
    
    ORDER_FILE = 'data/orders.json'
    
    @staticmethod
    def _ensure_data_dir():
        """Pastikan direktori data ada"""
        os.makedirs('data', exist_ok=True)
    
    @staticmethod
    def _load_orders():
        """
        Memuat data pesanan dari file JSON
        Returns: List pesanan
        """
        OrderManager._ensure_data_dir()
        
        if not os.path.exists(OrderManager.ORDER_FILE):
            # Jika file tidak ada, buat file kosong
            with open(OrderManager.ORDER_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)
            return []
        
        try:
            with open(OrderManager.ORDER_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    @staticmethod
    def _save_orders(orders):
        """
        Menyimpan data pesanan ke file JSON
        Args:
            orders: List pesanan
        Returns: Boolean sukses/gagal
        """
        try:
            OrderManager._ensure_data_dir()
            with open(OrderManager.ORDER_FILE, 'w', encoding='utf-8') as f:
                json.dump(orders, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error saving orders: {e}")
            return False
    
    @staticmethod
    def create_order(order_data):
        """
        Membuat pesanan baru
        Args:
            order_data: Dictionary data pesanan
        Returns: Boolean sukses/gagal
        """
        try:
            orders = OrderManager._load_orders()
            
            # Validasi data wajib
            required_fields = ['order_id', 'user_id', 'fullname', 'phone', 'items', 'total', 'pickup_location']
            for field in required_fields:
                if field not in order_data:
                    print(f"Missing required field: {field}")
                    return False
            
            # Pastikan items adalah list
            if not isinstance(order_data['items'], list):
                print("Items must be a list")
                return False
            
            # Tambahkan timestamp jika belum ada
            if 'created_at' not in order_data:
                order_data['created_at'] = datetime.now().isoformat()
            
            # Set default status jika belum ada
            if 'status' not in order_data:
                order_data['status'] = 'menunggu_pembayaran'
            
            if 'payment_status' not in order_data:
                order_data['payment_status'] = 'pending'
            
            # Tambahkan pesanan ke list
            orders.append(order_data)
            
            # Simpan ke file
            return OrderManager._save_orders(orders)
            
        except Exception as e:
            print(f"Error creating order: {e}")
            return False
    
    @staticmethod
    def get_order_by_id(order_id):
        """
        Mengambil pesanan berdasarkan ID
        Args:
            order_id: ID pesanan
        Returns: Dictionary pesanan atau None
        """
        try:
            orders = OrderManager._load_orders()
            
            for order in orders:
                if order.get('order_id') == order_id:
                    return order
            
            return None
            
        except Exception as e:
            print(f"Error getting order by ID: {e}")
            return None
    
    @staticmethod
    def get_orders_by_user_id(user_id):
        """
        Mengambil semua pesanan berdasarkan user ID
        Args:
            user_id: ID pengguna
        Returns: List pesanan
        """
        try:
            orders = OrderManager._load_orders()
            
            user_orders = []
            for order in orders:
                if order.get('user_id') == user_id:
                    user_orders.append(order)
            
            # Urutkan berdasarkan tanggal terbaru
            user_orders.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return user_orders
            
        except Exception as e:
            print(f"Error getting orders by user ID: {e}")
            return []
    
    @staticmethod
    def get_all_orders():
        """
        Mengambil semua pesanan
        Returns: List semua pesanan
        """
        try:
            orders = OrderManager._load_orders()
            
            # Urutkan berdasarkan tanggal terbaru
            orders.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return orders
            
        except Exception as e:
            print(f"Error getting all orders: {e}")
            return []
    
    @staticmethod
    def update_order_status(order_id, status):
        """
        Mengupdate status pesanan
        Args:
            order_id: ID pesanan
            status: Status baru
        Returns: Boolean sukses/gagal
        """
        try:
            orders = OrderManager._load_orders()
            
            for order in orders:
                if order.get('order_id') == order_id:
                    order['status'] = status
                    order['updated_at'] = datetime.now().isoformat()
                    return OrderManager._save_orders(orders)
            
            return False
            
        except Exception as e:
            print(f"Error updating order status: {e}")
            return False
    
    @staticmethod
    def update_payment_status(order_id, payment_status):
        """
        Mengupdate status pembayaran
        Args:
            order_id: ID pesanan
            payment_status: Status pembayaran baru
        Returns: Boolean sukses/gagal
        """
        try:
            orders = OrderManager._load_orders()
            
            for order in orders:
                if order.get('order_id') == order_id:
                    order['payment_status'] = payment_status
                    order['updated_at'] = datetime.now().isoformat()
                    return OrderManager._save_orders(orders)
            
            return False
            
        except Exception as e:
            print(f"Error updating payment status: {e}")
            return False
    
    @staticmethod
    def delete_order(order_id):
        """
        Menghapus pesanan
        Args:
            order_id: ID pesanan
        Returns: Boolean sukses/gagal
        """
        try:
            orders = OrderManager._load_orders()
            
            orders = [order for order in orders if order.get('order_id') != order_id]
            
            return OrderManager._save_orders(orders)
            
        except Exception as e:
            print(f"Error deleting order: {e}")
            return False
    
    @staticmethod
    def get_order_statistics():
        """
        Mengambil statistik pesanan
        Returns: Dictionary statistik
        """
        try:
            orders = OrderManager._load_orders()
            
            total_orders = len(orders)
            total_revenue = sum(order.get('total', 0) for order in orders)
            
            status_count = {}
            for order in orders:
                status = order.get('status', 'unknown')
                status_count[status] = status_count.get(status, 0) + 1
            
            return {
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'status_breakdown': status_count
            }
            
        except Exception as e:
            print(f"Error getting order statistics: {e}")
            return {
                'total_orders': 0,
                'total_revenue': 0,
                'status_breakdown': {}
            }