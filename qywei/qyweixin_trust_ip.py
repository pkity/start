# -*- coding: utf-8 -*-
import json
import os
import time
import urllib.request
from playwright.sync_api import sync_playwright

COOKIE_PATH = "/mnt/quark/qyweixin/qyweixin_cookie.json"

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
                print("✅ Successfully obtained public IP: {} (via {})".format(ip, service))
                return ip
        except Exception as e:
            print("  {} failed: {}".format(service, e))
            continue
    print("❌ All IP services failed")
    return None

def save_cookies(context):
    cookies = context.cookies()
    with open(COOKIE_PATH, "w", encoding="utf-8") as f:
        json.dump(cookies, f)
    print("✅ Cookies saved")

def load_cookies(context, page):
    if not os.path.exists(COOKIE_PATH):
        return False
    try:
        page.goto("https://work.weixin.qq.com/")
        time.sleep(1)
        with open(COOKIE_PATH, encoding="utf-8") as f:
            cookies = json.load(f)
        context.add_cookies(cookies)
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
        page = context.new_page()
        try:
            cookie_loaded = load_cookies(context, page)
            if cookie_loaded:
                page.goto("https://work.weixin.qq.com/wework_admin/frame")
                time.sleep(1)
                if "login" not in page.url:
                    print("✅ Cookies loaded, entered WeChat Work admin panel")
                else:
                    print("🔑 Cookies expired, please scan QR code to login...")
                    page.wait_for_url("**/wework_admin/frame**", timeout=60000)
                    save_cookies(context)
            else:
                page.goto("https://work.weixin.qq.com/wework_admin/frame")
                print("🔑 Please scan QR code to login...")
                page.wait_for_url("**/wework_admin/frame**", timeout=60000)
                save_cookies(context)
            print("Entering app trusted IP settings...")
            page.goto("https://work.weixin.qq.com/wework_admin/frame#/apps/modApiApp/5629501431766533")
            print("✅ Located trusted IP configuration page, waiting for page load...")
            time.sleep(3)
            page.screenshot(path="/tmp/debug_page.png")
            print("📸 Screenshot saved to debug_page.png")

            try:
                print("Searching for the enterprise Trusted IP app card...")
                page.wait_for_selector("li.app_card .app_card_head_title", timeout=10000)

                page.screenshot(path="/tmp/debug_before_click.png")
                print("📸 Screenshot before click saved to debug_before_click.png")

                target_heading = page.locator("li.app_card .app_card_head_title:has-text('企业可信IP')").first
                if target_heading.count() == 0:
                    print("❌ No enterprise Trusted IP app card found")
                    return

                target_card = target_heading.locator('xpath=ancestor::li[contains(@class, "app_card")]').first
                setting_link = target_card.locator("a:has-text('配置'), button:has-text('配置'), a, button").first
                if setting_link.count() == 0:
                    print("❌ No configuration link/button found in enterprise Trusted IP card")
                    return

                print("✅ Found enterprise Trusted IP card and action link")
                print("Clicking configuration link...")
                setting_link.scroll_into_view_if_needed()
                time.sleep(0.5)
                try:
                    setting_link.click(timeout=10000)
                except Exception as e:
                    print("⚠️ Direct click failed, trying JS click: {}".format(e))
                    handle = setting_link.element_handle()
                    if handle:
                        page.evaluate("el => el.click()", handle)
                    else:
                        raise

                print("✅ Clicked configuration link, waiting for Trusted IP dialog...")
                try:
                    page.wait_for_selector('.app_ipConfig_dialog, .js_ipConfig_textarea', timeout=15000)
                except Exception as e:
                    print("⚠️ Trusted IP dialog did not appear immediately: {}".format(e))
                    page.wait_for_timeout(3000)

                public_ip = get_public_ip()
                if not public_ip:
                    print("❌ Unable to get public IP")
                    return

                print("Waiting for Trusted IP textarea...")
                time.sleep(2)
                page.screenshot(path="/tmp/debug_after_click.png")
                print("📸 Screenshot saved to debug_after_click.png")
                print("Current URL: {}".format(page.url))

                ip_input = page.locator('.js_ipConfig_textarea').first
                try:
                    ip_input.wait_for(timeout=10000)
                    print("✅ Found Trusted IP textarea")
                    ip_input.fill(public_ip)
                    print("✅ Filled IP: {}".format(public_ip))
                except Exception as e:
                    print("❌ Failed to find Trusted IP textarea: {}".format(e))
                    page.screenshot(path="/tmp/debug_no_ip_input.png")
                    return

                submit_button = page.locator('.js_ipConfig_confirmBtn').first
                if submit_button.count() > 0:
                    submit_button.click()
                    print("✅ Trusted IP updated successfully!")
                else:
                    print("❌ Confirm button not found in Trusted IP dialog")
                    page.screenshot(path="/tmp/debug_no_submit.png")
            except Exception as e:
                print("❌ Operation failed: {}".format(e))
                print("Current page URL: {}".format(page.url))
                print("Page title: {}".format(page.title()))
        except Exception as e:
            print("❌ Error occurred: {}".format(e))
        finally:
            time.sleep(1)
            browser.close()

if __name__ == "__main__":
    update_qyweixin_app_trust_ip()