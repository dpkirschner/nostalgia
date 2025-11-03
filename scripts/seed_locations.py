import asyncio
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.location import Location


async def seed_locations(csv_path: str):
    async with AsyncSessionLocal() as session:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            locations_to_add = []
            for row in reader:
                result = await session.execute(
                    select(Location).where(Location.id == int(row["id"]))
                )
                existing = result.scalar_one_or_none()

                if existing:
                    print(f"Location {row['id']} already exists, skipping")
                    continue

                location = Location(
                    id=int(row["id"]),
                    lat=float(row["lat"]),
                    lon=float(row["lon"]),
                    address=row["address"],
                )
                locations_to_add.append(location)

            if locations_to_add:
                session.add_all(locations_to_add)
                await session.commit()
                print(f"Successfully seeded {len(locations_to_add)} locations")
            else:
                print("No new locations to seed")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python seed_locations.py <path_to_locations.csv>")
        sys.exit(1)

    csv_path = sys.argv[1]
    if not Path(csv_path).exists():
        print(f"Error: File not found: {csv_path}")
        sys.exit(1)

    asyncio.run(seed_locations(csv_path))
