# Clean markdown before chunking

import re
import ftfy

# Define URL prefixes
LANGUAGE_URL_PREFIXES = re.compile(
    r"^/(de|es|fr|hi|ja|ko|pt|ru|tr|uk|zh|zh-hant|vi|it|nl|pl)(/|$)"
)

# Noise lines
NOISE_LINE_PATTERNS = [
    re.compile(r"^\[Skip to content\]", re.IGNORECASE),
    re.compile(r"^(On this page|Table of contents|Mục lục)\s*$", re.IGNORECASE),
    re.compile(r"^\d+\.\s*\[.*?\]\(#.*?\)\s*$"),  
    re.compile(r"^```\s*$"),                        # empty code fence 
    re.compile(r"^Copy(ied)?\s*$", re.IGNORECASE),  
]

# Check translated page => Remove
def is_translated_page(url_path: str) -> bool:
    """Remove if it's translated page"""
    return bool(LANGUAGE_URL_PREFIXES.match(url_path))

# Clean markdown
def clean_markdown(text: str) -> str:
    text = ftfy.fix_text(text)  # fix mojibake
    lines = text.split("\n")
    cleaned_lines = [
        line for line in lines
        if not any(pattern.match(line.strip()) for pattern in NOISE_LINE_PATTERNS) 
    ]
    result = "\n".join(cleaned_lines)

    # Merge empty lines into 1
    while "\n\n\n" in result:
        result = result.replace("\n\n\n", "\n\n")
    return result.strip()