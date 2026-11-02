
import html
import re
import httpx
import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.environ["DDRAGON_URL"]


def clean_text(text: str) -> str:
    """Remove markup and normalize whitespace."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return " ".join(text.split())


def fetch_champions(
    champion_ids: list[str] | None = None,
) -> list[dict]:
    """
    Fetch champion metadata and short lore from Data Dragon.
    Uses one HTTP client and a bounded request timeout.
    """
    documents = []

    with httpx.Client(timeout=20.0) as client:
        # 1. Get the latest Data Dragon version.
        response = client.get(
            f"{BASE_URL}/api/versions.json"
        )
        response.raise_for_status()
        version = response.json()[0]

        # 2. Fetch available champion IDs.
        response = client.get(
            f"{BASE_URL}/cdn/{version}/data/en_US/champion.json"
        )
        response.raise_for_status()

        roster = response.json()["data"]

        # 3. Use selected champions or the complete roster.
        ids = champion_ids or list(roster.keys())

        for champion_id in ids:
            if champion_id not in roster:
                print(f"Unknown champion: {champion_id}")
                continue

            detail_url = (
                f"{BASE_URL}/cdn/{version}/data/"
                f"en_US/champion/{champion_id}.json"
            )

            response = client.get(detail_url)
            response.raise_for_status()

            champion = response.json()["data"][champion_id]

            lore = clean_text(champion.get("lore", ""))

            if not lore:
                print(f"Skipping {champion_id}: no lore")
                continue

            title = clean_text(champion.get("title", ""))
            region = None  # Data Dragon does not reliably supply lore region.

            documents.append({
                "champion_id": champion_id,
                "name": champion["name"],
                "title": title,
                "region": region,
                "image_url": (
                    f"{BASE_URL}/cdn/{version}/img/"
                    f"champion/{champion_id}.png"
                ),
                "source_key": f"ddragon:en_US:{champion_id}",
                "source_url": detail_url,
                "document_title": f"{champion['name']} Biography",
                "content": lore,
                "source_type": "ddragon",
            })

            print(f"Fetched: {champion['name']}")

    return documents
