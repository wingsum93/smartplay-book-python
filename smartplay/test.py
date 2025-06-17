from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time

def main():
    options = Options()
    options.set_preference("dom.webdriver.enabled", False)  # 嘗試隱藏自動化
    options.set_preference("useAutomationExtension", False)

    driver = webdriver.Firefox(options=options)
    driver.get("https://www.smartplay.lcsd.gov.hk/home?lang=tc")
    time.sleep(5)
    print("Title:", driver.title)
    driver.save_screenshot("smartplay_firefox_selenium.png")

    input("👀 Press Enter to close...")
    driver.quit()

main()
