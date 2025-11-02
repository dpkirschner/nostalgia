import asyncio
import csv
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.tenancy import Tenancy


async def seed_tenancies(csv_path: str):
    async with AsyncSessionLocal() as session:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            tenancies_to_add = []
            for row in reader:
                start_date = None
                if row.get('start_date'):
                    try:
                        start_date = datetime.strptime(row['start_date'], '%Y-%m-%d').date()
                    except ValueError:
                        print(f"Warning: Invalid start_date format for {row['business_name']}")

                end_date = None
                if row.get('end_date'):
                    try:
                        end_date = datetime.strptime(row['end_date'], '%Y-%m-%d').date()
                    except ValueError:
                        print(f"Warning: Invalid end_date format for {row['business_name']}")

                is_current = row.get('is_current', 'false').lower() in ('true', '1', 'yes')

                tenancy = Tenancy(
                    location_id=int(row['location_id']),
                    business_name=row['business_name'],
                    category=row.get('category') or None,
                    start_date=start_date,
                    end_date=end_date,
                    is_current=is_current,
                )
                tenancies_to_add.append(tenancy)

            if tenancies_to_add:
                session.add_all(tenancies_to_add)
                await session.commit()
                print(f"Successfully seeded {len(tenancies_to_add)} tenancies")
            else:
                print("No tenancies to seed")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python seed_tenancies.py <path_to_tenancies.csv>")
        sys.exit(1)

    csv_path = sys.argv[1]
    if not Path(csv_path).exists():
        print(f"Error: File not found: {csv_path}")
        sys.exit(1)

    asyncio.run(seed_tenancies(csv_path))
