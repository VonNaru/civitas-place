import json
import os

class PickupLocationManager:
    """Class untuk mengelola lokasi pengambilan"""
    
    LOCATION_FILE = 'data/pickup_locations.json'
    
    @staticmethod
    def _ensure_data_dir():
        """Pastikan direktori data ada"""
        os.makedirs('data', exist_ok=True)
    
    @staticmethod
    def _load_locations():
        """
        Memuat data lokasi dari file JSON
        Returns: Dictionary lokasi
        """
        PickupLocationManager._ensure_data_dir()
        
        if not os.path.exists(PickupLocationManager.LOCATION_FILE):
            # Jika file tidak ada, buat dengan data default
            default_locations = {
                "loc_library": {
                    "id": "loc_library",
                    "name": "Perpustakaan Utama",
                    "address": "Gedung Perpustakaan Kampus, Lantai 1",
                    "operating_hours": "08:00 - 17:00",
                    "phone": "021-12345678",
                    "description": "Lobi utama perpustakaan, dekat dengan meja informasi"
                },
                "loc_canteen": {
                    "id": "loc_canteen",
                    "name": "Kafeteria Kantin Utama",
                    "address": "Gedung Student Center, Lantai 2",
                    "operating_hours": "10:00 - 18:00",
                    "phone": "021-12345679",
                    "description": "Area kasir kafeteria, meja pickup khusus"
                },
                "loc_student_center": {
                    "id": "loc_student_center",
                    "name": "Student Center",
                    "address": "Gedung Student Center, Lantai 1",
                    "operating_hours": "09:00 - 19:00",
                    "phone": "021-12345680",
                    "description": "Lobby utama Student Center, meja layanan mahasiswa"
                }
            }
            
            with open(PickupLocationManager.LOCATION_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_locations, f, ensure_ascii=False, indent=4)
            
            return default_locations
        
        try:
            with open(PickupLocationManager.LOCATION_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    @staticmethod
    def _save_locations(locations):
        """
        Menyimpan data lokasi ke file JSON
        Args:
            locations: Dictionary lokasi
        Returns: Boolean sukses/gagal
        """
        try:
            PickupLocationManager._ensure_data_dir()
            with open(PickupLocationManager.LOCATION_FILE, 'w', encoding='utf-8') as f:
                json.dump(locations, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error saving locations: {e}")
            return False
    
    @staticmethod
    def get_all_locations():
        """
        Mengambil semua lokasi pengambilan
        Returns: Dictionary semua lokasi
        """
        try:
            return PickupLocationManager._load_locations()
        except Exception as e:
            print(f"Error getting all locations: {e}")
            return {}
    
    @staticmethod
    def get_location_by_id(location_id):
        """
        Mengambil lokasi berdasarkan ID
        Args:
            location_id: ID lokasi
        Returns: Dictionary lokasi atau None
        """
        try:
            locations = PickupLocationManager._load_locations()
            return locations.get(location_id)
        except Exception as e:
            print(f"Error getting location by ID: {e}")
            return None
    
    @staticmethod
    def get_locations_list():
        """
        Mengambil lokasi dalam bentuk list untuk template
        Returns: List lokasi
        """
        try:
            locations = PickupLocationManager._load_locations()
            return list(locations.values())
        except Exception as e:
            print(f"Error getting locations list: {e}")
            return []
    
    @staticmethod
    def add_location(location_data):
        """
        Menambah lokasi baru
        Args:
            location_data: Dictionary data lokasi
        Returns: Boolean sukses/gagal
        """
        try:
            locations = PickupLocationManager._load_locations()
            
            # Validasi data wajib
            required_fields = ['id', 'name', 'address', 'operating_hours', 'phone']
            for field in required_fields:
                if field not in location_data:
                    print(f"Missing required field: {field}")
                    return False
            
            location_id = location_data['id']
            locations[location_id] = location_data
            
            return PickupLocationManager._save_locations(locations)
            
        except Exception as e:
            print(f"Error adding location: {e}")
            return False
    
    @staticmethod
    def update_location(location_id, location_data):
        """
        Mengupdate lokasi
        Args:
            location_id: ID lokasi
            location_data: Dictionary data lokasi baru
        Returns: Boolean sukses/gagal
        """
        try:
            locations = PickupLocationManager._load_locations()
            
            if location_id not in locations:
                return False
            
            locations[location_id].update(location_data)
            
            return PickupLocationManager._save_locations(locations)
            
        except Exception as e:
            print(f"Error updating location: {e}")
            return False
    
    @staticmethod
    def delete_location(location_id):
        """
        Menghapus lokasi
        Args:
            location_id: ID lokasi
        Returns: Boolean sukses/gagal
        """
        try:
            locations = PickupLocationManager._load_locations()
            
            if location_id in locations:
                del locations[location_id]
                return PickupLocationManager._save_locations(locations)
            
            return False
            
        except Exception as e:
            print(f"Error deleting location: {e}")
            return False
    
    @staticmethod
    def is_location_available(location_id):
        """
        Cek apakah lokasi tersedia
        Args:
            location_id: ID lokasi
        Returns: Boolean tersedia/tidak
        """
        try:
            locations = PickupLocationManager._load_locations()
            return location_id in locations
        except Exception as e:
            print(f"Error checking location availability: {e}")
            return False
    
    @staticmethod
    def get_location_name(location_id):
        """
        Mengambil nama lokasi berdasarkan ID
        Args:
            location_id: ID lokasi  
        Returns: String nama lokasi atau "Unknown Location"
        """
        try:
            location = PickupLocationManager.get_location_by_id(location_id)
            return location.get('name', 'Unknown Location') if location else 'Unknown Location'
        except Exception as e:
            print(f"Error getting location name: {e}")
            return 'Unknown Location'