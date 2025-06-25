import csv
import time
from datetime import date, timedelta, datetime
from urllib.parse import urlencode, quote
from playwright.sync_api import sync_playwright
from smartplay.page_handler import PageStateHandler
from smartplay.url_composer import VenuePageUrlBuilder
from smartplay.config import Config
from smartplay.selector import Selector
from dotenv import load_dotenv

load_dotenv()

AREA_CSV_PATH = "area_setting.csv"
URL = 'https://www.smartplay.lcsd.gov.hk/home?lang=tc'


def load_venue_settings(csv_path):
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [row for row in reader if row.get('venueId') and row.get('venueName') and row.get('district')]

def main():
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False, slow_mo=200)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            bypass_csp=True,
            java_script_enabled=True
        )

        page = context.new_page()
        handler = PageStateHandler(page)

        # 登入與排隊流程
        while True:
            page.goto(URL)
            page.wait_for_load_state('domcontentloaded')

            if handler.is_unlogin_page():
                handler.try_auto_login()
                time.sleep(1)
                continue

            if handler.is_queue_page():
                handler.wait_for_queue_to_pass()
                time.sleep(1)
                continue

            if handler.is_loggedin_home_page():
                print("🎉 Successfully reached home page.")
                break

            print("🔁 Retrying page detection...")
            time.sleep(1)

        # 載入場館資料並組成網址
        venue_settings = load_venue_settings(AREA_CSV_PATH)
        now = datetime.now()
        target_date = date.today() + timedelta(days=5 if now.hour < 7 else 6)



        for venue in venue_settings:
            builder = VenuePageUrlBuilder(
                venue_id=venue['venueId'],
                venue_name=venue['venueName'],
                district=venue['district'],
                play_date=target_date
            )
            arena_url = builder.build_url()
            print(f"➡️ Visiting arena: {arena_url}")
            page.goto(arena_url)
            page.wait_for_load_state('domcontentloaded')
            page.click(Selector.the_day_selection)  
            page.wait_for_selector(Selector.sport_section, timeout=10000)  # 等待主元素出現
            page.screenshot(path=f"temp/arena_{venue['venueName']}.png", full_page=True)
            
            # 1. 選取全部 16 個主元素
            all_items = page.query_selector_all(Selector.sport_section)  # 換成你真實嘅 selector
            if len(all_items) < 7:
                print("元素數量不足, abnormal page structure.")
                return

            # 2. 從尾向前 loop（但跳過頭 5 個）
            found = False
            for i in range(len(all_items)-1, 4, -1):  # index 5 開始，逆向
                current = all_items[i]
                prev = all_items[i-1]

                has_span_curr = current.query_selector(Selector.have_area) is not None
                has_span_prev = prev.query_selector(Selector.have_area) is not None

                if has_span_curr and has_span_prev:
                    # click 兩個元素
                    prev.click()
                    current.click()
                    print(f"Clicked on index: {i-1} and {i}")

                    # click 下一頁
                    next_button = page.get_by_role("button", name="繼續")  # 換成實際按鈕 selector
                    if next_button:
                        try:
                            next_button.click()
                        except Exception as e:
                            print(f"Timeout while clicking '繼續' button: {e}")
                    else:
                        print("無找到『繼續』按鈕")
                    found = True
                    break
            if not found:
                print(f"{venue['venueName']}, 無找到兩個連續場")
            

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
