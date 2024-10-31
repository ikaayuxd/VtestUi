import os
import tempfile
import random
import re
import subprocess
import threading
import time
import ctypes
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk

import ctypes
from tkinter import messagebox, ttk
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

codigo_view_py = """
import os
import sys
import requests
import threading
from threading import active_count

n_threads = 1000
threads = []

if len(sys.argv) > 1:
    link1 = sys.argv[1]
else:
    sys.exit(1) 

def view2(proxy):
    try:
        channel = link1.split('/')[3]
        msgid = link1.split('/')[4]
        send_seen(channel, msgid, proxy)
    except Exception:
        pass  

def send_seen(channel, msgid, proxy):
    s = requests.Session()
    s.proxies = {
        'http': proxy,
        'https': proxy,
    }
    
    try:
        a = s.get(f"https://t.me/{channel}/{msgid}", timeout=10)
        cookie = a.headers.get('set-cookie', '').split(';')[0]
    except Exception:
        return False 

    headers = {
        "Accept": "*/*",
        "Cookie": cookie,
        "User-Agent": "Chrome",
    }
    
    data = {"_rl": "1"}

    try:
        r = s.post(f'https://t.me/{channel}/{msgid}?embed=1', json=data, headers=headers)
        key = r.text.split('data-view="')[1].split('"')[0]
        now_view = r.text.split('<span class="tgme_widget_message_views">')[1].split('</span>')[0]

        if "K" in now_view:
            now_view = now_view.replace("K", "00").replace(".", "")
    except Exception:
        return False

    headers["X-Requested-With"] = "XMLHttpRequest"
    
    try:
        response = s.get(f'https://t.me/v/?views={key}', headers=headers)
        if response.text == "true":
            pass  
    except Exception:
        return False

def scrap():
    try:
        proxies = {
            "https": requests.get("https://api.proxyscrape.com/?request=displayproxies&proxytype=https", timeout=5).text.splitlines(),
            "http": requests.get("https://api.proxyscrape.com/?request=displayproxies&proxytype=http", timeout=5).text.splitlines(),
            "socks": requests.get("https://api.proxyscrape.com/?request=displayproxies&proxytype=socks4", timeout=5).text.splitlines(),
        }
        return proxies
    except Exception:
        return False 

def is_proxy_valid(proxy, test_url="https://www.google.com"):
    try:
        response = requests.get(test_url, proxies={"http": proxy, "https": proxy}, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def checker(proxy):
    if is_proxy_valid(proxy):  # Solo continuar si el proxy es válido
        view2(proxy)

def checker(proxy):
    try:
        if is_proxy_valid(proxy):  # Solo continuar si el proxy es válido
            view2(proxy)
    except Exception:
        pass 

def start():
    proxies = scrap()
    if not proxies:
        return

    for p in proxies.get('https', []):
        p = p.strip()
        if p:
            while active_count() > n_threads:
                continue
            thread = threading.Thread(target=checker, args=(p,))
            threads.append(thread)
            thread.start()

    for p in proxies.get('http', []):
        p = p.strip()
        if p:
            while active_count() > n_threads:
                continue
            thread = threading.Thread(target=checker, args=(p,))
            threads.append(thread)
            thread.start()

    for p in proxies.get('socks', []):
        p = p.strip()
        if p:
            while active_count() > n_threads:
                continue
            pr = f"socks5://{p}"
            thread = threading.Thread(target=checker, args=(pr,))
            threads.append(thread)
            thread.start()

def process(run_for_ever: bool = False):
    if run_for_ever:
        while True:
            start()
    else:
        start()

process(False)
"""
tmp_dir = tempfile.gettempdir()
link_index = 0
processes = []
is_running = False
telegram_url_regex = r"^https:\/\/t\.me\/[a-zA-Z0-9_\/]+$"

def open_url():
    url = "https://t.me/underbytes"
    subprocess.Popen(['cmd', '/c', 'start', url])

def crear_subcarpetas_y_generar_scripts(num_subcarpetas):
    subcarpetas = []
    for _ in range(num_subcarpetas):
        nombre_subcarpeta = str(random.randint(1000, 9999))
        ruta_subcarpeta = os.path.join(tmp_dir, nombre_subcarpeta)
        os.makedirs(ruta_subcarpeta, exist_ok=True)
        destino_script = os.path.join(ruta_subcarpeta, 'view.py')
        
        with open(destino_script, 'w', encoding='utf-8') as archivo:  
            archivo.write(codigo_view_py)  
        
        subcarpetas.append(ruta_subcarpeta)
    return subcarpetas


def ejecutar_scripts_en_subcarpetas(subcarpetas, link):
    global processes
    for carpeta in subcarpetas:
        script_a_ejecutar = os.path.join(carpeta, 'view.py')
        comando = ['python', script_a_ejecutar, link]
        process = subprocess.Popen(comando)
        processes.append(process)

def iniciar_ejecucion():
    global is_running, link_index
    if is_running:
        return
    is_running = True
    num_subcarpetas = int(entry_num_subcarpetas.get())
    while is_running:
        subcarpetas = crear_subcarpetas_y_generar_scripts(num_subcarpetas)
        link_actual = tree.item(tree.get_children()[link_index])['values'][0]
        ejecutar_scripts_en_subcarpetas(subcarpetas, link_actual)
        link_index = (link_index + 1) % len(tree.get_children())
        root.update()
        time.sleep(60)

def iniciar_ejecucion_en_hilo():
    open_url()
    threading.Thread(target=iniciar_ejecucion).start()

def detener_ejecucion():
    global is_running, processes
    is_running = False
    for process in processes:
        process.terminate()
    processes.clear()
    messagebox.showinfo("Stopped", "All processes have been stopped.")

def agregar_link():
    link = entry_link.get()
    if re.match(telegram_url_regex, link):
        tree.insert('', 'end', values=(link,))
        entry_link.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Please enter a valid Telegram URL.")

def eliminar_link():
    selected_item = tree.selection()
    if selected_item:
        tree.delete(selected_item)

def start_move(event):
    root.x = event.x
    root.y = event.y

def stop_move(event):
    root.x = None
    root.y = None

def on_motion(event):
    x = (event.x_root - root.x)
    y = (event.y_root - root.y)
    root.geometry(f"+{x}+{y}")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.geometry("500x410")
root.title("𝐒𝐇𝐈𝐓 𝐔𝐍𝐃𝐄𝐑 💀")
root.configure(bg="#262626")
root.resizable(False, False)
root.overrideredirect(True) 
root.wm_attributes('-alpha', 0.92)
icon_path = os.path.abspath("undermain.ico")
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)


root.bind("<Button-1>", start_move)
root.bind("<ButtonRelease-1>", stop_move)
root.bind("<B1-Motion>", on_motion)

frame_config = ctk.CTkFrame(root, fg_color="#262626")
frame_config.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

label_num_subcarpetas = ctk.CTkLabel(frame_config, text="Procss:", text_color="#ffffff")
label_num_subcarpetas.grid(row=0, column=0, padx=(5, 0), pady=5, sticky="w")
entry_num_subcarpetas = ctk.CTkEntry(frame_config, width=50)
entry_num_subcarpetas.grid(row=0, column=1, padx=5, pady=5)
entry_num_subcarpetas.insert(0, "5")

label_link = ctk.CTkLabel(frame_config, text="Link:", text_color="#ffffff")
label_link.grid(row=0, column=2, padx=(10, 5), pady=5, sticky="w")
entry_link = ctk.CTkEntry(frame_config, width=140)
entry_link.grid(row=0, column=3, padx=5, pady=5)

btn_agregar = ctk.CTkButton(frame_config, text="Add Link", command=agregar_link, fg_color="#ba4a4a", hover_color="#953636")
btn_agregar.grid(row=0, column=4, padx=5, pady=5)

frame_tabla = ctk.CTkFrame(root, fg_color="#262626")
frame_tabla.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

tree = ttk.Treeview(frame_tabla, columns=("LINKS"), show="headings", height=6)
tree.heading("LINKS", text="LINKS")
tree.pack(side="left", fill="both", expand=True)
style = ttk.Style()
style.configure("Treeview", background="#333333", foreground="white", rowheight=25, fieldbackground="#333333")
style.map('Treeview', background=[('selected', '#4f4f4f')])

scrollbar = ctk.CTkScrollbar(frame_tabla, orientation="vertical", command=tree.yview)
scrollbar.pack(side="right", fill="y")
tree.configure(yscrollcommand=scrollbar.set)

frame_botones = ctk.CTkFrame(root, fg_color="#262626")
frame_botones.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))

btn_eliminar = ctk.CTkButton(frame_botones, text="Remove", command=eliminar_link, fg_color="#3A3A4D", hover_color="#953636")
btn_eliminar.grid(row=0, column=0, padx=5, pady=5)

btn_iniciar = ctk.CTkButton(frame_botones, text="Start", command=iniciar_ejecucion_en_hilo, fg_color="#3A3A4D", hover_color="#276749")
btn_iniciar.grid(row=0, column=1, padx=5, pady=5)

btn_detener = ctk.CTkButton(frame_botones, text="Stop", command=detener_ejecucion, fg_color="#3A3A4D", hover_color="#953636")
btn_detener.grid(row=0, column=2, padx=5, pady=5)

root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

root.mainloop()
