from playwright.sync_api import sync_playwright, expect
from smartplay.page_handler import PageStateHandler
from smartplay.config import Config
from smartplay.url_composer import SmartPlayURLComposer, VenuePageUrlBuilder
from dotenv import load_dotenv

import json
import time
from datetime import datetime, timedelta
import random

URL = 'https://www.smartplay.lcsd.gov.hk/home?lang=tc'

composer = SmartPlayURLComposer(Config.LOCATION_CODES)
composer.set_start_date(Config.START_DATE)

def wait_until_7am():
    now = datetime.now()
    target = now.replace(hour=7, minute=0, second=0, microsecond=0)

    # 如果已經過咗 7am，就唔等
    if now >= target:
        return

    # 只係 6:45am ~ 7:00am 才等
    if now.hour == 6 and now.minute >= 45:
        print(f"⏳ Waiting until 7:00:00 AM... current time: {now.strftime('%H:%M:%S')}")
        while datetime.now() < target:
            time.sleep(0.2)  # sleep 200ms
            print(f"⏳ Current time: {datetime.now().strftime('%H:%M:%S')}", end='\r')
        print("✅ Reached 7:00:00 AM")
        
def main():
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False, slow_mo=150)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            bypass_csp=True,
            java_script_enabled=True
        )

        page = context.new_page()
        handler = PageStateHandler(page)
        page.goto(URL)
        page.wait_for_load_state('domcontentloaded')
        
        wait_until_7am()
        # 登入流程 + 排隊流程整理成 while loop，直到成功進入主頁為止
        while True:
            if handler.is_queue_page():
                page.screenshot(path="temp/queue.png", full_page=True)
                handler.wait_for_queue_to_pass()
                time.sleep(random.uniform(1, 2))  # human-like delay
                continue  # retry 檢查頁面狀態
            
            if handler.is_unlogin_page():
                page.screenshot(path="temp/login.png", full_page=True)
                handler.try_auto_login()
                time.sleep(random.uniform(1, 2))  # human-like delay
                continue  # retry 檢查頁面狀態

            if handler.is_loggedin_home_page():
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
        have_preferred_time = False
        if not Config.PREFER_NIGHT:
            handler.click_afternoon_section()
            handler.has_two_consecutive_enabled_slots()
            handler.click_night_section()
            handler.has_two_consecutive_enabled_slots()
        else:
            handler.click_night_section()
            handler.has_two_consecutive_enabled_slots()
            handler.click_afternoon_section()
            handler.has_two_consecutive_enabled_slots()
        
        page.screenshot(path="temp/booking_page_2.png", full_page=True)
        
        wait_for_user_to_end()
        print("✅ Browser closed. Exiting program.")
        browser.close()
        
def wait_for_user_to_end():
    while True:
        user_input = input("🔸 Type 'end' to exit browser: ")
        if user_input.strip() == "end":
            print("👋 'end' received. Closing browser...")
            break
        else:
            print("❌ Invalid input. Please type exactly: end")

if __name__ == '__main__':
    main()
