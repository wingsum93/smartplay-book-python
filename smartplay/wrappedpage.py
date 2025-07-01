from datetime import datetime
from smartplay.config import Config
from smartplay.selector import Selector
import time

class WrappedPage:
    def __init__(self, page, handler):
        self.page = page
        self.handler = handler

    def goto(self, url: str, *, wait_until="domcontentloaded", screenshot_prefix=None, postLogic=None)-> bool:
        print(f"🌐 Visiting URL: {url}")
        try:
            self.page.goto(url, wait_until=wait_until)

            if screenshot_prefix:
                path = f"temp/{screenshot_prefix}_{datetime.now().strftime('%H%M%S')}.png"
                self.page.screenshot(path=path, full_page=True)
                print(f"🖼️ Screenshot saved: {path}")

            if postLogic:
                return postLogic(self.page)  # ⭐️ 改為有回傳

        except Exception as e:
            print(f"❌ Failed to visit {url}: {e}")
            raise

    def __getattr__(self, name):
        return getattr(self.page, name)
