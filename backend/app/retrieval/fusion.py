
from app.retrieval.models import RetrievalResult


def reciprocal_rank_fusion(
    semantic_results: list[dict],
    keyword_results: list[dict],
    limit: int = 5,
    k: int = 60,
) -> list[RetrievalResult]:
    """
    Merge ranked search results using RRF.

    Each branch contributes:
        1 / (k + rank)

    Rank begins at 1.
    """
    fused = {}

    branches = [
        ("semantic", semantic_results),
        ("keyword", keyword_results),
    ]

    for branch_name, results in branches:
        seen_in_branch = set()

        for rank, result in enumerate(results, start=1):
            chunk_id = result["chunk_id"]

            # Avoid duplicate votes from one branch.
            if chunk_id in seen_in_branch:
                continue

            seen_in_branch.add(chunk_id)

            if chunk_id not in fused:
                fused[chunk_id] = RetrievalResult(
                    chunk_id=result["chunk_id"],
                    document_id=result["document_id"],
                    title=result["title"],
                    source_url=result["source_url"],
                    source_type=result["source_type"],
                    continuity=result["continuity"],
                    content=result["content"],
                )

            item = fused[chunk_id]

            item.rrf_score += 1.0 / (k + rank)

            if branch_name == "semantic":
                item.semantic_rank = rank
                item.semantic_score = result.get(
                    "semantic_score"
                )

            elif branch_name == "keyword":
                item.keyword_rank = rank
                item.keyword_score = result.get(
                    "keyword_score"
                )

    ranked = sorted(
        fused.values(),
        key=lambda item: (
            -item.rrf_score,
            item.chunk_id,
        ),
    )

    return ranked[:limit]
