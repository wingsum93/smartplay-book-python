

class Config:
   LOCATION_CODES = ["KC", "YTM", "ST", ]  # 最多 5 個
   PREFER_NIGHT = True  # 偏好夜晚時段
   MUST_BOOK_2_HOUR = False
   START_DATE = "2025-06-26"  # 預設開始日期
   QUEUE_REMINDER = True  # 是否發音排隊狀態
   QUEUE_REMINDER_THRESHOLD = 4000  # 排隊人數小過此數量才提醒