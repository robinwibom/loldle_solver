import re
import requests
from bs4 import BeautifulSoup
from utils.handlers.print_handler import PrintHandler
from utils.handlers.progress_handler import ProgressHandler
from utils.loaders.base_loader import BaseLoader

class PositionEnricher(BaseLoader):
    BASE_URL = "https://lolalytics.com/lol/"

    def slugify(self, name):
        return re.sub(r"[^a-zA-Z0-9]", "", name.lower())

    def fetch_positions(self, champ_name):
        url_template = f"{self.BASE_URL}{{}}/build/"
        url, response = self.try_urls(url_template, champ_name)
        if not response:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        positions = []

        for block in soup.select("a[href*='/build']"):
            if not (img := block.find("img")):
                continue

            if (percent := float(block.find("div").get_text(strip=True).strip("%"))) >= 20.0:
                position = img["alt"].replace(" lane", "").capitalize()
                positions.append(position)

        return positions

    def run(self):
        PrintHandler.section("Enriching Positions")
        count = 0

        for champ in ProgressHandler.wrap(self.champions, description="Enriching positions"):
            if champ.get("positions"):
                continue

            try:
                if positions := self.fetch_positions(champ["name"]):
                    champ["positions"] = positions
                    count += 1
                    self.success(f"{champ['name']} → {positions}")
            except Exception as e:
                errors += 1
                PrintHandler.error(f"{champ['name']} → ERROR: {e}")

        PrintHandler.info(f"Position enrichment completed. {count} champions updated.")
