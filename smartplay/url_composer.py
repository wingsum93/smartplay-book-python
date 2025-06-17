from urllib.parse import urlencode, quote
from typing import List

class SmartPlayURLComposer:
    BASE_URL = "https://www.smartplay.lcsd.gov.hk/facilities/search-result"

    def __init__(self, districts: List[str]):
        self.params = {
            "district": ",".join(districts[:5]),  # 最多五個地區代碼
            "startDate": "",
            "typeCode": "BADC",
            "venueCode": "",
            "sportCode": "BAGM",
            "typeName": "羽毛球",
            "frmFilterType": "",
            "venueSportCode": "",
            "isFree": "false"
        }

    def set_start_date(self, date_str: str):
        self.params["startDate"] = date_str

    def set_free_only(self, is_free: bool):
        self.params["isFree"] = "true" if is_free else "false"

    def set_type_name(self, type_name: str):
        self.params["typeName"] = type_name

    def compose_url(self) -> str:
        encoded = urlencode({k: v for k, v in self.params.items()}, quote_via=quote)
        return f"{self.BASE_URL}?{encoded}"


# 範例使用
if __name__ == "__main__":
    from smartplay.config import Config

    composer = SmartPlayURLComposer(Config.LOCATION_CODES)
    composer.set_start_date("2025-06-23")
    url = composer.compose_url()
    print(url)
