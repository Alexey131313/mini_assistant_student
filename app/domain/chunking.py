"""Разбиение текста на чанки.

TODO (M3): правила разбиения и граничные случаи — в SPEC.md (веха M3)
и в tests/unit/test_chunking.py.
"""


def chunk_text(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    """TODO: вернуть список непустых чанков длиной не больше size."""
    if size <= 0:
        raise ValueError("unvalid size")
    if overlap < 0 or overlap >= size:
        raise ValueError("unvalid overlap")
    text = text.strip()
    if not text:
            return []
    paragraphs: list[str] = text.split("\n\n")
    chunks: list[str] = []
    current_chunk_parts: list[str] = []
    current_length: int = 0
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(para) > size:
            if current_chunk_parts:
                chunks.append("\n\n".join(current_chunk_parts))
                current_chunk_parts = []
                current_length = 0
            start = 0
            n = len(para)
            while start < n:
                end = min(start + size, n)
                if para[start:end]:
                    chunks.append(para[start:end])
                if end == n:
                    break
                start += size - overlap
        else:
            separator_len = 2 if current_chunk_parts else 0
            
            if current_length + separator_len + len(para) <= size:
                current_chunk_parts.append(para)
                current_length += separator_len + len(para)
            else:
                if current_chunk_parts:
                    chunks.append("\n\n".join(current_chunk_parts))
                current_chunk_parts = [para]
                current_length = len(para)
                
    if current_chunk_parts:
        chunks.append("\n\n".join(current_chunk_parts))
        
    return chunks