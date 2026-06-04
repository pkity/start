# -*- coding: utf-8 -*-
import json
import os
import time
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

COOKIE_PATH = "qyweixin_cookie.json"

def get_public_ip():
    ip_services = [
        "https://ip.sb",
        "https://ifconfig.me/ip",
        "https://api.ipify.org",
        "https://ipinfo.io/ip",
        "https://icanhazip.com",
    ]
    for service in ip_services:
        try:
            req = urllib.request.Request(service, headers={"User-Agent": "curl"})
            with urllib.request.urlopen(req, timeout=10) as response:
                ip = response.read().decode("utf-8").strip()
                print("✅ Public IP: {}".format(ip))
                return ip
        except:
            continue
    print("❌ Failed to get public IP")
    return None

def save_cookies(driver):
    cookies = driver.get_cookies()
    with open(COOKIE_PATH, "w", encoding="utf-8") as f:
        json.dump(cookies, f)

def load_cookies(driver):
    if not os.path.exists(COOKIE_PATH):
        return False
    try:
        driver.get("https://work.weixin.qq.com/")
        time.sleep(1)
        with open(COOKIE_PATH, encoding="utf-8") as f:
            cookies = json.load(f)
        driver.delete_all_cookies()
        for cookie in cookies:
            if 'sameSite' in cookie and cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
                cookie['sameSite'] = 'Lax'
            driver.add_cookie(cookie)
        return True
    except:
        return False

def update_qyweixin_app_trust_ip():
    options = Options()
    options.add_argument("--start-maximized")
    service = Service()
    driver = webdriver.Edge(service=service, options=options)
    wait = WebDriverWait(driver, 60)
    try:
        cookie_loaded = load_cookies(driver)
        if cookie_loaded:
            driver.get("https://work.weixin.qq.com/wework_admin/frame")
            time.sleep(1)
            if "login" in driver.current_url:
                print("🔑 Please scan QR code to login...")
                wait.until(EC.url_contains("wework_admin/frame"))
                save_cookies(driver)
        else:
            driver.get("https://work.weixin.qq.com/wework_admin/frame")
            print("🔑 Please scan QR code to login...")
            wait.until(EC.url_contains("wework_admin/frame"))
            save_cookies(driver)
        
    except Exception as e:
        print("❌ Error: {}".format(e))
    finally:
        time.sleep(1)
        driver.quit()

if __name__ == "__main__":
    update_qyweixin_app_trust_ip()
