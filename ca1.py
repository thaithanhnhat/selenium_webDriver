import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
from multiprocessing import Process
import zipfile
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Danh sách user agent cho iPhone
IPHONE_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
]

# Danh sách proxy
PROXY_LIST = [
    "45.251.61.175:6893:fnrbjjbf:smfqbs91u00f",
    "216.173.74.150:5830:fnrbjjbf:smfqbs91u00f",
    "193.42.224.108:6309:fnrbjjbf:smfqbs91u00f",
    "206.41.175.159:6372:fnrbjjbf:smfqbs91u00f",
    "171.22.249.177:5757:fnrbjjbf:smfqbs91u00f",
    "171.22.249.110:5690:fnrbjjbf:smfqbs91u00f",
    "206.41.175.224:6437:fnrbjjbf:smfqbs91u00f",
    "216.173.74.136:5816:fnrbjjbf:smfqbs91u00f"
]

def get_nameFolder():
    folder_path = "D:\\Tdata_run\\Alltdata\\Tdata_1"
    subfolders = [f.name for f in os.scandir(folder_path) if f.is_dir()]
    return subfolders

def create_profile():
    for name in get_nameFolder():
        profile_dir = os.path.join(os.getcwd(), "D:\\Tdata_run\\AllProfile\\Profile_1", name)
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)

def get_plugin(proxy_host, proxy_port, proxy_user, proxy_pass, profile_name):
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = f"""
    var config = {{
        mode: "fixed_servers",
        rules: {{
            singleProxy: {{
                scheme: "http",
                host: "{proxy_host}",
                port: parseInt({proxy_port})
            }},
            bypassList: ["localhost"]
        }}
    }};

    chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

    function callbackFn(details) {{
        return {{
            authCredentials: {{
                username: "{proxy_user}",
                password: "{proxy_pass}"
            }}
        }};
    }}

    chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        {{urls: ["<all_urls>"]}},
        ['blocking']
    );
    """

    # Tạo thư mục cho plugin của profile
    plugin_dir = os.path.join(os.getcwd(), "proxy_plugins", profile_name)
    os.makedirs(plugin_dir, exist_ok=True)

    pluginfile = os.path.join(plugin_dir, 'proxy_auth_plugin.zip')
    
    with zipfile.ZipFile(pluginfile, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    return pluginfile

def run_profile(name, user_agent, proxy):
    proxy_parts = proxy.split(":")
    proxy_host = proxy_parts[0]
    proxy_port = proxy_parts[1]
    proxy_user = proxy_parts[2]
    proxy_pass = proxy_parts[3]
    extensions = [
        #"Extention/bypass.crx",
        "Extention/Ignore-X-Frame-headers.crx",
        #"Extention/getIframe.crx"
        "Extention/getQuery.crx"
        #"Extention/violentmonkey.crx"
    ]
    
    profile_dir = os.path.join(os.getcwd(), "D:\\Tdata_run\\AllProfile\\Profile_1", name)
    options = Options()
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument(f"user-data-dir={profile_dir}")
    options.add_argument("--force-device-scale-factor=0.8")
    options.add_argument('--disable-ipv6')
    for extension in extensions:
        options.add_extension(extension)
    # Thêm plugin proxy
    plugin_file = get_plugin(proxy_host, proxy_port, proxy_user, proxy_pass, name)
    options.add_extension(plugin_file)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(300, 700)

    with open('refGame_noquery\linkref.txt', 'r') as file:
        lines = file.readlines()

    lines = [line.strip() for line in lines]
    driver.get(lines[0])
    
    wait = WebDriverWait(driver, 999999)  
    openweb = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//a[span[text()="Open in Web"]]'))
    )
    openweb.click()
    try:
        luanch = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//button[span[text()="Launch"]]'))
        )
        luanch.click()
    finally:
        time.sleep(299999)
    time.sleep(9999)
    driver.quit()

if __name__ == "__main__":
    create_profile()
    processes = []
    user_agents = IPHONE_USER_AGENTS

    # Bắt đầu các process với proxy riêng
    for i, name in enumerate(get_nameFolder()):
        if i < len(user_agents) and i < len(PROXY_LIST):
            logging.info(f"Starting profile '{name}' with proxy: {PROXY_LIST[i]}")
            process = Process(target=run_profile, args=(name, user_agents[i], PROXY_LIST[i]))
            processes.append(process)
            process.start()

    for process in processes:
        process.join()
