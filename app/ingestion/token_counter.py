# Count token for each doc => Use token_count of all-mpnet-base-v2 to avoid different from embedding step

from functools import lru_cache
from transformers import AutoTokenizer
from app.config import config

MODEL_MAX_SEQ_LENGTH = 384  # limit for model all-mpnet-base-v2
SAFE_TOKEN_CAP = 380        # space for [CLS] / [SEP]

# Get tokenizer
@lru_cache(maxsize=1)
def get_tokenizer():
    return AutoTokenizer.from_pretrained(f"sentence-transformers/{config.embedding.model_name}")

# Count tokens
def count_tokens(text: str) -> int:
    return len(get_tokenizer().encode(text, add_special_tokens=True))   # add [CLS], [SEP] tokens

# Safe cap
def exceeds_safe_cap(text: str) -> bool:
    return count_tokens(text) > SAFE_TOKEN_CAP