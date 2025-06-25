from playwright.sync_api import sync_playwright
from smartplay.selector import Selector
import time

def run():
    playDate= "2025-06-30"  # 👈 你想要的日期
    venueName= "紅磡市政大廈體育館"
    venueId= "224"  # 👈 你想要的場地 ID
    district= "KC"  # 👈 你想要的地區代碼
    fatId= 504
    TEMP_URL = f'https://www.smartplay.lcsd.gov.hk/facilities/select/court?venueId={venueId}&fatId={fatId}&venueName={venueName}&sessionIndex=0&dateIndex=0&playDate={playDate}&district={district}&typeCode=BADC&sportCode=BAGM&frmFilterType=&isFree=false'
    
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False, slow_mo=150)  # 開啟實體視窗方便 debug
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            bypass_csp=True,
            java_script_enabled=True
        )
        page = context.new_page()
        print(f"🔗 Opening URL: {TEMP_URL}")
        page.goto(TEMP_URL,wait_until="domcontentloaded")  # 👈 你嘅目標網址
        page.wait_for_timeout(9000)
        # 1. 選取全部 16 個主元素
        all_items = page.query_selector_all(Selector.sport_section)  # 換成你真實嘅 selector
        if len(all_items) < 7:
            print("元素數量不足")
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
                    next_button.click()
                else:
                    print("無找到『繼續』按鈕")
                found = True
                break

        if not found:
            print("無找到兩個連續場")

        wait_for_user_to_end()

def wait_for_user_to_end():
    while True:
        user_input = input("🔸 Type 'end' to exit browser: ")
        if user_input.strip() == "end":
            print("👋 'end' received. Closing browser...")
            break
        else:
            print("❌ Invalid input. Please type exactly: end")
            
if __name__ == "__main__":
    run()
