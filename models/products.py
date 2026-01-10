# Import library untuk file operations, JSON handling, dan thread safety
import os, json
from threading import Lock

# Path ke file JSON yang menyimpan data produk
_PRODUCTS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'products.json')
# Lock untuk mencegah race condition saat concurrent write operations
_SAVE_LOCK = Lock()

class ProductsManager:
    """Class untuk mengelola data produk dengan operasi CRUD dan stock management"""
    @staticmethod
    def _load():
        """Memuat data produk dari file JSON
        Returns: Dictionary berisi semua data produk atau {} jika file tidak ada/error
        """
        try:
            path = os.path.abspath(_PRODUCTS_FILE)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            # Jika terjadi error, return empty dict sebagai fallback
            pass
        return {}

    @staticmethod
    def _save(data):
        """Menyimpan data produk ke file JSON dengan atomic operation
        Args: data - Dictionary berisi semua data produk
        """
        path = os.path.abspath(_PRODUCTS_FILE)
        dirpath = os.path.dirname(path)
        # Buat direktori jika belum ada
        os.makedirs(dirpath, exist_ok=True)
        tmp = path + '.tmp'  # File temporary untuk atomic write
        with _SAVE_LOCK:  # Gunakan lock untuk thread safety
            with open(tmp, 'w', encoding='utf-8') as f:
                # Simpan dengan format JSON yang readable (indent=2)
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.flush()  # Flush buffer ke OS
                os.fsync(f.fileno())  # Force write ke disk
            # Atomic replace: file asli tidak akan corrupt jika gagal
            os.replace(tmp, path)

    @classmethod
    def get_all(cls):
        """Mengambil semua data produk
        Returns: Dictionary dengan structure {product_id: product_data}
        """
        return cls._load()

    @classmethod
    def get(cls, product_id):
        """Mengambil data produk berdasarkan ID
        Args: product_id - ID unik produk
        Returns: Dictionary data produk atau None jika tidak ditemukan
        """
        return cls._load().get(product_id)

    @classmethod
    def get_stock(cls, product_id):
        """Mengambil jumlah stok produk
        Args: product_id - ID unik produk
        Returns: Integer jumlah stok, 0 jika produk tidak ada
        """
        p = cls.get(product_id)
        return p.get('stock', 0) if p else 0

    @classmethod
    def set_stock(cls, product_id, value):
        """Mengatur stok produk ke nilai absolut tertentu
        Args: product_id - ID produk, value - Jumlah stok baru
        Returns: True jika berhasil, False jika produk tidak ditemukan
        """
        data = cls._load()
        if product_id in data:
            data[product_id]['stock'] = int(value)
            cls._save(data)
            return True
        return False

    @classmethod
    def change_stock(cls, product_id, delta):
        """Mengubah stok produk secara relatif (tambah/kurang)
        Args: product_id - ID produk, delta - Perubahan stok (+/-)
        Returns: True jika berhasil, False jika gagal/stok akan negatif
        Use cases: delta=-1 (kurang stok saat add to cart), delta=+1 (restore stok saat remove from cart)
        """
        data = cls._load()
        p = data.get(product_id)
        if not p:
            return False  # Produk tidak ditemukan
        new = int(p.get('stock', 0)) + int(delta)
        if new < 0:
            return False  # BUSINESS RULE: Cegah stok negatif (overselling)
        p['stock'] = new
        cls._save(data)
        return True

    @classmethod
    def add_product(cls, product_data):
        """Menambahkan produk baru ke dalam database
        Args: product_data - Dictionary berisi data produk lengkap dengan 'id'
        Returns: True jika berhasil ditambahkan, False jika ID sudah ada/invalid
        """
        data = cls._load()
        product_id = product_data.get('id')
        if product_id and product_id not in data:  # Validasi ID ada dan unique
            data[product_id] = product_data
            cls._save(data)
            return True
        return False  # ID tidak ada atau sudah digunakan

    @classmethod
    def generate_product_id(cls):
        """Generate ID produk baru dengan format p_produk_X
        Returns: String ID yang belum digunakan (contoh: p_produk_5)
        Logic: Cari counter terkecil yang belum dipakai
        """
        data = cls._load()
        existing_ids = list(data.keys())
        counter = 1
        # Loop sampai menemukan ID yang belum dipakai
        while f"p_produk_{counter}" in existing_ids:
            counter += 1
        return f"p_produk_{counter}"