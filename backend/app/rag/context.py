
from app.retrieval.models import RetrievalResult
from app.rag.models import SourceReference


MAX_CONTEXT_CHARS = 12000


def select_context(
    results: list[RetrievalResult],
    max_chunks: int = 4,
    max_per_document: int = 2,
) -> list[SourceReference]:

    selected = []
    counts = {}
    total_chars = 0

    for result in results:
        if len(selected) >= max_chunks:
            break

        document_id = result.document_id

        if counts.get(document_id, 0) >= max_per_document:
            continue

        content = result.content.strip()

        if not content:
            continue

        if total_chars + len(content) > MAX_CONTEXT_CHARS:
            continue

        selected.append(
            SourceReference(
                id=len(selected) + 1,
                chunk_id=result.chunk_id,
                document_id=result.document_id,
                title=result.title,
                url=result.source_url,
                content=content,
            )
        )

        counts[document_id] = (
            counts.get(document_id, 0) + 1
        )
        total_chars += len(content)

    return selected


def format_context(
    sources: list[SourceReference],
) -> str:

    sections = []

    for source in sources:
        sections.append(
            f"[{source.id}]\n"
            f"Title: {source.title}\n"
            f"Source: {source.url}\n"
            f"Content:\n{source.content}"
        )

    return "\n\n---\n\n".join(sections)
