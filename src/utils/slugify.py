import re
import unicodedata

def slugify(text: str) -> str:
    """
    Converts a string into a URL-friendly slug:
    - Lower-cases characters
    - Removes diacritical marks
    - Replaces non-alphanumerics with hyphens
    - Collapses multiple hyphens and trims edges
    """
    text = text.lower()
    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-{2,}", "-", text).strip("-")
