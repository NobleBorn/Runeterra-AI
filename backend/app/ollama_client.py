
from ollama import Client

client = Client(host="http://localhost:11434")

CHAT_MODEL = "qwen3:4b"
EMBEDDING_MODEL = "embeddinggemma"


def generate_answer(question: str) -> str:
    response = client.chat(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful League of Legends "
                    "lore assistant. If uncertain about a "
                    "fact, acknowledge that uncertainty."
                )
            },
            {
                "role": "user",
                "content": question
            }
        ],
        think=False
    )

    return response.message.content or ""


def generate_embedding(text: str) -> list[float]:
    response = client.embed(
        model=EMBEDDING_MODEL,
        input=text
    )

    return response.embeddings[0]
