import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from src.utils.slugify import slugify


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


@dataclass
class Card:
    title: str
    name: str
    number: str
    expansion: str
    code: str
    slug: str


class TCGCollectorScraper:
    """
    Scraper for TCG Collector sets.
    """

    DEFAULT_WAIT: int = 10

    def __init__(self, url: str, output_dir: Path = Path("data")) -> None:
        self.url = url
        self.output_dir = output_dir
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.expansion_slug = ""
        self.cards: List[Card] = []
        self.driver = self._init_driver()

    def _init_driver(self) -> webdriver.Chrome:
        """Initialize Chrome WebDriver with options."""
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        return driver

    def run(self) -> None:
        """Execute the full scraping workflow."""
        try:
            self.driver.get(self.url)
            self._wait_for_cards()
            self._extract_cards()
            self._save_results()
        except Exception as exc:
            logging.error("An error occurred: %s", exc)
        finally:
            self.driver.quit()

    def _wait_for_cards(self) -> None:
        """Wait until card elements are present on the page."""
        WebDriverWait(self.driver, self.DEFAULT_WAIT).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".card-list-item"))
        )
        logging.info("Card elements loaded.")

    def _extract_cards(self) -> None:
        """Extract card details and build Card objects."""
        elements = self.driver.find_elements(By.CSS_SELECTOR, ".card-list-item")
        if not elements:
            raise ValueError("No cards found on the page.")

        # Derive expansion slug
        raw_expansion = elements[0].find_element(
            By.CSS_SELECTOR, ".card-list-item-expansion-name"
        ).text.strip()
        self.expansion_slug = slugify(raw_expansion)
        logging.info("Expansion slug: %s", self.expansion_slug)

        for element in elements:
            try:
                card = self._parse_card_element(element)
                self.cards.append(card)
            except Exception as parse_exc:
                logging.warning("Failed to parse a card: %s", parse_exc)

        logging.info("Parsed %d cards.", len(self.cards))

    def _parse_card_element(self, element: webdriver.remote.webelement.WebElement) -> Card:
        """Parse a single card element into a Card dataclass."""
        link_elem = element.find_element(By.CSS_SELECTOR, ".card-list-item-card-name a")
        name = link_elem.text.strip()
        full_title = link_elem.get_attribute("title").strip()

        number_raw = element.find_element(
            By.CSS_SELECTOR, ".card-list-item-card-number span"
        ).text.strip()
        number = number_raw.split("/")[0]

        expansion_name = element.find_element(
            By.CLASS_NAME, "card-list-item-expansion-name"
        ).text.strip()
        code = element.find_element(
            By.CLASS_NAME, "card-list-item-expansion-code"
        ).text.strip()

        slug_parts = [
            slugify(name),
            slugify(expansion_name),
            code.lower(),
            slugify(number)
        ]
        slug = "-".join(slug_parts)

        return Card(
            title=full_title,
            name=name,
            number=number_raw,
            expansion=expansion_name,
            code=code,
            slug=slug
        )

    def _save_results(self) -> None:
        """Save raw card data and slugs to JSON files."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        raw_filename = f"{self.expansion_slug}_{self.timestamp}_raw.json"
        slug_filename = f"{self.expansion_slug}_{self.timestamp}.json"

        raw_path = self.output_dir / raw_filename
        slug_path = self.output_dir / slug_filename

        # Write full data
        with raw_path.open("w", encoding="utf-8") as f:
            json.dump([asdict(card) for card in self.cards], f, indent=2, ensure_ascii=False)
        logging.info("Raw data saved to %s", raw_path)

        # Write only slugs
        with slug_path.open("w", encoding="utf-8") as f:
            json.dump([card.slug for card in self.cards], f, indent=2, ensure_ascii=False)
        logging.info("Slug list saved to %s", slug_path)


if __name__ == "__main__":
    TARGET_URL = (
        "https://www.tcgcollector.com/sets/11453/brilliant-stars"
        "?releaseDateOrder=newToOld&displayAs=list"
        "&cardSource=notInCardCollection&sortBy=cardNumber&viewUser=Lumbreras"
    )
    scraper = TCGCollectorScraper(TARGET_URL)
    scraper.run()
