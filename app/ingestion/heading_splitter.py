# Split at each: "#", "##", ...

import re
import uuid
from langchain_text_splitters import MarkdownHeaderTextSplitter

HEADERS_TO_SPLIT_ON = [
    ("#", "h1"), ("##", "h2"), ("###", "h3"), ("####", "h4")
]
_CODE_FENCE_PATTERN = re.compile(r"```.*?```", re.DOTALL)   # fence to avoid splitting wrong at "#" (comment) in code

# Mask code fences
def _mask_code_fences(text: str) -> tuple[str, dict[str, str]]:
    placeholders: dict[str, str] = {}

    def _replace(match: re.Match) -> str:   
        """Create code block distinguish which is code block and heading"""
        key = f"__CODE_BLOCK_{uuid.uuid4().hex[:8]}__"
        placeholders[key] = match.group(0)
        return key
    return _CODE_FENCE_PATTERN.sub(_replace, text), placeholders

# Restore code fences
def _restore_code_fences(text: str, placeholders: dict[str, str]) -> str:
    for key, original in placeholders.items():
        text = text.replace(key, original)
    return text

# Split by heading
def split_by_heading(markdown_text: str) -> list[dict]:
    """Split by heading to return dict"""
    masked_text, placeholders = _mask_code_fences(markdown_text)

    # Get splitter
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=HEADERS_TO_SPLIT_ON, strip_headers=True)
    docs = splitter.split_text(masked_text)

    sections = []
    for doc in docs:
        heading_path = list(doc.metadata.values()) # keep hierarchical heading
        content = _restore_code_fences(doc.page_content, placeholders)
        sections.append({
            "content": content,
            "heading_path": heading_path,
            "immediate_heading": heading_path[-1] if heading_path else ""   # get closest heading path
        })
    return sections