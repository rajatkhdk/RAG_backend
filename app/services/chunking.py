import nltk
nltk.download('punkt', quiet=True)

import re
from typing import List

def chunk_text_fixed(text: str, chunk_size: int = 500) -> List[str]:
    """
    Fixed-size chunks (by characters)
    """
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

def chunk_text_sentence(text: str, max_sentences: int = 5) -> List[str]:
    """
    Chunk by sentence
    """
    sentences = nltk.sent_tokenize(text)
    chunks = []
    for i in range(0, len(sentences), max_sentences):
        chunk = " ".join(sentences[i:i+max_sentences])
        chunks.append(chunk)
    return chunks

def chunk_text(text: str, strategy: str = "fixed"):
    """
    Wrapper function
    """
    if strategy == "fixed":
        return chunk_text_fixed(text)
    elif strategy == "sentence":
        return chunk_text_sentence(text)
    else:
        raise ValueError("Unknown chunking strategy")