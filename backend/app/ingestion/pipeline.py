
import json

import numpy as np

from app.db import get_connection
from app.ollama_client import generate_embedding
from app.ingestion.text_processing import (
    chunk_text,
    content_hash,
)


EMBEDDING_MODEL = "embeddinggemma"
VECTOR_DIMENSIONS = 768


def ingest_document(document: dict) -> str:
    """
    Insert or update one champion biography.

    Returns:
        "created", "updated", or "skipped"
    """
    source_key = document["source_key"]
    text = document["content"]
    new_hash = content_hash(text)

    # 1. Check if this document is already indexed.
    with get_connection() as conn:
        existing = conn.execute(
            """
            SELECT
                d.id,
                d.content_hash,
                EXISTS (
                    SELECT 1
                    FROM lore_chunks c
                    WHERE c.document_id = d.id
                      AND c.embedding_model = %s
                ) AS has_embeddings
            FROM lore_documents d
            WHERE d.source_key = %s
            """,
            (EMBEDDING_MODEL, source_key),
        ).fetchone()

    unchanged = (
        existing is not None
        and existing[1] == new_hash
        and existing[2]
    )

    # 2. Generate vectors only when necessary.
    vectors = []

    if not unchanged:
        chunks = chunk_text(text)

        if not chunks:
            raise ValueError("Cannot ingest empty content")

        print(
            f"Generating {len(chunks)} embedding(s) "
            f"for {document['name']}..."
        )

        for chunk in chunks:
            vector = np.asarray(
                generate_embedding(chunk),
                dtype=np.float32,
            )

            if vector.shape != (VECTOR_DIMENSIONS,):
                raise ValueError(
                    f"Unexpected embedding shape: {vector.shape}"
                )

            vectors.append((chunk, vector))

    # 3. Insert/update everything in one transaction.
    with get_connection() as conn:
        # Champion metadata
        conn.execute(
            """
            INSERT INTO champions (
                id, name, title, region, image_url
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id)
            DO UPDATE SET
                name = EXCLUDED.name,
                title = EXCLUDED.title,
                image_url = EXCLUDED.image_url
            """,
            (
                document["champion_id"],
                document["name"],
                document["title"],
                document["region"],
                document["image_url"],
            ),
        )

        # Original lore document
        row = conn.execute(
            """
            INSERT INTO lore_documents (
                source_key,
                title,
                source_url,
                source_type,
                content,
                content_hash
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (source_key)
            DO UPDATE SET
                title = EXCLUDED.title,
                source_url = EXCLUDED.source_url,
                source_type = EXCLUDED.source_type,
                content = EXCLUDED.content,
                content_hash = EXCLUDED.content_hash,
                updated_at = CASE
                    WHEN lore_documents.content_hash
                         IS DISTINCT FROM EXCLUDED.content_hash
                    THEN NOW()
                    ELSE lore_documents.updated_at
                END
            RETURNING id
            """,
            (
                source_key,
                document["document_title"],
                document["source_url"],
                document["source_type"],
                text,
                new_hash,
            ),
        ).fetchone()

        document_id = row[0]

        # Link the champion and document.
        conn.execute(
            """
            INSERT INTO document_champions (
                document_id, champion_id
            )
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            """,
            (document_id, document["champion_id"]),
        )

        if not unchanged:
            # Replace older embeddings for this document.
            conn.execute(
                """
                DELETE FROM lore_chunks
                WHERE document_id = %s
                """,
                (document_id,),
            )

            for index, (chunk, vector) in enumerate(vectors):
                metadata = {
                    "champion": document["name"],
                    "source_type": document["source_type"],
                }

                conn.execute(
                    """
                    INSERT INTO lore_chunks (
                        document_id,
                        chunk_index,
                        content,
                        embedding,
                        embedding_model,
                        metadata
                    )
                    VALUES (%s, %s, %s, %s, %s, %s::jsonb)
                    """,
                    (
                        document_id,
                        index,
                        chunk,
                        vector,
                        EMBEDDING_MODEL,
                        json.dumps(metadata),
                    ),
                )

    if unchanged:
        return "skipped"

    return "updated" if existing else "created"
