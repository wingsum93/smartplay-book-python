from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def run_scraper():
    options = Options()
    
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # 防止 navigator.webdriver = true
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """
    })

    url = 'https://www.smartplay.lcsd.gov.hk/home?lang=tc'  # 更換成你需要爬的頁面
    driver.get(url)

    print(driver.current_url)
    print(driver.page_source[:500])  # print 前 500 個字元


    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "#login"))
    )

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    items = soup.select('.fp-item-content')

    for item in items:
        print(item.text.strip())

    driver.quit()

if __name__ == "__main__":
    run_scraper()
