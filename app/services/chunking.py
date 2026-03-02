from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from app.services.vector_store import model

def chunk_text_recursive(
        text: str,
        chunk_size: int = 800,
        chunk_overlap: int = 150
) -> List[str]:
    """
Recursive semantic-aware chunking with overlap.
Tries paragraph -> sentence -> word splits.
Best default choice for RAG systems.
"""

    splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap,
        separators=["\n\n","\n","."," ",""]
    )

    return splitter.split_text(text)

def chunk_text_fixed(
        text: str,
        chunk_size: int = 800,
        chunk_overlap: int = 150
) -> List[str]:
    """
Recursive semantic-aware chunking with overlap.
Tries paragraph -> sentence -> word splits.
Best default choice for RAG systems.
"""

    splitter = CharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap,
        separator=" "
    )

    return splitter.split_text(text)

from app.services.vector_store import model

def chunk_text_semantic(
        text: str,
        chunk_size: int = 800,
        chunk_overlap: int = 150
) -> List[str]:
    """
Recursive semantic-aware chunking with overlap.
Tries paragraph -> sentence -> word splits.
Best default choice for RAG systems.
"""

    splitter = SemanticChunker(
        embeddings=model,
        breakpoint_threshold_type="percentile", # or standard deviation
    breakpoint_threshold_amount=70
    )

    return splitter.split_text(text)

def chunk_text(
        text: str,
        strategy: str = "recursive",
        **kwargs
) -> List[str]:
    """
    Wrapper function

    stratigies:
    -recursive 
    - fized
    - sentence
    """

    if strategy == "recursive":
        return chunk_text_recursive(text, **kwargs)
    
    elif strategy == "fixed":
        return chunk_text_fixed(text, **kwargs)
    
    elif strategy == "semantic":
        return chunk_text_semantic(text, **kwargs)
    
    else:
        raise ValueError("Unknown chunking strategy")