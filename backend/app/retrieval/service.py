
from app.retrieval.semantic import semantic_search
from app.retrieval.keyword import keyword_search
from app.retrieval.fusion import reciprocal_rank_fusion
from app.retrieval.models import RetrievalResult


class HybridRetriever:
    def __init__(
        self,
        candidate_limit: int = 20,
        rrf_k: int = 60,
    ):
        if candidate_limit < 1:
            raise ValueError(
                "candidate_limit must be positive"
            )

        if rrf_k < 1:
            raise ValueError("rrf_k must be positive")

        self.candidate_limit = candidate_limit
        self.rrf_k = rrf_k

    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[RetrievalResult]:

        if not query.strip():
            return []

        if limit < 1:
            raise ValueError("limit must be positive")

        candidates = max(
            self.candidate_limit, limit
        )

        # 1. Retrieve semantic matches.
        semantic_results = semantic_search(
            query=query,
            limit=candidates,
        )

        # 2. Retrieve keyword matches.
        keyword_results = keyword_search(
            query=query,
            limit=candidates,
        )

        # 3. Combine rankings.
        return reciprocal_rank_fusion(
            semantic_results=semantic_results,
            keyword_results=keyword_results,
            limit=limit,
            k=self.rrf_k,
        )
