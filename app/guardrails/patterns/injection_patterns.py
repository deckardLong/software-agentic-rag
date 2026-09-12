# List of regex patterns to find out injection prompt

import re

INJECTION_PATTERNS: list[re.Pattern] = [
    # ======= English Patterns =======
    re.compile(r"ignore (all |any )?(previous|above|prior) instructions", re.IGNORECASE),
    re.compile(r"disregard (all |any )?(previous|above|prior) (instructions|rules|prompts)", re.IGNORECASE),
    re.compile(r"forget (everything|all) (you|above)", re.IGNORECASE),
    re.compile(r"you are now (a|an)?\s*\w+", re.IGNORECASE),
    re.compile(r"reveal (your|the) (system )?prompt", re.IGNORECASE),
    re.compile(r"show me (your|the) (system )?(prompt|instructions)", re.IGNORECASE),
    re.compile(r"what (is|are) your (system )?(prompt|instructions)", re.IGNORECASE),
    re.compile(r"act as (if )?you (are|were)", re.IGNORECASE),
    re.compile(r"pretend (you are|to be)", re.IGNORECASE),
    re.compile(r"\bDAN\b"),     # # "Do Anything Now" popular jailbreak pattern
    re.compile(r"jailbreak", re.IGNORECASE),
    re.compile(r"bypass (your |the )?(safety|guardrail|filter)", re.IGNORECASE),

    # ======= Vietnamese Patterns =======
    # "bỏ qua các hướng dẫn trước đó / phía trên"
    re.compile(r"bỏ qua (tất cả |mọi )?(các )?(hướng dẫn|chỉ thị|lệnh|quy tắc|luật) (trước|phía trên|ở trên)", re.IGNORECASE),
    # "quên hết / quên tất cả những gì (bạn) vừa được dặn"
    re.compile(r"quên (hết|tất cả|toàn bộ)( những gì)?( bạn)?( vừa)?( được)?( dặn| nói| hướng dẫn)?", re.IGNORECASE),
    # "từ bây giờ bạn là..." / "bạn bây giờ là..." — role override
    re.compile(r"(từ )?bây giờ bạn (là|hãy đóng vai|sẽ là)", re.IGNORECASE),
    re.compile(r"bạn (hãy )?đóng vai (là )?", re.IGNORECASE),
    re.compile(r"giả vờ (là|bạn là)", re.IGNORECASE),
    re.compile(r"giả sử (bạn|mày) (là|không có)", re.IGNORECASE),
    # "tiết lộ / cho tôi xem system prompt"
    re.compile(r"(tiết lộ|cho (tôi|xem)|hiển thị) (system prompt|prompt hệ thống|chỉ thị hệ thống)", re.IGNORECASE),
    re.compile(r"prompt (hệ thống|gốc|ban đầu) của (bạn|mày) là gì", re.IGNORECASE),
    # "vượt qua / bỏ qua bộ lọc an toàn"
    re.compile(r"(vượt qua|bỏ qua|phá vỡ) (bộ lọc|rào cản|giới hạn|an toàn|guardrail)", re.IGNORECASE),
    re.compile(r"không (còn )?(bị )?(giới hạn|ràng buộc|kiểm duyệt)", re.IGNORECASE),

    # ======= Cross-Language =======
    re.compile(r"</?(system|admin|instruction)>", re.IGNORECASE),
    re.compile(r"\[SYSTEM\]|\[ADMIN\]|\[OVERRIDE\]", re.IGNORECASE),
]

# Match injection pattern
def matches_injection_pattern(text: str) -> tuple[bool, str | None]:
    """Find out what injection pattern does it match"""
    for pattern in INJECTION_PATTERNS:
        if pattern.search(text):
            return True, pattern.pattern
    return False, None