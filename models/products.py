import os, json
from threading import Lock

_PRODUCTS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'products.json')
_SAVE_LOCK = Lock()

class ProductsManager:
    @staticmethod
    def _load():
        try:
            path = os.path.abspath(_PRODUCTS_FILE)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    @staticmethod
    def _save(data):
        path = os.path.abspath(_PRODUCTS_FILE)
        dirpath = os.path.dirname(path)
        os.makedirs(dirpath, exist_ok=True)
        tmp = path + '.tmp'
        with _SAVE_LOCK:
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, path)

    @classmethod
    def get_all(cls):
        return cls._load()

    @classmethod
    def get(cls, product_id):
        return cls._load().get(product_id)

    @classmethod
    def get_stock(cls, product_id):
        p = cls.get(product_id)
        return p.get('stock', 0) if p else 0

    @classmethod
    def set_stock(cls, product_id, value):
        data = cls._load()
        if product_id in data:
            data[product_id]['stock'] = int(value)
            cls._save(data)
            return True
        return False

    @classmethod
    def change_stock(cls, product_id, delta):
        data = cls._load()
        p = data.get(product_id)
        if not p:
            return False
        new = int(p.get('stock', 0)) + int(delta)
        if new < 0:
            return False
        p['stock'] = new
        cls._save(data)
        return True

    @classmethod
    def add_product(cls, product_data):
        """Menambahkan produk baru ke dalam database"""
        data = cls._load()
        product_id = product_data.get('id')
        if product_id and product_id not in data:
            data[product_id] = product_data
            cls._save(data)
            return True
        return False

    @classmethod
    def generate_product_id(cls):
        """Generate ID produk baru"""
        data = cls._load()
        existing_ids = list(data.keys())
        counter = 1
        while f"p_produk_{counter}" in existing_ids:
            counter += 1
        return f"p_produk_{counter}"