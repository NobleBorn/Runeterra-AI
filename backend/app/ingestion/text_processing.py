
import hashlib


def content_hash(text: str) -> str:
    """
    Return a stable SHA-256 hash of the text.
    """
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def chunk_text(
    text: str,
    chunk_size: int = 140,
    overlap: int = 25,
) -> list[str]:
    """
    Split text into overlapping word chunks.

    chunk_size: maximum words per chunk
    overlap: words shared between neighboring chunks
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be between 0 and chunk_size"
        )

    words = text.split()

    if not words:
        return []

    chunks = []
    step = chunk_size - overlap

    for start in range(0, len(words), step):
        end = min(start + chunk_size, len(words))

        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        if end == len(words):
            break

    return chunks
