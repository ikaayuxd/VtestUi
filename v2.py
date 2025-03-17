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
import sys
import json

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

codigo_view_py = r"""

import aiohttp, asyncio
from re import search
from aiohttp_socks import ProxyConnector
from argparse import ArgumentParser
from re import compile
from os import system, name
from threading import Thread
from time import sleep
import random
from rich.console import Console
from rich.table import Table
from rich.live import Live
import json
import itertools

def generate_user_agent():
    bases = [
        "Mozilla/5.0 ({system}) AppleWebKit/537.36 (KHTML, like Gecko) {browser}/{version} Safari/537.36",
        "Mozilla/5.0 ({system}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 ({system}; rv:{version}) Gecko/20100101 Firefox/{version}",
        "Mozilla/5.0 ({system}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36 Edg/{edge_version}",
    ]
    systems = [
        "Windows NT 10.0; Win64; x64",
        "Windows NT 6.1; WOW64",
        "Windows NT 5.1; Win32",
        "Macintosh; Intel Mac OS X 10_15_7",
        "Macintosh; Intel Mac OS X 11_3_1",
        "Linux; Android 11; Pixel 5",
        "Linux; Android 8.0.0; Nexus 5X",
        "iPhone; CPU iPhone OS 16_0 like Mac OS X",
        "iPad; CPU OS 15_0 like Mac OS X",
    ]
    browsers = [
        ("Chrome", list(range(80, 117))),
        ("Safari", [12, 13, 14, 15, 16]),
        ("Opera", list(range(40, 90))),
        ("Brave", [1, 1.1, 1.2, 1.3, 1.5]),
        ("Firefox", list(range(50, 117))),
        ("Edge", list(range(80, 116))),
    ]
    
    system = random.choice(systems)
    browser, versions = random.choice(browsers)
    version = random.choice(versions)
    base = random.choice(bases)
    edge_version = random.randint(80, 116)  
    
    return base.format(system=system, browser=browser, version=version, edge_version=edge_version)

REGEX = compile(
    r"(?:^|\D)?(("+ r"(?:[1-9]|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
    + r"\." + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
    + r"\." + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
    + r"\." + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
    + r"):" + (r"(?:\d|[1-9]\d{1,3}|[1-5]\d{4}|6[0-4]\d{3}"
    + r"|65[0-4]\d{2}|655[0-2]\d|6553[0-5])")
    + r")(?:\D|$)"
)

class Telegram:
    def __init__(self, channel: str, post: int) -> None:
        self.tasks = 1000
        self.channel = channel
        self.post = post
        self.cookie_error = 0
        self.sucsess_sent = 0
        self.failled_sent = 0
        self.token_error  = 0
        self.proxy_error  = 0
        self.console = Console()

    async def request(self, proxy: str, proxy_type: str):
        if proxy_type == 'socks4': connector = ProxyConnector.from_url(f'socks4://{proxy}')
        elif proxy_type == 'socks5': connector = ProxyConnector.from_url(f'socks5://{proxy}')
        elif proxy_type == 'https': connector = ProxyConnector.from_url(f'https://{proxy}')
        else: connector = ProxyConnector.from_url(f'http://{proxy}')

        jar = aiohttp.CookieJar(unsafe=True)
        async with aiohttp.ClientSession(cookie_jar=jar, connector=connector) as session:
            try:
                async with session.get(
                    f'https://t.me/{self.channel}/{self.post}?embed=1&mode=tme',
                    headers={
                        'referer': f'https://t.me/{self.channel}/{self.post}',
                        'user-agent': generate_user_agent()
                    }, timeout=aiohttp.ClientTimeout(total=5)
                ) as embed_response:

                    if jar.filter_cookies(embed_response.url).get('stel_ssid'):
                        views_token = search('data-view="([^"]+)"', await embed_response.text())
                        if views_token:
                            views_response = await session.post(
                                'https://t.me/v/?views=' + views_token.group(1),
                                headers={
                                    'referer': f'https://t.me/{self.channel}/{self.post}?embed=1&mode=tme',
                                    'user-agent': generate_user_agent(),
                                    'x-requested-with': 'XMLHttpRequest'
                                }, timeout=aiohttp.ClientTimeout(total=5)
                            )
                            if await views_response.text() == "true" and views_response.status == 200:
                                self.sucsess_sent += 1
                            else:
                                self.failled_sent += 1
                        else:
                            self.token_error += 1
                    else:
                        self.cookie_error += 1
            except:
                self.proxy_error += 1
            finally:
                jar.clear()

            status_update = json.dumps({
                "channel": self.channel,
                "post": self.post,
                "success": self.sucsess_sent,
                "fail": self.failled_sent,
                "proxy_err": self.proxy_error,
                "token_err": self.token_error,
                "cookie_err": self.cookie_error
            })
            print(f'\r{status_update}', end='', flush=True)
        
    
    def run_auto_tasks(self):
        while True:
            async def inner(proxies: tuple):
                await asyncio.wait(
                    [asyncio.create_task(self.request(proxy, proxy_type)) 
                    for proxy_type, proxy in proxies])
            auto = Auto()
            chunks = [auto.proxies[i:i+self.tasks] for i in range(0, len(auto.proxies), self.tasks)]
            for chunk in chunks: asyncio.run(inner(chunk))


    

    def cli(self):
   
        while True:
            
            self.sucsess_sent += 1
            self.failled_sent += 2
            self.proxy_error += 1
            self.token_error += 1
            self.cookie_error += 1

            sleep(1) 

class Auto:
    def __init__(self):
        self.proxies = []
        self.proxy_urls = {
            "http": [
                "https://api.proxyscrape.com/?request=displayproxies&proxytype=",
                "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Https.txt",
                "https://github.com/MrMarble/proxy-list/raw/main/all.txt",
                "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt",
                "https://github.com/gitrecon1455/ProxyScraper/raw/main/proxies.txt",
                "https://github.com/Zaeem20/FREE_PROXIES_LIST/raw/master/http.txt",
                "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt",
                "https://raw.githubusercontent.com/yemixzy/proxy-list/main/proxies/http.txt",
                "https://github.com/elliottophellia/proxylist/raw/master/results/http/global/http_checked.txt",
                "https://api.proxyscrape.com/?request=displayproxies&proxytype=http",
                "https://www.proxy-list.download/api/v1/get?type=http",
                "http://spys.me/proxy.txt",
                "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
                "https://api.openproxylist.xyz/http.txt",
                "https://www.my-proxy.com/free-proxy-list.html",
                "https://raw.githubusercontent.com/shiftytr/proxy-list/master/proxy.txt",
                "https://www.my-proxy.com/free-anonymous-proxy.html",
                "https://www.my-proxy.com/free-transparent-proxy.html",
                "https://www.my-proxy.com/free-proxy-list-2.html",
                "https://www.my-proxy.com/free-proxy-list-3.html",
                "https://www.my-proxy.com/free-proxy-list-4.html",
                "https://proxy50-50.blogspot.com/",
                "https://www.my-proxy.com/free-proxy-list-5.html",
                "http://alexa.lr2b.com/proxylist.txt",
                "http://rootjazz.com/proxies/proxies.txt",
                "https://www.my-proxy.com/free-socks-4-proxy.html",
                "https://www.my-proxy.com/free-proxy-list-6.html",
                "https://www.my-proxy.com/free-proxy-list-7.html",
                "https://www.my-proxy.com/free-proxy-list-8.html",
                "http://proxysearcher.sourceforge.net/Proxy%20List.php?type=http",
                "https://www.my-proxy.com/free-proxy-list-9.html",
                "https://www.my-proxy.com/free-proxy-list-10.html",
                "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
                "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
                "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
                "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
                "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
                "https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/http.txt",
                "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
                "https://raw.githubusercontent.com/opsxcq/proxy-list/master/list.txt",
                "https://proxy-spider.com/api/proxies.example.txt",
                "http://rootjazz.com/proxies/proxies.txt",
                "https://proxyspace.pro/http.txt",
                "https://proxyspace.pro/https.txt",
            ],
            "socks4": [
                "https://api.proxyscrape.com/?request=displayproxies&proxytype=socks4",
                "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4/data.txt",
                "https://openproxylist.xyz/socks4.txt",
                "https://proxyspace.pro/socks4.txt",
                "https://www.proxy-list.download/api/v1/get?type=socks4",
                "https://proxyhub.me/en/all-socks4-proxy-list.html",
                "https://proxy-tools.com/proxy/socks4"
                "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks4",
                "https://spys.me/socks.txt",
                "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4",
                "https://api.proxyscrape.com/?request=displayproxies&proxytype=socks4",
                "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt",
                "https://www.proxy-list.download/api/v1/get?type=socks4",
                "https://api.openproxylist.xyz/socks4.txt",
                "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt",
                "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
                "https://www.my-proxy.com/free-socks-4-proxy.html",
                "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt",
                "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
                "http://worm.rip/socks4.txt",
                "https://www.socks-proxy.net/",
                "https://www.my-proxy.com/free-socks-4-proxy.html",
                "https://cdn.jsdelivr.net/gh/B4RC0DE-TM/proxy-list/SOCKS4.txt",
                "https://cdn.jsdelivr.net/gh/jetkai/proxy-list/online-proxies/txt/proxies-socks4.txt",
                "https://cdn.jsdelivr.net/gh/roosterkid/openproxylist/SOCKS4_RAW.txt",
                "https://cdn.jsdelivr.net/gh/saschazesiger/Free-Proxies/proxies/socks4.txt",
                "https://cdn.jsdelivr.net/gh/TheSpeedX/PROXY-List/socks4.txt",
                "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
                "https://raw.githubusercontent.com/elliottophellia/yakumo/master/results/socks4/global/socks4_checked.txt",
                "https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks4.txt",
                "https://raw.githubusercontent.com/fahimscirex/proxybd/master/proxylist/socks4.txt",
                "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks4.txt",
                "https://raw.githubusercontent.com/yemixzy/proxy-list/main/proxies/socks4.txt",
                "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks4.txt",
                "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
                "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/generated/socks4_proxies.txt",
                "https://raw.githubusercontent.com/SevenworksDev/proxy-list/main/proxies/socks4.txt",
                "https://raw.githubusercontent.com/tuanminpay/live-proxy/master/socks4.txt",
                "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks4/socks4.txt",
                "https://raw.githubusercontent.com/Tsprnay/Proxy-lists/master/proxies/socks4.txt",
                "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt",
                "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks4.txt",
                "https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks4.txt",
            ],
            "socks5": [
                "https://api.proxyscrape.com/?request=displayproxies&proxytype=socks5",
                "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt",
                "https://openproxylist.xyz/socks5.txt",
                "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5",
                "https://proxyspace.pro/socks5.txt",
                "https://spys.me/socks.txt",
                "https://www.proxy-list.download/api/v1/get?type=socks5",
                "https://proxy-tools.com/proxy/socks5",
                "https://proxyhub.me/en/all-sock5-proxy-list.html",
                "https://www.my-proxy.com/free-socks-5-proxy.html",
                "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5",
                "https://cdn.jsdelivr.net/gh/HyperBeats/proxy-list/socks5.txt",
                "https://cdn.jsdelivr.net/gh/jetkai/proxy-list/online-proxies/txt/proxies-socks5.txt",
                "https://cdn.jsdelivr.net/gh/roosterkid/openproxylist/SOCKS5_RAW.txt",
                "https://cdn.jsdelivr.net/gh/TheSpeedX/PROXY-List/socks5.txt",
                "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
                "https://raw.githubusercontent.com/elliottophellia/yakumo/master/results/socks5/global/socks5_checked.txt",
                "https://raw.githubusercontent.com/fahimscirex/proxybd/master/proxylist/socks5.txt",
                "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt",
                "https://raw.githubusercontent.com/yemixzy/proxy-list/main/proxies/socks5.txt",
                "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
                "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks5.txt",
                "https://raw.githubusercontent.com/im-razvan/proxy_list/main/socks5.txt",
                "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
                "https://raw.githubusercontent.com/SevenworksDev/proxy-list/main/proxies/socks5.txt",
                "https://raw.githubusercontent.com/tuanminpay/live-proxy/master/socks5.txt",
                "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt"
                "https://raw.githubusercontent.com/Tsprnay/Proxy-lists/master/proxies/socks5.txt",
                "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt",
                "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks5.txt",
                "https://api.proxyscrape.com/?request=displayproxies&proxytype=socks5",
                "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5",
                "https://www.proxy-list.download/api/v1/get?type=socks5",
                "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
                "https://www.my-proxy.com/free-socks-5-proxy.html",
                "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt",
                "https://github.com/roosterkid/openproxylist/blob/main/SOCKS5_RAW.txt",
                "https://api.openproxylist.xyz/socks5.txt",
                "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
                "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5",
                "http://www.socks24.org/feeds/posts/default",
                "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt"
                "http://worm.rip/socks5.txt",
                "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
      
            ]
        }


        print(' [ WAIT ] Scraping proxies... ')
        asyncio.run(self.init())

    async def scrap(self, source_url, proxy_type):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    source_url, 
                    headers={'user-agent': generate_user_agent()}, 
                    timeout=aiohttp.ClientTimeout(total=10), 
                ) as response:
                    html = await response.text()
                    matches = REGEX.findall(html)
                    for match in matches:
                        self.proxies.append((proxy_type, match[0]))
        except Exception as e:
            with open('error.txt', 'a', encoding='utf-8', errors='ignore') as f:
                f.write(f'{source_url} -> {e}\n')


    async def init(self):
        tasks = []
        self.proxies.clear()
        for proxy_type, urls in self.proxy_urls.items():
            for source_url in urls:
                tasks.append(asyncio.create_task(self.scrap(source_url, proxy_type)))

        await asyncio.gather(*tasks)

        self.proxies = list(set(self.proxies))

        random.shuffle(self.proxies)

        print(f'[ INFO ] Total proxies disponibles: {len(self.proxies)}')
        self.proxy_iter = itertools.cycle(self.proxies)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-c', '--channel', dest='channel', help='Channel user', type=str, required=True)
    parser.add_argument('-pt', '--post', dest='post', help='Post number', type=int, required=True)
    args = parser.parse_args()

    api = Telegram(args.channel, args.post)

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(api.run_auto_tasks())


"""

tmp_dir = tempfile.gettempdir()
link_index = 0
processes = []
is_running = False
lock = threading.Lock()
telegram_url_regex = r"^https:\/\/t\.me\/[a-zA-Z0-9_]+\/[0-9]+$"

class Manager:
    def __init__(self, tree):
        self.tree = tree
        self.processes = {}  
        self.data = {} 
        
    def create_view_copy(self, index, channel, post):
        sub_dir = os.path.join(tmp_dir, f'subdir_{index}')
        if not os.path.exists(sub_dir):
            os.makedirs(sub_dir)
        
        copy_path = os.path.join(sub_dir, f'view_{channel}_{post}.py')
        with open("view.py", "r", encoding="utf-8") as original_file:
            with open(copy_path, "w", encoding="utf-8") as copy_file:
                copy_file.write(original_file.read())

        return copy_path, sub_dir

    def run_view_script(self, copy_path, sub_dir, channel, post):
        """Ejecuta el script de vista en un subproceso y lo almacena en la lista de procesos"""
        comando = [sys.executable, copy_path, '-c', channel, '-pt', str(post)]
        proc = subprocess.Popen(comando, cwd=sub_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        
        self.processes[(channel, post)] = proc
        self.data[(channel, post)] = {"success": 0, "fail": 0, "proxy_err": 0, "token_err": 0, "cookie_err": 0}

    def update_table(self):
        """Actualiza la tabla con los valores actuales (no acumulados)"""
        for item in self.tree.get_children():
            self.tree.delete(item)  
        for (channel, post), stats in self.data.items():
            self.tree.insert('', 'end', values=(
                channel,
                str(post),
                str(stats["success"]),
                str(stats["fail"]),
                str(stats["proxy_err"]),
                str(stats["token_err"]),
                str(stats["cookie_err"])
            ))

    def update_data(self):
        """Monitorea los procesos en ejecución y actualiza la tabla de estadísticas"""
        while True:
            for (channel, post), proc in list(self.processes.items()):
                if proc.poll() is not None:
                    # Si el proceso ha terminado, lo eliminamos de la lista
                    del self.processes[(channel, post)]
                    continue

                # Leer múltiples líneas para evitar bloqueos
                for line in iter(proc.stdout.readline, ''):
                    if line:
                        try:
                            status_update = json.loads(line.strip())

                            # **Reemplazamos los valores en lugar de sumarlos**
                            self.data[(channel, post)] = {
                                "success": status_update["success"],
                                "fail": status_update["fail"],
                                "proxy_err": status_update["proxy_err"],
                                "token_err": status_update["token_err"],
                                "cookie_err": status_update["cookie_err"]
                            }

                            self.update_table()
                        except json.JSONDecodeError:
                            continue

            time.sleep(1)  # Evita consumo excesivo de CPU
def open_url():
    url = "https://t.me/underbytes"
    subprocess.Popen(['cmd', '/c', 'start', url])

def iniciar_ejecucion():
    global is_running, link_index
    with lock:
        if is_running:
            return
        is_running = True
    links = [tree.item(item)['values'][0] for item in tree.get_children()]
    manager = Manager(tree_stats)
    for i, url in enumerate(links):
        try:
            parts = url.strip().split("/")
            if len(parts) >= 5 and parts[2] == "t.me":
                channel = parts[3]
                post = parts[4]
                
                copy_path, sub_dir = manager.create_view_copy(i, channel, post)
                manager.run_view_script(copy_path, sub_dir, channel, post)
                
                print(f"Ejecutando copia en {sub_dir} con -c {channel} -pt {post}...")

        except Exception as e:
            print(f"Error procesando la URL {url.strip()}: {e}")

    threading.Thread(target=manager.update_data, daemon=True).start()

def iniciar_ejecucion_en_hilo():

    threading.Thread(target=iniciar_ejecucion, daemon=True).start()

def detener_ejecucion():
    global is_running, processes
    with lock:
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
root.geometry("800x600")
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
frame_config.grid(row=0, column=0, sticky="ew", padx=10, pady=2)

entry_link = ctk.CTkEntry(frame_config, width=550)
entry_link.grid(row=0, column=3, padx=5, pady=2)  
btn_agregar = ctk.CTkButton(frame_config, text="Add Link", command=agregar_link, fg_color="#ba4a4a", hover_color="#953636")
btn_agregar.grid(row=0, column=4, padx=5, pady=2, sticky="e") 


frame_config.grid_columnconfigure(2, weight=1) 
frame_config.grid_columnconfigure(3, weight=0)  
frame_config.grid_columnconfigure(4, weight=1)  

frame_tabla = ctk.CTkFrame(root, fg_color="#262626")
frame_tabla.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

tree = ttk.Treeview(frame_tabla, columns=("LINKS"), show="headings", height=6)
tree.heading("LINKS", text="LINKS")
tree.column("LINKS", width=300, anchor="center", stretch=True) 

tree.pack(side="left", fill="both", expand=True)
style = ttk.Style()
style.configure("Treeview",
                background="white", 
                foreground="black", 
                rowheight=25,
                fieldbackground="white") 
style.map('Treeview',
          background=[('selected', 'black')],  
          foreground=[('selected', 'white')])  


frame_stats = ctk.CTkFrame(root, fg_color="#262626")
frame_stats.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)


tree_stats = ttk.Treeview(frame_stats, columns=("@", "👁‍🗨", "✅", "❌", "🔄", "🔑", "🍪"), show="headings", height=6)

for col in ("@", "👁‍🗨", "✅", "❌", "🔄", "🔑", "🍪"):
    tree_stats.heading(col, text=col)
    tree_stats.column(col, width=140, anchor="center", stretch=False)  
tree_stats.pack(side="left", fill="both", expand=True)

tree_stats.heading("@", text="@")
tree_stats.heading("👁‍🗨", text="👁‍🗨")
tree_stats.heading("✅", text="✅")
tree_stats.heading("❌", text="❌")
tree_stats.heading("🔄", text="🔄")
tree_stats.heading("🔑", text="🔑")
tree_stats.heading("🍪", text="🍪")
tree_stats.column("@", width=140, stretch=False)  
tree_stats.column("👁‍🗨", width=140, stretch=False)   
tree_stats.column("✅", width=140, stretch=False)   
tree_stats.column("❌", width=140, stretch=False)    
tree_stats.column("🔄", width=140, stretch=False)    
tree_stats.column("🔑", width=135, stretch=False)   
tree_stats.column("🍪", width=135, stretch=False)    
tree_stats.pack(side="left", fill="both", expand=True)
frame_botones = ctk.CTkFrame(root, fg_color="#262626")
frame_botones.grid(row=3, column=0, sticky="ew", padx=10, pady=2)  
btn_eliminar = ctk.CTkButton(frame_botones, text="Remove", command=eliminar_link, fg_color="#3A3A4D", hover_color="#953636")
btn_eliminar.grid(row=0, column=0, padx=(0, 5), pady=2, sticky="w")  
btn_iniciar = ctk.CTkButton(frame_botones, text="Start", command=iniciar_ejecucion_en_hilo, fg_color="#3A3A4D", hover_color="#276749")
btn_iniciar.grid(row=0, column=1, padx=5, pady=2) 
btn_detener = ctk.CTkButton(frame_botones, text="Stop", command=detener_ejecucion, fg_color="#3A3A4D", hover_color="#953636")
btn_detener.grid(row=0, column=2, padx=(5, 0), pady=2, sticky="e") 
frame_botones.grid_columnconfigure(0, weight=1)  
frame_botones.grid_columnconfigure(1, weight=0)  
frame_botones.grid_columnconfigure(2, weight=1) 

root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

root.mainloop()
