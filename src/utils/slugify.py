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

def extract_card_info(raw_text: str) -> str:
    """
    Extrae nombre del Pokémon, habilidad (si hay) y ataques de una carta.
    Si hay una habilidad, se toma solo la línea donde aparece.
    Luego se eliminan símbolos, flechas, y cualquier cosa después del primer número.
    """
    lines = raw_text.splitlines()

    # Si contiene una habilidad, quedarse solo con la línea que la contiene
    for line in lines:
        if "Ability" in line:
            raw_text = line
            break

    # Eliminar todo lo que venga después del primer número
    raw_text = re.split(r"\d+", raw_text, maxsplit=1)[0]

    # Eliminar símbolos de energía como {G}, {C}, etc.
    cleaned = re.sub(r"\{[\w\s\n]+\}", "", raw_text)

    # Eliminar palabra "Ability" y símbolos → ⇢ :
    cleaned = re.sub(r"\bAbility\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"[→⇢:]", "", cleaned)

    # Reemplazar saltos de línea y múltiples espacios por uno solo
    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned.strip()
