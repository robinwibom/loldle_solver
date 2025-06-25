import requests
from bs4 import BeautifulSoup
from utils.handlers.print_handler import PrintHandler
from utils.handlers.progress_handler import ProgressHandler
from utils.loaders.base_loader import BaseLoader

class GenderEnricher(BaseLoader):
    BASE_URL = "https://lol.fandom.com/wiki/"

    def fetch_pronouns(self, champ_name):
        url_template = f"{self.BASE_URL}{{}}"
        url, response = self.try_urls(url_template, champ_name)
        if not response:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        if not (cell := next((c for c in soup.select("table.infobox td.infobox-label")
                            if "pronouns" in c.get_text(strip=True).lower()), None)):
            return None

        key = next((w.strip() for w in cell.find_next_sibling("td").get_text(strip=True).lower().split("/") if w.strip()), "")
        return self.GENDER_MAP.get(key, "Other")



    def run(self):
        PrintHandler.section("Enriching Genders")
        count, errors = 0, 0

        for champ in ProgressHandler.wrap(self.champions, description="Enriching genders"):
            if (current_gender := champ.get("gender", "").lower()) in ["female", "male"]:
                continue

            try:
                if fandom_gender := self.fetch_pronouns(champ["name"]):
                    champ["gender"] = fandom_gender
                    count += 1
                    self.success(f"{champ['name']} → {fandom_gender}")
            except Exception as e:
                errors += 1
                PrintHandler.error(f"{champ['name']} → ERROR: {e}")

        self.log(f"Gender enrichment completed. {count} champions updated, {errors} errors.")