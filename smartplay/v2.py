import csv
import time
from datetime import date, timedelta, datetime
from urllib.parse import urlencode, quote
from playwright.sync_api import sync_playwright
from smartplay.page_handler import PageStateHandler
from smartplay.url_composer import VenuePageUrlBuilder
from smartplay.smartplay_page import SmartPlayPage
from smartplay.arena import Arena
from smartplay.config import Config
from smartplay.selector import Selector
from smartplay.queue_listener import OnQueuePageListener
from dotenv import load_dotenv
import random
import threading

load_dotenv()

AREA_CSV_PATH = "area_setting.csv"
URL = 'https://www.smartplay.lcsd.gov.hk/home?lang=tc'

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
def run_one_instance():
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            bypass_csp=True,
            java_script_enabled=True
        )
        page = context.new_page()

        smart_page = SmartPlayPage(page)
        smart_page.goto("https://www.smartplay.lcsd.gov.hk/home?lang=tc")
        

def main():
    wait_until_7am()  # <--- 👈 加呢句
    threads = []
    for _ in range(Config.PAGE_TAB):
        t = threading.Thread(target=run_one_instance)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
        
    wait_for_user_to_end()
    print("✅ Browser closed. Exiting program.")    
        
    
def post_logic_select_consecutive_slots(page, venue_name="N/A", prefer_start_hour=21)-> bool:
    print(f"🔍 Checking preferred timeslot ({prefer_start_hour}:00) for venue: {venue_name}")

    all_items = page.query_selector_all(Selector.sport_section)

    if len(all_items) != 16:
        print(f"❌ Expected 16 timeslots (07:00–22:00), but got {len(all_items)}. Skipping...")
        return False

    start_index = prefer_start_hour - 7  # index from 0~15 for 07:00–22:00

    if not (0 <= start_index <= 14):  # max allowed = 14 (for last pair 21:00 + 22:00)
        print(f"❌ Invalid prefer_start_hour: {prefer_start_hour}. Must be between 7 and 21.")
        return False

    try:
        current = all_items[start_index]
        next_slot = all_items[start_index + 1]
    except IndexError:
        print("❌ Not enough slots for a 2-hour window. Skipping...")
        return False

    has_curr = current.query_selector(Selector.have_area) is not None
    has_next = next_slot.query_selector(Selector.have_area) is not None

    if has_curr and has_next:
        current.click()
        next_slot.click()
        print(f"✅ Clicked timeslots at {prefer_start_hour}:00 and {prefer_start_hour+1}:00")

        next_button = page.get_by_role("button", name="繼續")
        if next_button:
            try:
                next_button.click()
            except Exception as e:
                print(f"⚠️ Timeout clicking '繼續': {e}")
        else:
            print("❌ 『繼續』按鈕不存在")
        return True  # 🎯 成功
    else:
        print(f"❌ Preferred slots at {prefer_start_hour}:00 not available (one or both unavailable)")
        return False
class PrintQueueListener(OnQueuePageListener):
    def onQueuePage(self, queue: int):
        print(f"🔔 Listener triggered: Current queue number is {queue}")            
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
