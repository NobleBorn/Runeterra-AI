
import argparse

from app.rag.service import RAGService


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("question", type=str)
    args = parser.parse_args()

    service = RAGService()

    print(f"\nQuestion: {args.question}")
    print("\nRetrieving lore and generating answer...\n")

    response = service.answer(args.question)

    print("Answer:")
    print(response.answer)

    print(f"\nGrounded: {response.grounded}")
    print(f"Status: {response.status.value}")

    if response.sources:
        print("\nSources:")

        for source in response.sources:
            print(f"\n[{source.id}] {source.title}")
            print(f"URL: {source.url}")
            print(f"Chunk ID: {source.chunk_id}")
            
    else:
        print("\nNo cited sources.")


if __name__ == "__main__":
    main()
