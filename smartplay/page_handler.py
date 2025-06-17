from playwright.sync_api import Page
import os
import time
from smartplay.config import Config
from smartplay.selector import Selector
from dotenv import load_dotenv

load_dotenv()

class PageStateHandler:
    def __init__(self, page: Page):
        self.page = page
        self.username = os.getenv("USERNAME")
        self.password = os.getenv("PASSWORD")

    def is_unlogin_page(self) -> bool:
        return self.page.get_by_text("登入", exact=True).is_visible()

    def is_loggedin_home_page(self) -> bool:
        return self.page.query_selector(Selector.LOGIN_HOME_PAGE) is not None

    def is_queue_page(self) -> bool:
        return self.page.query_selector(Selector.QUEUE_PAGE) is not None

    def try_auto_login(self, max_retries: int = 3):
        print("🔒 Unlogin page detected. Attempting to login...")
        attempts = 0
        while attempts < max_retries:
            if not self.is_unlogin_page():
                return
            self.page.fill('input[name="pc-login-username"]', self.username)
            self.page.fill('input[name="pc-login-password"]', self.password)
            self.page.click('div[name="pc-login-btn"] div[role="button"]')
            self.page.wait_for_load_state('networkidle')

            error_prompt = self.page.query_selector(Selector.DIALOG_FOR_RELOGIN)
            if error_prompt:
                print("⚠️ Login error detected. Retrying...")
                cancel_btn = self.page.query_selector(Selector.DIALOG_FOR_RELOGIN)
                if cancel_btn:
                    cancel_btn.click()
                attempts += 1
                time.sleep(1)
            else:
                break
        else:
            print("❌ Failed to login after multiple attempts.")

    def wait_for_queue_to_pass(self):
        print("⏳ In queue... checking periodically if passed.")
        while True:
            time.sleep(1)
            ## check how much people in queue
            queue_element = self.page.query_selector(Selector.QUEUE_NUMBER)
            queue_element_text = queue_element.inner_text().strip() if queue_element else "0"
            try:
                queue_number = int(queue_element_text)
            except ValueError:
                queue_number = 0
            print(f"🔢 Current queue number: {queue_number}")
            if self.is_loggedin_home_page():
                print("✅ Queue passed, now on home page.")
                return

    def click_night_section(self):
        print("🌙 Clicking on 夜間 section...")
        night_section = self.page.query_selector('div.sp-tabs-scroll [tabindex]:nth-of-type(3)')
        if night_section:
            night_section.click()
            self.page.wait_for_load_state('networkidle')
            print("✅ Successfully clicked on 夜間 section.")
        else:
            print("❌ 夜間 section not found.")

    def click_afternoon_section(self):
        print("🌞 Clicking on 下午 section...")
        afternoon_section = self.page.query_selector('div.sp-tabs-scroll [tabindex]:nth-of-type(2)')
        if afternoon_section:
            afternoon_section.click()
            self.page.wait_for_load_state('networkidle')
            print("✅ Successfully clicked on 下午 section.")
        else:
            print("❌ 下午 section not found.")
            
    def has_two_consecutive_timeslots(self) -> bool:
        print("🔍 Checking for two consecutive available timeslots...")
        timeslot_elements = self.page.query_selector_all('.time-slot.available')

        times = []
        for slot in timeslot_elements:
            time_text = slot.inner_text().strip()
            if time_text:
                try:
                    hours, minutes = map(int, time_text.split(":"))
                    total_minutes = hours * 60 + minutes
                    times.append(total_minutes)
                except:
                    continue

        times.sort()

        for i in range(len(times) - 1):
            if times[i+1] - times[i] == 30:
                print("✅ Found consecutive timeslots.")
                return True

        print("❌ No consecutive timeslots available.")
        return False
    
    def has_two_consecutive_enabled_slots(self) -> bool:
        # 先選出所有目標元素 in select time slot page
        all_elements = self.page.query_selector_all("div.facilities-date-list-scroll div.facilities-date-list-item div.relative")

        # 跳過前 7 個元素
        elements_to_check = all_elements[7:]

        # 抽出 enabled 嘅 index
        enabled_indexes = []
        for i, el in enumerate(elements_to_check):
            class_name = el.get_attribute("class") or ""
            if "item-num-box" in class_name and "item-num-box-disable" not in class_name:
                enabled_indexes.append(i)

        # 檢查有無 index[i+1] == index[i] + 1，代表有兩個連續
        for i in range(len(enabled_indexes) - 1):
            if enabled_indexes[i + 1] == enabled_indexes[i] + 1:
                print("✅ Found two consecutive enabled slots.")
                elements_to_check[enabled_indexes[i]].click()
                ## go to booking confirm page
                return True
        print("❌ No two consecutive enabled slots found.")
        return False
    
    
    # relative tag session-tag-box-select
    
