
import argparse

import numpy as np

from app.db import get_connection
from app.ollama_client import generate_embedding


def search_lore(question: str, limit: int = 5):
    query_vector = np.asarray(
        generate_embedding(question),
        dtype=np.float32,
    )

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                d.title,
                d.source_url,
                c.content,
                1 - (c.embedding <=> %s) AS similarity
            FROM lore_chunks c
            JOIN lore_documents d
                ON c.document_id = d.id
            WHERE c.embedding_model = 'embeddinggemma'
            ORDER BY c.embedding <=> %s
            LIMIT %s
            """,
            (query_vector, query_vector, limit),
        ).fetchall()

    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("question", type=str)
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    results = search_lore(args.question, args.limit)

    if not results:
        print("No lore documents found.")
        return

    for index, row in enumerate(results, start=1):
        title, url, content, score = row

        print(f"\n--- Result {index} ---")
        print(f"Title: {title}")
        print(f"Similarity: {score:.4f}")
        print(f"Source: {url}")
        print(f"Content: {content}")


if __name__ == "__main__":
    main()
