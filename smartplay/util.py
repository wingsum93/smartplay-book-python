from smartplay.arena import Arena
from typing import List
import csv

def load_venue_settings(csv_path: str) -> list[Arena]:
    arena_list = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                arena = Arena(
                    venue_name=row["venueName"],
                    venue_id=row["venueId"],
                    district=row["district"],
                    fat_id=int(row["fatId"])
                )
                arena_list.append(arena)
            except (ValueError, KeyError) as e:
                print(f"❌ Skip row due to error: {e} -> {row}")
    return arena_list