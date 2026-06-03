# -*- coding: utf-8 -*-
import json
import os
import time
import urllib.request
from playwright.sync_api import sync_playwright

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
                print("Searching for Company's Trusted IP settings link...")
                page.wait_for_selector("[class*='card']", timeout=10000)

                page.screenshot(path="/tmp/debug_before_click.png")
                print("📸 Screenshot before click saved to debug_before_click.png")

                cards = page.locator("[class*='card']").all()
                print("Found {} card(s) total".format(len(cards)))

                target_card = None
                for idx, card in enumerate(cards):
                    try:
                        card_text = card.inner_text()
                        print("Card {}: {}".format(idx, card_text[:100]))
                        if '企业可信IP' in card_text or '企业IP' in card_text or ('可信IP' in card_text and '设置' in card_text):
                            target_card = card
                            print("✅ Found Trusted IP card at index {}".format(idx))
                            break
                    except Exception as e:
                        print("Error reading card {}: {}".format(idx, e))
                        continue

                if not target_card:
                    print("❌ No card found with Trusted IP text")
                    return

                setting_link = target_card.locator("a:has-text('设置'), button:has-text('设置'), [class*='setting']").first
                if setting_link.count() == 0:
                    setting_link = target_card.locator("[class*='operationLink'], a, button").first
                print("✅ Found settings link")
                print("Clicking settings link...")
                setting_link.scroll_into_view_if_needed()
                time.sleep(0.5)
                setting_link.click()
                print("✅ Clicked settings link, waiting for content to load...")
                page.wait_for_load_state("networkidle", timeout=10000)
                public_ip = get_public_ip()
                if not public_ip:
                    print("❌ Unable to get public IP")
                    return

                print("Waiting for IP input field...")
                time.sleep(2)
                page.screenshot(path="/tmp/debug_after_click.png")
                print("📸 Screenshot saved to debug_after_click.png")
                print("Current URL: {}".format(page.url))

                input_elements = page.locator('input, textarea').all()
                print("Found {} input/textarea elements".format(len(input_elements)))
                for i, elem in enumerate(input_elements):
                    try:
                        tag = elem.evaluate("el => el.tagName")
                        elem_type = elem.evaluate("el => el.type || ''")
                        placeholder = elem.evaluate("el => el.placeholder || ''")
                        name = elem.evaluate("el => el.name || ''")
                        print("  Element {}: tag={}, type={}, placeholder={}, name={}".format(i, tag, elem_type, placeholder, name))
                    except:
                        pass

                try:
                    ip_input = page.locator('textarea, input[type="text"]').first
                    ip_input.wait_for(timeout=10000)
                    print("✅ Found input field")
                    ip_input.fill(public_ip)
                    print("✅ Filled IP: {}".format(public_ip))
                except Exception as e:
                    print("❌ Failed to find textarea: {}".format(e))
                    return

                submit_button = page.locator('[d_ck="submit"]').first
                if submit_button.count() > 0:
                    submit_button.click()
                    print("✅ Trusted IP updated successfully!")
                else:
                    print("❌ Submit button not found")
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