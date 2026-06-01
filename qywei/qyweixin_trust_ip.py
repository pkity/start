# -*- coding: utf-8 -*-
import json
import os
import time
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from playwright.sync_api import sync_playwright
import time

COOKIE_PATH = "qyweixin_cookie.json"

def get_public_ip():
    """Get the public IP of current device"""
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
                print("✅ Successfully obtained public IP: {} (via {})".format(ip, service))
                return ip
        except Exception as e:
            print("  {} failed: {}".format(service, e))
            continue
    print("❌ All IP services failed")
    return None

def save_cookies(driver):
    """Save cookies to file"""
    cookies = driver.get_cookies()
    with open(COOKIE_PATH, "w", encoding="utf-8") as f:
        json.dump(cookies, f)
    print("✅ Cookies saved")

def load_cookies(driver):
    """Load cookies from file"""
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
        print("✅ Cookies loaded successfully!")
        return True
    except Exception as e:
        print("❌ Failed to load cookies: {}".format(e))
        return False

def update_qyweixin_app_trust_ip():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        )
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        driver = context.new_page()
        wait = WebDriverWait(driver, 60)
        try:
            cookie_loaded = load_cookies(driver)
            if cookie_loaded:
                driver.get("https://work.weixin.qq.com/wework_admin/frame")
                time.sleep(1)
                if "login" not in driver.current_url:
                    print("✅ Cookies loaded, entered WeChat Work admin panel")
                else:
                    print("🔑 Cookies expired, please scan QR code to login...")
                    wait.until(EC.url_contains("wework_admin/frame"))
                    save_cookies(driver)
            else:
                driver.get("https://work.weixin.qq.com/wework_admin/frame")
                print("🔑 Please scan QR code to login...")
                wait.until(EC.url_contains("wework_admin/frame"))
                save_cookies(driver)
            print("Entering app trusted IP settings...")
            driver.get("https://work.weixin.qq.com/wework_admin/frame#/apps/modApiApp/5629501431766533")
            print("✅ Located trusted IP configuration page, waiting for page load...")
            time.sleep(1)  # Wait for page to fully load

            try:
                print("Searching for Company's Trusted IP settings link...")
                # Try multiple selectors
                cards = driver.find_elements(By.CLASS_NAME, "app_card")
                if not cards:
                    print("Trying alternative selectors...")
                    cards = driver.find_elements(By.CSS_SELECTOR, "[class*='card']")
                if not cards:
                    cards = driver.find_elements(By.CSS_SELECTOR, "[class*='Card']")
                target_card = None
                for card in cards:
                    try:
                        title_elem = card.find_element(By.CLASS_NAME, "app_card_head_title")
                        if "Company's Trusted IP" in title_elem.text or "Trusted IP" in title_elem.text:
                            target_card = card
                            print("✅ Found Company's Trusted IP card")
                            break
                    except Exception as e:
                        continue
                if not target_card:
                    print("❌ Company's Trusted IP card not found")
                    return
                setting_link = target_card.find_element(By.CLASS_NAME, "apiApp_mod_card_operationLink")
                print("✅ Found settings link")
                print("Clicking settings link...")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", setting_link)
                driver.execute_script("arguments[0].click();", setting_link)
                print("✅ Clicked settings link, waiting for content to load...")
                public_ip = get_public_ip()
                if not public_ip:
                    print("❌ Unable to get public IP")
                    return
                ip_textarea = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea[placeholder*="Trusted IP"]'))
                )
                ip_textarea.clear()
                ip_textarea.send_keys(public_ip)
                submit_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[d_ck="submit"]'))
                )
                submit_button.click()
                print("✅ Trusted IP updated successfully!")
            except Exception as e:
                print("❌ Operation failed: {}".format(e))
                print("Current page URL: {}".format(driver.current_url))
                print("Page title: {}".format(driver.title))
        except Exception as e:
            print("❌ Error occurred: {}".format(e))
        finally:
            time.sleep(1)
            driver.quit()

if __name__ == "__main__":
    update_qyweixin_app_trust_ip()
