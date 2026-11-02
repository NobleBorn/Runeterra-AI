import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

with psycopg.connect(
    os.environ["DATABASE_URL"],
    connect_timeout=10,
) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                (SELECT COUNT(*) FROM champions),
                (SELECT COUNT(*) FROM lore_documents),
                (SELECT COUNT(*) FROM lore_chunks),
                (SELECT COUNT(*) FROM document_champions)
        """)

        print("Database counts:", cur.fetchone())

        cur.execute("""
            SELECT
                extensions.vector_dims(embedding)
            FROM lore_chunks
            LIMIT 1
        """)

        print("Embedding dimensions:", cur.fetchone())