
from ollama import Client
from dotenv import load_dotenv
import os

client = Client(host="http://localhost:11434")

load_dotenv()

CHAT_MODEL = os.environ["CHAT_MODEL"]
EMBEDDING_MODEL = os.environ["EMBEDDING_MODEL"]


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
