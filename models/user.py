import os
import json
from werkzeug.security import generate_password_hash, check_password_hash

class UserManager:
    """Class untuk mengelola data user"""
    
    def __init__(self, json_file='user.json'):
        self.json_file = json_file
        self.users = self._load_users()
    
    def _load_users(self):
        """
        Memuat data user dari file JSON
        Returns: Dictionary berisi data semua user yang terdaftar
        """
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
        except Exception as e:
            print(f"Gagal memuat data user dari {self.json_file}: {e}")
        return {}
    
    def save_users(self):
        """
        Menyimpan data user ke file JSON dengan atomic operation
        """
        try:
            # Buat direktori jika belum ada
            dirpath = os.path.dirname(self.json_file)
            if dirpath and not os.path.exists(dirpath):
                os.makedirs(dirpath, exist_ok=True)
            
            # Simpan ke file temporary dulu untuk keamanan
            tmp_path = self.json_file + '.tmp'
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            
            # Pindahkan file temporary ke file asli (atomic operation)
            os.replace(tmp_path, self.json_file)
            
        except Exception as e:
            print(f"Gagal menyimpan data user ke {self.json_file}: {e}")
    
    def create_user(self, email, password, full_name):
        """
        Membuat user baru
        Args:
            email: Email user (digunakan sebagai username)
            password: Password user (akan di-hash)
            full_name: Nama lengkap user
        Returns:
            tuple: (success: bool, message: str)
        """
        if email in self.users:
            return False, "Email sudah terdaftar"
        
        # Hash password untuk keamanan
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        # Simpan user baru
        self.users[email] = {
            "username": email,
            "password_hash": hashed_password,
            "full_name": full_name
        }
        
        # Simpan ke file
        self.save_users()
        return True, "User berhasil dibuat"
    
    def authenticate_user(self, email, password):
        """
        Autentikasi user login
        Args:
            email: Email user
            password: Password user
        Returns:
            tuple: (success: bool, user_data: dict atau None)
        """
        user = self.users.get(email)
        if user and check_password_hash(user['password_hash'], password):
            return True, user
        return False, None
    
    def get_user(self, email):
        """
        Mendapatkan data user berdasarkan email
        Args:
            email: Email user
        Returns:
            dict: Data user atau None jika tidak ditemukan
        """
        return self.users.get(email)