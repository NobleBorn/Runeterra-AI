
from app.db import get_connection
from app.retrieval.query_processing import (
    prepare_keyword_query,
)


def keyword_search(
    query: str,
    limit: int = 20,
) -> list[dict]:

    processed_query = prepare_keyword_query(query)

    if not processed_query:
        return []

    with get_connection() as conn:
        rows = conn.execute(
            """
            WITH search_query AS (
                SELECT websearch_to_tsquery(
                    'english', %s
                ) AS q
            ),
            candidates AS (
                SELECT
                    c.id,
                    c.document_id,
                    d.title,
                    d.source_url,
                    d.source_type,
                    d.continuity,
                    c.content,
                    (
                        setweight(
                            to_tsvector('english', COALESCE(ch.name, '')),
                            'A'
                        ) ||
                        setweight(
                            to_tsvector('english', COALESCE(ch.title, '')),
                            'A'
                        ) ||
                        setweight(
                            to_tsvector('english', d.title),
                            'B'
                        ) ||
                        setweight(
                            to_tsvector('english', c.content),
                            'C'
                        )
                    ) AS search_vector
                FROM lore_chunks c
                JOIN lore_documents d
                    ON d.id = c.document_id
                LEFT JOIN document_champions dc
                    ON dc.document_id = d.id
                LEFT JOIN champions ch
                    ON ch.id = dc.champion_id
                WHERE c.embedding_model = 'embeddinggemma'
                  AND d.source_type <> 'demo'
            )
            SELECT
                candidates.id,
                candidates.document_id,
                candidates.title,
                candidates.source_url,
                candidates.source_type,
                candidates.continuity,
                candidates.content,
                ts_rank_cd(
                    candidates.search_vector,
                    search_query.q
                ) AS score
            FROM candidates
            CROSS JOIN search_query
            WHERE candidates.search_vector @@ search_query.q
            ORDER BY score DESC, candidates.id
            LIMIT %s
            """,
            (processed_query, limit),
        ).fetchall()

    return [
        {
            "chunk_id": str(row[0]),
            "document_id": str(row[1]),
            "title": row[2],
            "source_url": row[3],
            "source_type": row[4],
            "continuity": row[5],
            "content": row[6],
            "keyword_score": float(row[7]),
        }
        for row in rows
    ]
