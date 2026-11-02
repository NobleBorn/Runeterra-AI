
from app.ollama_client import client, CHAT_MODEL

response = client.chat(
    model=CHAT_MODEL,
    messages=[
        {
            "role": "system",
            "content": (
                "You are a League of Legends lore assistant. "
                "Answer concisely."
            ),
        },
        {
            "role": "user",
            "content": "Who is Aatrox? Answer in two sentences."
        }
    ],
    options={
        "temperature": 0.2,
        "num_predict": 300,
    },
)

print("MODEL:", CHAT_MODEL)
print("CONTENT:", repr(response.message.content))
print("THINKING:", repr(response.message.thinking))
print("STOP REASON:", response.done_reason)
