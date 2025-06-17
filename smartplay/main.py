from playwright.sync_api import sync_playwright, expect
from smartplay.page_handler import is_unlogin_page, is_loggedin_home_page, is_queue_page, try_auto_login, wait_for_queue_to_pass
from smartplay.config import Config
from smartplay.url_composer import SmartPlayURLComposer
from dotenv import load_dotenv

import os
import json
import time
import random

# Load environment variables
load_dotenv()

URL = 'https://www.smartplay.lcsd.gov.hk/home?lang=tc'

composer = SmartPlayURLComposer(Config.LOCATION_CODES)
composer.set_start_date("2025-06-23")

def main():
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False, slow_mo=200)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            bypass_csp=True,
            java_script_enabled=True
        )

        page = context.new_page()

        # 登入流程 + 排隊流程整理成 while loop，直到成功進入主頁為止
        while True:
            page.goto(URL)
            page.wait_for_load_state('domcontentloaded')

            if is_unlogin_page(page):
                page.screenshot(path="temp/login.png", full_page=True)
                try_auto_login(page)
                time.sleep(random.uniform(1, 2))  # human-like delay
                continue  # retry 檢查頁面狀態

            if is_queue_page(page):
                page.screenshot(path="temp/queue.png", full_page=True)
                wait_for_queue_to_pass(page)
                time.sleep(random.uniform(1, 2))  # human-like delay
                continue  # retry 檢查頁面狀態

            if is_loggedin_home_page(page):
                page.screenshot(path="temp/home.png", full_page=True)
                print("🎉 Successfully entered home page!")
                break
            
            print("🔁 Still not on home page, retrying...")
            time.sleep(random.uniform(1, 2))  # human-like delay before retry

        # 成功登入後前往目標場地預約頁
        booking_url = composer.compose_url()
        print("🔗 Navigating to booking URL:", booking_url)
        page.goto(booking_url)
        page.wait_for_load_state('networkidle')
        page.screenshot(path="temp/booking_page.png", full_page=True)

        # 這裡可以加上場地篩選邏輯
        page.pause()

if __name__ == '__main__':
    main()
