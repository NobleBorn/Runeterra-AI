
import argparse

from app.retrieval.service import HybridRetriever


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "question",
        type=str,
        help="Lore question to search for",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=5,
    )

    args = parser.parse_args()

    retriever = HybridRetriever()

    results = retriever.search(
        query=args.question,
        limit=args.limit,
    )

    if not results:
        print("No relevant lore passages found.")
        return

    for index, result in enumerate(results, start=1):
        print(f"\n--- Result {index} ---")
        print(f"Title: {result.title}")
        print(f"RRF score: {result.rrf_score:.5f}")
        print(f"Semantic rank: {result.semantic_rank}")
        print(f"Keyword rank: {result.keyword_rank}")
        print(f"Semantic score: {result.semantic_score}")
        print(f"Keyword score: {result.keyword_score}")
        print(f"Source: {result.source_url}")
        print(f"Content:\n{result.content}\n")


if __name__ == "__main__":
    main()
