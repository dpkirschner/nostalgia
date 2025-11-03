import asyncio
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

from app.db.session import AsyncSessionLocal
from app.models.kc_food_inspection import KcFoodInspection


async def load_kc_food_inspections(csv_path: str, batch_size: int = 1000):
    async with AsyncSessionLocal() as session:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            inspections_to_add = []
            total_processed = 0
            total_skipped = 0

            for row in reader:
                if not row.get("Name") or not row.get("Name").strip():
                    total_skipped += 1
                    continue

                if not row.get("Address") or not row.get("Address").strip():
                    total_skipped += 1
                    continue

                try:
                    latitude = float(row["Latitude"]) if row.get("Latitude") else None
                    longitude = float(row["Longitude"]) if row.get("Longitude") else None
                except (ValueError, KeyError):
                    latitude = None
                    longitude = None

                if latitude is None or longitude is None:
                    total_skipped += 1
                    continue

                inspection_date = None
                if row.get("Inspection Date"):
                    try:
                        inspection_date = datetime.strptime(
                            row["Inspection Date"], "%m/%d/%Y"
                        ).date()
                    except ValueError:
                        try:
                            inspection_date = datetime.strptime(
                                row["Inspection Date"], "%Y-%m-%d"
                            ).date()
                        except ValueError:
                            pass

                inspection = KcFoodInspection(
                    business_name=row["Name"].strip(),
                    address=row.get("Address", "").strip() or None,
                    city=row.get("City", "").strip() or None,
                    state=row.get("State", "WA").strip() or "WA",
                    zip=row.get("Zip Code", "").strip() or None,
                    latitude=latitude,
                    longitude=longitude,
                    inspection_date=inspection_date,
                    raw_line=json.dumps(row),
                )
                inspections_to_add.append(inspection)
                total_processed += 1

                if len(inspections_to_add) >= batch_size:
                    session.add_all(inspections_to_add)
                    await session.commit()
                    print(
                        f"Committed batch: {total_processed} records processed, {total_skipped} skipped"
                    )
                    inspections_to_add = []

            if inspections_to_add:
                session.add_all(inspections_to_add)
                await session.commit()
                print(
                    f"Committed final batch: {total_processed} records processed, {total_skipped} skipped"
                )

            print(f"\nLoad complete!")
            print(f"Total records processed: {total_processed}")
            print(f"Total records skipped: {total_skipped}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python load_kc_food_inspections.py <path_to_csv> [batch_size]")
        print(
            "Example: python load_kc_food_inspections.py data/Food_Establishment_Inspection_Data.csv 1000"
        )
        sys.exit(1)

    csv_path = sys.argv[1]
    if not Path(csv_path).exists():
        print(f"Error: File not found: {csv_path}")
        sys.exit(1)

    batch_size = 1000
    if len(sys.argv) >= 3:
        try:
            batch_size = int(sys.argv[2])
        except ValueError:
            print(f"Warning: Invalid batch_size '{sys.argv[2]}', using default: 1000")

    print(f"Loading KC Food Inspections from: {csv_path}")
    print(f"Batch size: {batch_size}")
    print("-" * 60)

    asyncio.run(load_kc_food_inspections(csv_path, batch_size))
