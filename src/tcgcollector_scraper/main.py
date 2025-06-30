import json
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from src.utils.slugify import slugify


# Target URL (set + user filter)
url = (
    "https://www.tcgcollector.com/sets/11453/brilliant-stars"
    "?releaseDateOrder=newToOld&displayAs=list"
    "&cardSource=notInCardCollection&sortBy=cardNumber&viewUser=Lumbreras"
)

# Extract values for file naming
parsed = urlparse(url)
query_params = parse_qs(parsed.query)
username = query_params.get("viewUser", ["unknown"])[0]
expansion_slug = Path(parsed.path).parts[-1]
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

try:
    driver.get(url)
    time.sleep(3)  # wait for JS‑rendered list

    cards = driver.find_elements(By.CSS_SELECTOR, ".card-list-item")
    data = []

    for card in cards:
        try:
            link_elem = card.find_element(By.CSS_SELECTOR, ".card-list-item-card-name a")
            name = link_elem.text.strip()
            full_title = link_elem.get_attribute("title").strip()

            number_raw = card.find_element(
                By.CSS_SELECTOR, ".card-list-item-card-number span"
            ).text.strip()
            number = number_raw.split("/")[0]

            expansion = card.find_element(
                By.CLASS_NAME, "card-list-item-expansion-name"
            ).text.strip()
            code = card.find_element(
                By.CLASS_NAME, "card-list-item-expansion-code"
            ).text.strip()

            slug = f"{slugify(name)}-{slugify(expansion)}-{code.lower()}-{slugify(number)}"

            data.append(
                {
                    "title": full_title,
                    "name": name,
                    "number": number_raw,
                    "expansion": expansion,
                    "code": code,
                    "slug": slug,
                }
            )

        except Exception:
            print(f"error!!")
            pass

finally:
    driver.quit()

# Output paths
raw_path = Path(f"data/{expansion_slug}_{username}_{timestamp}_raw.json")
slug_path = Path(f"data/{expansion_slug}_{username}_{timestamp}.json")

with raw_path.open("w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

with slug_path.open("w", encoding="utf-8") as f:
    json.dump([item["slug"] for item in data], f, indent=2, ensure_ascii=False)
