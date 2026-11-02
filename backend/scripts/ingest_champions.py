
import argparse

from app.ingestion.sources import fetch_champions
from app.ingestion.pipeline import ingest_document


STARTER_CHAMPIONS = [
    "Jinx",
    "Vi",
    "Caitlyn",
    "Warwick",
    "Viktor",
    "Jayce",
    "Ekko",
    "Aatrox",
    "Varus",
    "Kayn",
]


def main():
    parser = argparse.ArgumentParser(
        description="Ingest League of Legends champion lore"
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Import all available champions",
    )

    args = parser.parse_args()

    selected = None if args.all else STARTER_CHAMPIONS

    print("Fetching champion data...")
    documents = fetch_champions(selected)

    counts = {
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "failed": 0,
    }

    for document in documents:
        name = document["name"]

        try:
            result = ingest_document(document)
            counts[result] += 1
            print(f"{name}: {result}")

        except Exception as error:
            counts["failed"] += 1
            print(f"Failed to ingest {name}: {error}")

    print("\nIngestion summary:")
    for status, count in counts.items():
        print(f"{status}: {count}")


if __name__ == "__main__":
    main()
