import json
import logging
import hashlib
import re
from typing import List, Dict, Optional
from datetime import datetime

# Loglama ayarları
logging.basicConfig(
    filename='user_operations.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class UserValidationError(Exception):
    """Kullanıcı doğrulama hatalarını yönetmek için özel hata sınıfı."""
    pass

class UsersSave:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.users: List[Dict] = []
        self._load_users()
        logging.info(f"Sistem başlatıldı. Dosya yolu: {file_path}")

    def _save_users(self) -> None:
        """Tüm kullanıcıları JSON dosyasına kaydet."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as outfile:
                json.dump(self.users, outfile, ensure_ascii=False, indent=4)
            logging.info("Kullanıcılar başarıyla kaydedildi")
        except Exception as e:
            logging.error(f"Kayıt hatası: {str(e)}")
            raise

    def _load_users(self) -> None:
        """JSON dosyasından kullanıcıları yükle."""
        try:
            with open(self.file_path, 'r', encoding="utf-8") as openfile:
                self.users = json.load(openfile)
            logging.info("Kullanıcılar başarıyla yüklendi")
        except FileNotFoundError:
            self.users = []
            logging.info("Yeni kullanıcı listesi oluşturuldu")
        except json.JSONDecodeError as e:
            logging.error(f"JSON okuma hatası: {str(e)}")
            self.users = []

    @staticmethod
    def _validate_phone_number(number: str) -> bool:
        """Telefon numarası doğrulama."""
        pattern = r"^(05\d{9})$"  # Türkiye telefon formatı
        return bool(re.match(pattern, number))

    @staticmethod
    def _validate_password(password: str) -> bool:
        """Şifre karmaşıklığını kontrol et."""
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):  # Büyük harf kontrolü
            return False
        if not re.search(r"[a-z]", password):  # Küçük harf kontrolü
            return False
        if not re.search(r"\d", password):     # Rakam kontrolü
            return False
        return True

    @staticmethod
    def _hash_password(password: str) -> str:
        """Şifreyi güvenli bir şekilde hashle."""
        return hashlib.sha256(password.encode()).hexdigest()

    def add_user(self) -> None:
        """Kullanıcıdan bilgileri al ve sisteme ekle."""
        try:
            name = input("Lütfen adınızı girin: ").strip()
            if not name:
                raise UserValidationError("İsim boş olamaz!")

            number = input("Lütfen telefon numaranızı girin (05xxxxxxxxx): ").strip()
            if not self._validate_phone_number(number):
                raise UserValidationError("Geçersiz telefon numarası!")

            password = input("Lütfen şifrenizi girin (en az 8 karakter, büyük/küçük harf ve rakam içermeli): ")
            if not self._validate_password(password):
                raise UserValidationError("Şifre gereksinimleri karşılanmıyor!")

            user = {
                "name": name,
                "number": number,
                "password": self._hash_password(password),
                "created_at": datetime.now().isoformat()
            }

            self.users.append(user)
            self._save_users()
            logging.info(f"Yeni kullanıcı eklendi: {name}")
            print("Kullanıcı başarıyla kaydedildi!")

        except UserValidationError as e:
            logging.warning(f"Doğrulama hatası: {str(e)}")
            print(f"Hata: {str(e)}")
        except Exception as e:
            logging.error(f"Beklenmeyen hata: {str(e)}")
            print("Bir hata oluştu. Lütfen tekrar deneyin.")

    def find_user(self, phone_number: str) -> Optional[Dict]:
        """Telefon numarasına göre kullanıcı bul."""
        return next((user for user in self.users if user["number"] == phone_number), None)

    def update_user(self) -> None:
        """Kullanıcı bilgilerini güncelle."""
        number = input("Güncellenecek kullanıcının telefon numarasını girin: ")
        user = self.find_user(number)
        
        if user:
            print("\nGüncellenecek bilgiyi seçin:")
            print("1. İsim")
            print("2. Telefon Numarası")
            print("3. Şifre")
            
            choice = input("Seçiminiz (1-3): ")
            
            try:
                if choice == "1":
                    new_name = input("Yeni isim: ").strip()
                    if not new_name:
                        raise UserValidationError("İsim boş olamaz!")
                    user["name"] = new_name
                
                elif choice == "2":
                    new_number = input("Yeni telefon numarası: ").strip()
                    if not self._validate_phone_number(new_number):
                        raise UserValidationError("Geçersiz telefon numarası!")
                    user["number"] = new_number
                
                elif choice == "3":
                    new_password = input("Yeni şifre: ")
                    if not self._validate_password(new_password):
                        raise UserValidationError("Şifre gereksinimleri karşılanmıyor!")
                    user["password"] = self._hash_password(new_password)
                
                else:
                    print("Geçersiz seçim!")
                    return

                self._save_users()
                logging.info(f"Kullanıcı güncellendi: {user['name']}")
                print("Kullanıcı başarıyla güncellendi!")

            except UserValidationError as e:
                logging.warning(f"Güncelleme hatası: {str(e)}")
                print(f"Hata: {str(e)}")
        else:
            print("Kullanıcı bulunamadı!")

    def delete_user(self) -> None:
        """Kullanıcıyı sil."""
        number = input("Silinecek kullanıcının telefon numarasını girin: ")
        user = self.find_user(number)
        
        if user:
            self.users.remove(user)
            self._save_users()
            logging.info(f"Kullanıcı silindi: {user['name']}")
            print("Kullanıcı başarıyla silindi!")
        else:
            print("Kullanıcı bulunamadı!")

    def display_users(self) -> None:
        """Tüm kullanıcıları görüntüle."""
        if not self.users:
            print("Henüz kayıtlı kullanıcı bulunmamaktadır.")
            return
        
        for i, user in enumerate(self.users, 1):
            print(f"\nKullanıcı {i}:")
            print(f"Ad: {user['name']}")
            print(f"Numara: {user['number']}")
            print(f"Kayıt Tarihi: {user['created_at']}")

def main():
    users_save = UsersSave("users.json")
    
    while True:
        print("\n=== Kullanıcı Yönetim Sistemi ===")
        print("1. Yeni Kullanıcı Ekle")
        print("2. Kullanıcıları Görüntüle")
        print("3. Kullanıcı Güncelle")
        print("4. Kullanıcı Sil")
        print("5. Çıkış")
        
        choice = input("\nLütfen bir seçenek girin (1-5): ")
        
        if choice == "1":
            users_save.add_user()
        elif choice == "2":
            users_save.display_users()
        elif choice == "3":
            users_save.update_user()
        elif choice == "4":
            users_save.delete_user()
        elif choice == "5":
            print("Program sonlandırılıyor...")
            logging.info("Program sonlandırıldı")
            break
        else:
            print("Geçersiz seçenek! Lütfen tekrar deneyin.")

if __name__ == "__main__":
    main()