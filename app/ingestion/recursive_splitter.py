# Recursive splitting and custom step for code handling

import re
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from app.ingestion.token_counter import get_tokenizer, count_tokens, SAFE_TOKEN_CAP

_CODE_FENCE_PATTERN = re.compile(r"```.*?```", re.DOTALL)

# Split oversized code 
def _split_oversized_code_fence(code_block: str) -> list[str]:
    """Handle if code block is oversized"""
    lines = code_block.split("\n")
    fence_marker, closing = lines[0], lines[-1]
    body_lines = lines[1:-1]

    parts: list[list[str]] = [[]]
    for line in body_lines:
        candidate = "\n".join(parts[-1] + [line])
        wrapped = f"{fence_marker}\n{candidate}\n{closing}"
        if parts[-1] and count_tokens(wrapped) > SAFE_TOKEN_CAP:
            parts.append([line])
        else:
            parts[-1].append(line)

    total = len(parts)
    return [
        f"{fence_marker}\n" + "\n".join(part) + f"\n{closing}\n<!-- (phần {i+1}/{total}, tách do vượt giới hạn token) -->"
        for i, part in enumerate(parts)
    ]

# Extract code
def _extract_oversized_fences(text: str) -> tuple[str, dict[str, list[str]]]:
    """Replace code fence oversized by placeholder"""
    replacements: dict[str, list[str]] = {}

    def _replace(match: re.Match) -> str:
        block = match.group(0)
        if count_tokens(block) > SAFE_TOKEN_CAP:
            key = f"__OVERSIZED_CODE_{len(replacements)}__"
            replacements[key] = _split_oversized_code_fence(block)
            return key
        return block  # code fence normal -> keep it
    return _CODE_FENCE_PATTERN.sub(_replace, text), replacements

# Split sections
def split_long_section(text: str, chunk_overlap: int = 50) -> list[str]:
    masked_text, oversized_fences = _extract_oversized_fences(text)
    separators = RecursiveCharacterTextSplitter.get_separators_for_language(Language.MARKDOWN)

    # Get splitter
    splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        tokenizer=get_tokenizer(),
        chunk_size=SAFE_TOKEN_CAP,
        chunk_overlap=chunk_overlap,
        separators=separators
    )
    rough_chunks = splitter.split_text(masked_text)
    final_chunks: list[str] = []

    for chunk in rough_chunks:
        stripped = chunk.strip()
        if stripped in oversized_fences:
            final_chunks.extend(oversized_fences[stripped])
        else:
            final_chunks.append(chunk)
    return final_chunks