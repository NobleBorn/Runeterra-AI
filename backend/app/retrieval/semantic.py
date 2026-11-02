
import numpy as np

from app.db import get_connection
from app.ollama_client import generate_embedding


EMBEDDING_MODEL = "embeddinggemma"


def semantic_search(
    query: str,
    limit: int = 20,
) -> list[dict]:

    # Convert question into a vector.
    embedding = np.asarray(
        generate_embedding(query),
        dtype=np.float32,
    )

    if embedding.shape != (768,):
        raise ValueError(
            f"Expected 768 dimensions, got {embedding.shape}"
        )

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                c.id,
                c.document_id,
                d.title,
                d.source_url,
                d.source_type,
                d.continuity,
                c.content,
                1 - (c.embedding <=> %s) AS score
            FROM lore_chunks c
            JOIN lore_documents d
                ON d.id = c.document_id
            WHERE c.embedding_model = %s AND d.source_type <> 'demo'
            ORDER BY c.embedding <=> %s
            LIMIT %s
            """,
            (
                embedding,
                EMBEDDING_MODEL,
                embedding,
                limit,
            ),
        ).fetchall()

    results = []

    for row in rows:
        results.append({
            "chunk_id": str(row[0]),
            "document_id": str(row[1]),
            "title": row[2],
            "source_url": row[3],
            "source_type": row[4],
            "continuity": row[5],
            "content": row[6],
            "semantic_score": float(row[7]),
        })

    return results
