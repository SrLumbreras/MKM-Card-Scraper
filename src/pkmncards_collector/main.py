import json
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from src.utils.slugify import extract_card_info

import requests


base_url = "https://pkmncards.com/card"

# Extract values for file naming
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
title_pattern = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")  # usa "--headless" si tu Chrome es viejo
options.add_argument("--disable-gpu")   # recomendable en Windows
options.add_argument("--no-sandbox")    # a veces necesario en algunos entornos
options.add_argument("--window-size=1920,1080")  # previene errores de renderizado

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

input_slug_file = Path("data/brilliant-stars_Lumbreras_20250630_115249.json")

with input_slug_file.open(encoding="utf-8") as f:
    slugs = json.load(f)

results = []

try:
    # for slug in slugs :
    for index, slug in zip(range(5), slugs) :
        url = f"{base_url}/{slug}/"

        driver.get(url)
        card_type = driver.find_element(By.CSS_SELECTOR, ".type-evolves-is span a")
        card_name = driver.find_element(By.CSS_SELECTOR, ".name").text.strip()
        text_goal = ".text p"
        if card_type.text == "Trainer" :
            text_goal = ".text p"

        text_contents = driver.find_elements(By.CSS_SELECTOR, text_goal)
        # text_contents = text_box.find_elements(By., "p")
        card_body = card_name
        if (not card_type.text == "Trainer") :
            for content in text_contents:
                raw_text = content.text.strip()
                # print(f"[DEBUG] {raw_text}")
                card_body += f" {extract_card_info(raw_text)}"
# card_type.text != "Trainer"
        # print(f"[OK] [{card_body}] {slug}")
        print(f"[OK] [{card_body}]")
        results.append(card_body)

        time.sleep(0.5)  # evita rate limiting
except Exception as e:
    print(f"[ERROR] {slug}: {e}")

finally:
    driver.quit()

output_file = Path(f"data/pkmncards_{timestamp}.txt")
# Guardar resultados
with output_file.open("w", encoding="utf-8") as f:
    for card in results:
        f.write(f"{card}\n")
        
print(f"\n[✓] Guardado en {output_file}")