import re
from typing import List, Optional
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class FandomChampionPage(BaseScraper):
    BASE_URL = "https://leagueoflegends.fandom.com/wiki/{}"
    GENDER_MAP = {"she": "Female", "her": "Female", "he": "Male", "his": "Male"}

    def __init__(self, name, session=None, verbose=True):
        super().__init__(name, session, verbose)
        url, resp = self.try_urls(self.BASE_URL)
        self._soup = BeautifulSoup(resp.text, "html.parser") if resp else None
        lol_url, resp_lol = self.try_urls(self.BASE_URL + "/LoL")
        self._soup_lol = BeautifulSoup(resp_lol.text, "html.parser") if resp_lol else None

    @property
    def gender(self) -> str:
        """Extract pronouns from div[data-source='pronoun'] and map to Male/Female/Other."""
        if not self._soup:
            return None

        # 1. Select the data-value node under the pronoun block
        node = self._soup.select_one('div[data-source="pronoun"] .pi-data-value')
        if not node:
            return None

        pronouns = node.get_text(strip=True).lower()  # e.g. "he/him"
        # 2. Split and map
        for part in re.split(r"[/,]", pronouns):
            key = part.strip()
            if key in self.GENDER_MAP:
                return self.GENDER_MAP[key]

        # 3. Fallback
        return "Other"

    @property
    def region(self) -> Optional[List[str]]:
        return self.extract_infobox_list("region", self._soup)
    
    @property
    def origin(self) -> Optional[List[str]]:
        return self.extract_infobox_list("originplace", self._soup)
    
    @property
    def residence(self) -> Optional[List[str]]:
        return self.extract_infobox_list("residence", self._soup)

    @property
    def species(self) -> Optional[List[str]]:
        return self.extract_infobox_list("species", self._soup)
    
    @property
    def release_date(self) -> Optional[str]:
        return self.extract_infobox_list("release", self._soup_lol)

    @property
    def range_type(self) -> Optional[str]:
        return self.extract_infobox_list("rangetype", self._soup_lol)