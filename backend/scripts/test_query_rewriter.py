
import asyncio

from app.rag.models import HistoryMessage
from app.rag.query_rewriter import rewrite_question


TEST_CASES = [
    {
        "history": [
            HistoryMessage(
                role="user",
                content="Who is Aatrox?",
            ),
            HistoryMessage(
                role="assistant",
                content="Aatrox is a Darkin warrior.",
            ),
        ],
        "question": (
            "What happened to him after he was imprisoned?"
        ),
    },
    {
        "history": [
            HistoryMessage(
                role="user",
                content="Tell me about Jinx.",
            ),
            HistoryMessage(
                role="assistant",
                content="Jinx is a champion from Zaun.",
            ),
        ],
        "question": "Where is she from?",
    },
    {
        "history": [
            HistoryMessage(
                role="user",
                content="Who is Aatrox?",
            ),
        ],
        "question": "Who is Mordekaiser?",
    },
    {
        "history": [
            HistoryMessage(
                role="user",
                content="Tell me about Aatrox and Varus.",
            ),
        ],
        "question": "What happened to him?",
    },
]


async def main():
    for case in TEST_CASES:
        question = case["question"]

        rewritten = await rewrite_question(
            question=question,
            history=case["history"],
        )

        print(f"\nOriginal: {question}")
        print(f"Rewritten: {rewritten}")


if __name__ == "__main__":
    asyncio.run(main())
