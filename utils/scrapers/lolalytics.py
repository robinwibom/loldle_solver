from typing import List, Optional
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class LolalyticsChampionPage(BaseScraper):
    """
    Fetches and parses champion position data from Lolalytics.
    """
    BASE_URL = "https://lolalytics.com/lol/{}/build/"

    def __init__(self, name: str, session=None, verbose: bool = True):
        super().__init__(name, session, verbose)
        url, resp = self.try_urls(self.BASE_URL)
        if resp:
            self._soup = BeautifulSoup(resp.text, "html.parser")
        else:
            self._soup = None

    @property
    def positions(self) -> Optional[List[str]]:
        """
        Returns a list of positions where play rate >= 20%.
        """
        if not self._soup:
            return None
        results: List[str] = []
        # Each position block is an <a> linking to '/build', containing an <img> and percentage <div>
        for block in self._soup.select("a[href*='/build']"):
            if not (img := block.find("img")):
                continue
            # extract percentage text, strip '%' and convert
            if (pct_text := block.find("div").get_text(strip=True).strip("%")) and (percent := float(pct_text)) >= 20.0:
                pos = img["alt"].replace(" lane", "").capitalize()
                results.append(pos)
        return results