
from app.db import get_connection
from app.ollama_client import generate_embedding
import numpy as np


SAMPLE_LORE = (
    "Aatrox is a Darkin warrior associated with "
    "the ancient Ascended of Shurima. "
    "His history is tied to the corruption and "
    "imprisonment of the Darkin."
)

SOURCE_URL = "https://example.invalid/runeterra-demo/aatrox"


def main():
    print("Generating document embedding...")
    embedding = generate_embedding(SAMPLE_LORE)

    print(f"Embedding dimensions: {len(embedding)}")

    if len(embedding) != 768:
        raise ValueError("Expected a 768-dimensional embedding")

    with get_connection() as conn:
        # Insert our test champion.
        conn.execute(
            """
            INSERT INTO champions (id, name, title, region)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            ("Aatrox", "Aatrox", "The Darkin Blade", "Shurima"),
        )

        # Insert a test lore document.
        document = conn.execute(
            """
            INSERT INTO lore_documents (
                title, source_url, source_type, content
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (source_url)
            DO UPDATE SET
                content = EXCLUDED.content,
                updated_at = NOW()
            RETURNING id
            """,
            (
                "Aatrox Demo Biography",
                SOURCE_URL,
                "demo",
                SAMPLE_LORE,
            ),
        ).fetchone()

        document_id = document[0]

        # Associate the document with Aatrox.
        conn.execute(
            """
            INSERT INTO document_champions (
                document_id, champion_id
            )
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            """,
            (document_id, "Aatrox"),
        )

        # Store one lore chunk and its vector.
        conn.execute(
            """
            INSERT INTO lore_chunks (
                document_id, chunk_index,
                content, embedding
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (document_id, chunk_index)
            DO UPDATE SET
                content = EXCLUDED.content,
                embedding = EXCLUDED.embedding
            """,
            (document_id, 0, SAMPLE_LORE, embedding),
        )

    print("Test lore inserted successfully!")

    # Create an embedding for a new question.
    question = "Who is the Darkin warrior Aatrox?"
    query_embedding = np.array(
        generate_embedding(question),
        dtype=np.float32
    )

    # Retrieve the most similar stored passages.
    with get_connection() as conn:
        results = conn.execute(
            """
            SELECT
                c.content,
                d.title,
                1 - (c.embedding <=> %s) AS similarity
            FROM lore_chunks c
            JOIN lore_documents d
                ON c.document_id = d.id
            WHERE c.embedding_model = 'embeddinggemma'
            ORDER BY c.embedding <=> %s
            LIMIT 3
            """,
            (query_embedding, query_embedding),
        ).fetchall()

    print("\nSearch results:")

    for content, title, similarity in results:
        print(f"\nDocument: {title}")
        print(f"Similarity: {similarity:.4f}")
        print(f"Content: {content}")


if __name__ == "__main__":
    main()
