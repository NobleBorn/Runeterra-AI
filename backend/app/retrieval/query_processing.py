
import re

QUESTION_WORDS = {
    "what", "who", "where", "when", "why", "how",
    "is", "are", "was", "were", "did", "does", "do",
    "happened", "happen", "tell", "me", "about",
    "the", "a", "an", "to", "of", "in"
}


def prepare_keyword_query(query: str) -> str:
    words = re.findall(r"[^\W_]+", query.lower(), re.UNICODE)

    important_words = [
        word for word in words
        if word not in QUESTION_WORDS
    ]

    return " ".join(important_words)
