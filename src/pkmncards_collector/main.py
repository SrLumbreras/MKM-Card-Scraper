from enum import Enum
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List
from src.utils.cardUtils import *

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from ratelimit import limits, sleep_and_retry

class PKMNCardScraper:
    """
    Scrapes card data from pkmncards.com based on a list of slugs.
    """

    BASE_URL = "https://pkmncards.com/card"
    RATE_LIMIT_CALLS = 5
    RATE_LIMIT_PERIOD = 10  # seconds

    def __init__(self, input_path: Path, output_dir: Path = Path("data")) -> None:
        self.input_path = input_path
        self.output_dir = output_dir
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results: List[str] = []
        self.driver = self._init_driver()

    def _init_driver(self) -> webdriver.Chrome:
        """Initialize a headless Chrome WebDriver instance."""
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")

        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

    def load_slugs(self) -> List[str]:
        """Load card slugs from input JSON file."""
        with self.input_path.open(encoding="utf-8") as f:
            return json.load(f)

    def run(self, max_cards: int = None) -> None:
        """Execute the scraping routine."""
        slugs = self.load_slugs()
        if max_cards:
            slugs = slugs[:max_cards]

        try:
            for index, slug in enumerate(slugs):
                card_text = self._scrape_card(slug)
                if card_text:
                    self.results.append(card_text)
                    logging.info("[%d] %s", index + 1, card_text)

        except Exception as exc:
            logging.error("Unexpected error: %s", exc)

        finally:
            self.driver.quit()
            self._save_results()

    @sleep_and_retry
    @limits(calls=RATE_LIMIT_CALLS, period=RATE_LIMIT_PERIOD)
    def _scrape_card(self, slug: str) -> str:
        """Fetch and parse card information for a given slug."""
        try:
            url = f"{self.BASE_URL}/{slug}/"
            self.driver.get(url)

            card_type_elem = self.driver.find_element(By.CSS_SELECTOR, ".type-evolves-is span a")
            card_type = define_card_type(card_type_elem.text.strip())
            card_name = self.driver.find_element(By.CSS_SELECTOR, ".name").text.strip()
            text_elements = self.driver.find_elements(By.CSS_SELECTOR, ".text p")

            card_body = card_name
            match card_type:
                case CardType.Pokemon:
                    card_body += f" {extract_card_info(text_elements)}"
                    # for element in text_elements:
                    #     raw_text = element.text.strip()
                    #     card_body += f" {extract_card_info(raw_text)}"
                case CardType.VSTAR:
                    card_body += f" {extract_card_info(text_elements)}"                   

            return card_body

        except Exception as e:
            logging.error("Failed to scrape slug '%s': %s", slug, e)
            return ""

    def _save_results(self) -> None:
        """Write results to a .txt file."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_file = self.output_dir / f"pkmncards_{self.timestamp}.txt"

        with output_file.open("w", encoding="utf-8") as f:
            for card_text in self.results:
                f.write(f"{card_text}\n")

        logging.info("[\u2713] Results saved to %s", output_file)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # INPUT_FILE = Path("data/brilliant-stars_20250730_140329.json")
    INPUT_FILE = Path("data/testFile.json")
    scraper = PKMNCardScraper(INPUT_FILE)
    # scraper.run(max_cards=5)
    scraper.run()
