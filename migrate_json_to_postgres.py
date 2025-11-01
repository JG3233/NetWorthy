"""
Migration script to convert net_worth_history.json to PostgreSQL database
Run this script to migrate your existing JSON data to the new PostgreSQL database
"""
import json
import os
from app import app, init_db
from models import db, NetWorthYear


def migrate_json_to_postgres(json_file='net_worth_history.json'):
    """Migrate data from JSON file to PostgreSQL database"""

    if not os.path.exists(json_file):
        print(f"JSON file '{json_file}' not found. Starting with empty database.")
        return

    print(f"Reading data from {json_file}...")

    with open(json_file, 'r') as f:
        data = json.load(f)

    if not data:
        print("JSON file is empty. Nothing to migrate.")
        return

    print(f"Found {len(data)} years of data to migrate.")

    with app.app_context():
        # Initialize database
        print("Initializing database...")
        db.create_all()

        migrated_count = 0
        skipped_count = 0

        for year_str, year_data in data.items():
            try:
                year = int(year_str)

                # Check if year already exists
                existing = NetWorthYear.query.filter_by(year=year).first()
                if existing:
                    print(f"Year {year} already exists in database. Skipping.")
                    skipped_count += 1
                    continue

                # Create new record from JSON data
                year_record = NetWorthYear.from_dict(year, year_data)
                db.session.add(year_record)
                migrated_count += 1
                print(f"Migrated year {year}: Net Worth = ${year_record.net_worth:,.2f}")

            except Exception as e:
                print(f"Error migrating year {year_str}: {e}")
                continue

        # Commit all changes
        db.session.commit()
        print(f"\nMigration complete!")
        print(f"  - Migrated: {migrated_count} years")
        print(f"  - Skipped: {skipped_count} years")

        # Verify migration
        total_records = NetWorthYear.query.count()
        print(f"  - Total records in database: {total_records}")


if __name__ == '__main__':
    print("=" * 60)
    print("NetWorthy JSON to PostgreSQL Migration Script")
    print("=" * 60)

    migrate_json_to_postgres()

    print("\nMigration finished. You can now use the PostgreSQL-based app.")
    print("Your original JSON file has been preserved as a backup.")
