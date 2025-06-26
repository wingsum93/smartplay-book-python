from urllib.parse import urlencode, quote
from typing import List
from datetime import date

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

class VenuePageUrlBuilder:
    BASE_URL = "https://www.smartplay.lcsd.gov.hk/facilities/select/court"

    def __init__(self, venue_id: str, venue_name: str,district:str, fat_id:int, play_date: date):
        self.venue_id = venue_id
        self.venue_name = venue_name
        self.district = district
        self.fat_id = fat_id
        self.play_date = play_date

        # Static parameters
        self.date_index = 0
        self.sessionIndex = 2 # 預設時段索引 1 / 2
        self.type_code = "BADC"
        self.sport_code = "BAGM"
        self.frm_filter_type = ""
        self.is_free = "false"

    def build_url(self) -> str:
        query_params = {
            "venueId": self.venue_id,
            "fatId": self.fat_id,
            "venueName": self.venue_name,
            "sessionIndex": str(self.sessionIndex),
            "dateIndex": str(self.date_index),
            "playDate": self.play_date.strftime("%Y-%m-%d"),
            "district": self.district,
            "typeCode": self.type_code,
            "sportCode": self.sport_code,
            "frmFilterType": self.frm_filter_type,
            "isFree": self.is_free
        }

        encoded_params = urlencode(query_params, quote_via=quote)
        return f"{self.BASE_URL}?{encoded_params}"
    
# 範例使用
if __name__ == "__main__":
    from smartplay.config import Config

    composer = SmartPlayURLComposer(Config.LOCATION_CODES)
    composer.set_start_date("2025-06-23")
    url = composer.compose_url()
    print(url)
