from datetime import datetime
from smartplay.config import Config
from smartplay.selector import Selector
from smartplay.queue_listener import OnQueuePageListener
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta, date
import os
import random
from smartplay.url_composer import VenuePageUrlBuilder
from smartplay.arena import Arena
from smartplay.util import load_venue_settings
import time

class SmartPlayPage:
    def __init__(self, page, queue_listener: OnQueuePageListener = None):
        self._page = page  # 原始 Playwright Page 對象
        self.queue_listener = queue_listener
        
        dotenv_path = Path(__file__).parent.parent / ".env"
        load_dotenv(dotenv_path=dotenv_path, override=True)

        self.username = os.getenv("USERNAME")
        self.password = os.getenv("PASSWORD")

        if not self.username or not self.password:
            raise RuntimeError("⚠️ USERNAME or PASSWORD not found in .env")

    def goto(self, url: str, *, wait_until="domcontentloaded"):
        print(f"🌐 Visiting URL: {url}")
        # 🌀 自動處理 queue/login/home 狀態，直到到達主頁
        try:
            self._page.goto(url, wait_until=wait_until)

            while True:
                self._page.wait_for_load_state("domcontentloaded")

                if self.is_unlogin_page():
                    print("🔒 Detected login page")
                    self.try_auto_login()
                    time.sleep(1)
                    continue

                if self.is_queue_page():
                    print("🚧 Detected queue page")
                    queue_number = self._get_queue_number()
                    if self._queue_listener:
                        self._queue_listener.onQueuePage(queue_number)
                    self.wait_for_queue_to_pass()
                    time.sleep(1)
                    continue

                if self.is_loggedin_home_page():
                    print("🎉 Successfully reached home page.")
                    break

                print("🔁 Retrying page detection...")
                time.sleep(1)

            success = self.goto_all_venues("area_setting.csv", Config.START_TIME_IN_HOUR)
        except Exception as e:
            print(f"❌ Failed to visit {url}: {e}")
            raise
        
    def gotoAndDoThing(self, url: str, *, wait_until="domcontentloaded",screenshot_prefix=None, postLogic=None)-> bool:
        print(f"🌐 Visiting URL: {url}")
        try:
            self._page.goto(url, wait_until=wait_until)

            if screenshot_prefix:
                path = f"temp/{screenshot_prefix}_{datetime.now().strftime('%H%M%S')}.png"
                self._page.screenshot(path=path, full_page=True)
                print(f"🖼️ Screenshot saved: {path}")

            if postLogic:
                return postLogic(self._page)  # ⭐️ 改為有回傳

        except Exception as e:
            print(f"❌ Failed to visit {url}: {e}")
            raise
        return False  # 如果沒有 postLogic 或發生錯誤，返回 False
        
    def goto_all_venues(self, csv_path: str, prefer_start_hour: int) -> bool:
        venue_settings = load_venue_settings(csv_path)
        now = datetime.now()
        target_date = date.today() + timedelta(days=5 if now.hour < 7 else 6)
        print(f"🎯 Target date: {target_date}, Total venues: {len(venue_settings)}")

        for arena in venue_settings:
            builder = VenuePageUrlBuilder(
                venue_id=arena.venue_id,
                venue_name=arena.venue_name,
                district=arena.district,
                fat_id=arena.fat_id,
                play_date=target_date
            )
            arena_url = builder.build_url()

            print(f"🏸 Trying venue: {arena.venue_name} ({arena_url})")
            success = self.gotoAndDoThing(
                arena_url,
                wait_until="networkidle",
                screenshot_prefix=arena.venue_name,
                postLogic=lambda p: self._post_logic_select_consecutive_slots(p, arena.venue_name, prefer_start_hour)
            )

            if success:
                print(f"🎉 Booking success at {arena.venue_name}, stopping loop.")
                return True

            time.sleep(random.uniform(0.2, 0.5))

        print("❌ Booking failed at all venues.")
        return False
    def _post_logic_select_consecutive_slots(self, page, venue_name="N/A", prefer_start_hour=21) -> bool:
        print(f"🔍 Checking preferred timeslot ({prefer_start_hour}:00) for venue: {venue_name}")
        all_items = page.query_selector_all(Selector.sport_section)

        if len(all_items) != 16:
            print(f"❌ Expected 16 timeslots, but got {len(all_items)}. Skipping...")
            return False

        start_index = prefer_start_hour - 7
        if not (0 <= start_index <= 14):
            print(f"❌ Invalid hour: {prefer_start_hour}")
            return False

        try:
            curr = all_items[start_index]
            next_slot = all_items[start_index + 1]
            has_curr = curr.query_selector(Selector.have_area) is not None
            has_next = next_slot.query_selector(Selector.have_area) is not None

            if has_curr and has_next:
                curr.click()
                next_slot.click()
                print(f"✅ Clicked slots: {prefer_start_hour}:00 and {prefer_start_hour+1}:00")

                next_button = page.get_by_role("button", name="繼續")
                if next_button:
                    next_button.click()
                else:
                    print("❌ 『繼續』按鈕不存在")
                return True
            else:
                print("❌ Preferred slots not available.")
                return False
        except Exception as e:
            print(f"❌ Exception in post logic: {e}")
            return False
    # --- ✅ Page State Handler 部分 ---
    def is_unlogin_page(self) -> bool:
        return self._page.get_by_text("登入", exact=True).is_visible()

    def is_loggedin_home_page(self) -> bool:
        return self._page.query_selector(Selector.LOGIN_HOME_PAGE) is not None

    def is_queue_page(self) -> bool:
        return self._page.query_selector(Selector.QUEUE_PAGE) is not None

    def try_auto_login(self, max_retries: int = 3):
        print("🔒 Attempting login...")
        for attempt in range(max_retries):
            if not self.is_unlogin_page():
                return
            self._page.fill('input[name="pc-login-username"]', self.username)
            self._page.fill('input[name="pc-login-password"]', self.password)
            self._page.click('div[name="pc-login-btn"] div[role="button"]')
            self._page.wait_for_load_state('networkidle')

            error_prompt = self._page.query_selector(Selector.DIALOG_FOR_RELOGIN)
            if error_prompt:
                print("⚠️ Login error. Retrying...")
                error_prompt.click()
                time.sleep(1)
            else:
                break
        else:
            print("❌ Failed to login after retries.")

    def wait_for_queue_to_pass(self):
        print("⏳ Waiting in queue...")
        while self.is_queue_page():
            queue_num = self._get_queue_number()
            print(f"🔢 Queue number: {queue_num}", end='\r')
            time.sleep(1)
        print("✅ Queue passed.")
        
    def _get_queue_number(self) -> int:
        try:
            el = self._page.query_selector(Selector.QUEUE_NUMBER)
            text = el.inner_text().strip() if el else "0"
            return int(text)
        except:
            return 0

    def __getattr__(self, item):
        # 自動代理所有未定義屬性到原生 Page 對象
        return getattr(self._page, item)
