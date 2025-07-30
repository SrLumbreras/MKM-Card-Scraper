
from enum import Enum
import re
from typing import List


class CardType(Enum):
    Pokemon = 1
    Trainer = 2
    Energy = 3
    VSTAR = 4

def define_card_type(card_name: str) -> CardType:
    """Determine the type of card based on its name."""
    if "VSTAR" in card_name:
        return CardType.VSTAR
    elif "Trainer" in card_name:
        return CardType.Trainer
    elif "Energy" in card_name:
        return CardType.Energy
    else:
        return CardType.Pokemon
    
def extract_card_info(card_content: List) -> str:
    """
    Extrae nombre del Pokémon, habilidad (si hay) y ataques de una carta.
    Si hay una habilidad, se toma solo la línea donde aparece.
    Luego se eliminan símbolos, flechas, y cualquier cosa después del primer número.
    """
    result = ""
    for element in card_content:
        raw_text = element.text.strip()
        # Eliminar símbolos de energía como {G}, {C}, etc.
        cleaned = re.sub(r"\{[\w\s\n]+\}", "", raw_text)

        # Eliminar palabra "Ability" y símbolos → ⇢ :
        cleaned = re.sub(r"\bAbility\b", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"[→⇢:]", "", cleaned)

        # Eliminar "VSTAR Power" si está presente        
        cleaned = re.sub(r"\bVSTAR Power\b", "", cleaned, flags=re.IGNORECASE)

        lines = cleaned.splitlines()
        lines = list(filter(None, lines))  # Eliminar líneas vacías

        # Eliminar todo lo que venga después del primer número
        cleaned = re.split(r"\d+", lines[0], maxsplit=1)[0]

        # # Si contiene una habilidad, quedarse solo con la línea que la contiene
        # for line in lines:
        #     if "Ability" in line:
        #         raw_text = line
        #         break

        # Reemplazar saltos de línea y múltiples espacios por uno solo
        cleaned = re.sub(r"\s+", " ", cleaned)
        if cleaned : result += f" {cleaned.strip()}"

    return result.strip()