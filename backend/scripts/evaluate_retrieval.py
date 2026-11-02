
from app.retrieval.service import HybridRetriever


TEST_CASES = [
    ("Who is Aatrox?", "Aatrox Biography"),
    ("Who is the Darkin Blade?", "Aatrox Biography"),
    ("Who is Jinx?", "Jinx Biography"),
    ("What is Warwick's origin?", "Warwick Biography"),
    ("Who is Caitlyn?", "Caitlyn Biography"),
]


def main():
    retriever = HybridRetriever()
    hits = 0

    for question, expected_title in TEST_CASES:
        results = retriever.search(
            query=question,
            limit=5,
        )

        titles = [result.title for result in results]
        found = expected_title in titles

        if found:
            hits += 1

        status = "PASS" if found else "FAIL"

        print(f"{status}: {question}")
        print(f"Top results: {titles}\n")

    recall_at_5 = hits / len(TEST_CASES)

    print(f"Recall@5: {recall_at_5:.1%}")


if __name__ == "__main__":
    main()
