import re

REPLACEMENTS = [
    (r"\bcentury[-\s]*21\b", "le réseau"),
    (r"\bcentury[-\s]*net\b", "la base acquéreurs interne"),
    (r"\bcenturynet\b", "la base acquéreurs interne"),
    (r"\bc[-\s]*21\b", "le réseau"),
    (r"\bcentury\b", "le réseau"),
]
FORBIDDEN = re.compile(r"\b(century\s*21|century\s*net|centurynet|c21|century)\b", re.IGNORECASE)

def sanitize_brand(text: str) -> str:
    if not text:
        return text
    out = text
    for pattern, repl in REPLACEMENTS:
        out = re.sub(pattern, repl, out, flags=re.IGNORECASE)
    return out
def brand_block(text: str) -> str:
    if not text:
        return text
    if FORBIDDEN.search(text):
        return sanitize_brand(text)
    return text


