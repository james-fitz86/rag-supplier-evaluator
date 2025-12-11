from typing import List


EMBEDDING_DIM = 1536


def generate_embedding(text: str) -> List[float]:
    """
    Placeholder embedding generator.
    Later this will call a real embedding model (OpenAI, HF, etc.).
    For now it just returns a zero vector of the right size so the DB insert works.
    """
    return [0.0] * EMBEDDING_DIM
