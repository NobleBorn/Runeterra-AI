
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

MIGRATION = (
    Path(__file__).resolve().parents[1]
    / "migrations"
    / "001_initial.sql"
)


def main():
    sql = MIGRATION.read_text(encoding="utf-8")

    with psycopg.connect(DATABASE_URL) as conn:
        # Simple local migration, run as a single transaction.
        conn.execute(sql)

    print("Database migration completed!")


if __name__ == "__main__":
    main()
