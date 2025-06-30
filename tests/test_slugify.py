import pytest
from tcgcollector_scraper.utils.slugify import slugify

@pytest.mark.parametrize("input_text,expected_slug", [
    ("Hola Mundo", "hola-mundo"),
    ("áéíóú ñ Ñ", "aeiou-n-n"),
    ("   Espacios   múltiples   ", "espacios-multiples"),
    ("Símbolos!@#$%^&*", "simbolos"),
    ("123 números", "123-numeros"),
    ("Slugify--prueba__extraña", "slugify-prueba-extrana"),
    ("", ""),
])
def test_slugify(input_text, expected_slug):
    assert slugify(input_text) == expected_slug
