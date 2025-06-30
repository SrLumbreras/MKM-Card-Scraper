# 🃏 TCGCollector Scraper

A Python 3 tool to scrape Pokémon card data from [tcgcollector.com](https://www.tcgcollector.com/) for a specific set and user collection, and convert it into structured JSON files for further processing (e.g., generating CardMarket wantlists).

---

## 📦 Features

- Headless scraping of TCGCollector using Selenium
- Outputs:
  - Full card metadata per expansion
  - Clean slug list for downstream processing
- File names include expansion, username, and timestamp

---

## 🛠️ Requirements

- Python 3.7+
- Google Chrome (required by Selenium)

Install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
