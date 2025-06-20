import csv

class Venue:
    def __init__(self, venue_id: int, fat_id: int, venue_name: str, district: str):
        self.venue_id = venue_id
        self.fat_id = fat_id
        self.venue_name = venue_name
        self.district = district

    def __repr__(self):
        return (f"Venue(venueId={self.venue_id}, fatId={self.fat_id}, "
                f"venueName='{self.venue_name}', district='{self.district}')")



class VenueRegistry:
    def __init__(self, csv_path: str):
        self.venues = {}  # key = venueId
        self.load_from_csv(csv_path)

    def load_from_csv(self, csv_path: str):
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    venue_id = int(row["venueId"])
                    fat_id = int(row["fatId"])
                    venue_name = row["venueName"]
                    district = row["district"]

                    venue = Venue(venue_id, fat_id, venue_name, district)
                    self.venues[venue_id] = venue
                except ValueError as e:
                    print(f"❌ Skip row due to error: {e} -> {row}")


    def get_by_id(self, venue_id: int) -> Venue:
        return self.venues.get(venue_id)


# ✅ Example usage
if __name__ == "__main__":
    registry = VenueRegistry("venues.csv")
    try:
        input_id = int(input("請輸入 venueId (數字): ").strip())
        venue = registry.get_by_id(input_id)
        if venue:
            print("✅ 查詢結果:", venue)
        else:
            print("⚠️ 找不到該場地。")
    except ValueError:
        print("❌ 請輸入正確的整數 venueId。")
