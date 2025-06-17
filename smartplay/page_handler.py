from playwright.sync_api import Page
import os
import time
from smartplay.config import Config
from smartplay.selector import Selector
from dotenv import load_dotenv
load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

def is_unlogin_page(page: Page) -> bool:
    return page.query_selector(Selector.UN_LOGIN_TITLE) is not None

def is_loggedin_home_page(page: Page) -> bool:
    return page.query_selector(Selector.LOGIN_HOME_PAGE) is not None
    


def is_queue_page(page: Page) -> bool:
    return page.query_selector(Selector.QUEUE_PAGE) is not None  # customize as needed

def try_auto_login(page: Page, max_retries: int = 3):
    print("🔒 Unlogin page detected. Attempting to login...")
    attempts = 0
    while attempts < max_retries:
        page.fill('input[name="pc-login-username"]', USERNAME)
        page.fill('input[name="pc-login-password"]', PASSWORD)
        page.click('div[name="pc-login-btn"] div[role="button"]')
        page.wait_for_load_state('networkidle')

        # 檢查是否出現登入錯誤提示
        error_prompt = page.query_selector(Selector.DIALOG_FOR_RELOGIN)
        if error_prompt:
            print("⚠️ Login error detected. Retrying...")
            cancel_btn = page.query_selector(Selector.DIALOG_FOR_RELOGIN)
            if cancel_btn:
                cancel_btn.click()
            attempts += 1
            time.sleep(1)  # wait before retrying
        else:
            break
    else:
        print("❌ Failed to login after multiple attempts.")

def wait_for_queue_to_pass(page: Page, timeout: int = 1200):  # 20 minutes
    print("⏳ In queue... checking periodically if passed.")
    for _ in range(timeout):
        time.sleep(1)
        if is_loggedin_home_page(page):
            print("✅ Queue passed, now on home page.")
            return True
    print("❌ Still in queue after timeout.")
    return False

def click_night_section(page: Page):
    print("🌙 Clicking on 夜間 section...")
    night_section = page.query_selector('div.sp-tabs-scroll [tabindex]:nth-of-type(2)')
    if night_section:
        night_section.click()
        page.wait_for_load_state('networkidle')
        print("✅ Successfully clicked on 夜間 section.")
    else:
        print("❌ 夜間 section not found.")