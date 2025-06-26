import re
import requests
from bs4 import BeautifulSoup
from utils.handlers.print_handler import PrintHandler

class BaseScraper():
    """
    Base class for all scrapers:
    - Maintains a shared HTTP session
    - Provides slugification for champion names
    - Retry logic over URL variants
    - Logging via PrintHandler
    """
    def __init__(self, name: str, session: requests.Session = None, verbose: bool = True):
        self.name = name
        self.session = session or requests.Session()
        self.verbose = verbose
        self._soup: BeautifulSoup | None = None
        self.failed_urls: list[str] = []
        self.success_url: str | None = None

    def log(self, msg: str, indent: int=0):
        if self.verbose:
            PrintHandler.info(msg, indent)
    
    def success(self, msg: str, indent: int=0):
        if self.verbose:
            PrintHandler.success(msg, indent=0)

    def error(self, msg: str, indent=0):
        if self.verbose:
            PrintHandler.error(msg, indent=0)

    def slugify(self) -> list[str]:
        """
        Generate slug variants for this.name in order:
        1) spaces → underscores (preserve case)
        2) lowercase
        3) cleaned (alphanumeric + underscore)
        4) collapse runs of underscores
        5) concatenated (remove all underscores)
        6) first-word fallback
        """
        name = self.name

        # 1) spaces → underscores
        original     = name.replace(" ", "_")
        # 2) lowercase
        lower        = original.lower()
        # 3) keep only a–z, 0–9, and underscore
        cleaned      = re.sub(r"[^a-z0-9_]", "", lower)
        # 4) collapse any run of underscores into one
        collapsed    = re.sub(r"_+", "_", cleaned)
        # 5) concatenated (no underscores)
        concatenated = collapsed.replace("_", "")
        # 6) first-word fallback
        first_word   = collapsed.split("_", 1)[0] if "_" in collapsed else None

        candidates = (original, lower, cleaned, collapsed, concatenated, first_word)
        # dedupe while preserving order
        return [v for v in dict.fromkeys(filter(None, candidates))]
    
    def try_urls(self, template: str) -> tuple[str | None, requests.Response | None]:
        """
        Attempt each slug in template.format(slug):
        - record failures in self.failed_urls
        - record the first successful URL in self.success_url
        """
        for slug in self.slugify():
            url = template.format(slug)
            resp = self.session.get(url)
            if resp.ok:
                self.success_url = url
                self.success(f"Fetched URL: {url}")
                return url, resp
            self.failed_urls.append(url)
        self.error(f"All URL attempts failed for {self.name}")
        return None, None
    
    def extract_infobox_list(self,
                              data_source: str,
                              soup: BeautifulSoup | None = None) -> list[str] | None:
        """
        Generic infobox list extractor:
        - Finds <div data-source="{data_source}"> .pi-data-value container
        - Handles <li> entries, inline <a> links, and text fallback
        - Skips any items or links inside <s> (strikethrough)
        Returns a list of strings, or None if the block is missing.
        """

        # 1) assign 'tree' to the passed soup or the main self._soup
        if (tree := soup or self._soup) is None:
            return None

        # 2) locate container
        selector = f'div[data-source="{data_source}"] .pi-data-value'
        if not (container := tree.select_one(selector)):
            return None

        results: list[str] = []

        # 3) Case A: list items
        if items := container.select("li"):
            for li in items:
                if li.find("s"):
                    continue
                for a in li.find_all("a"):
                    text = a.get_text(strip=True)
                    if not text or a.find_parent("s"):
                        continue
                    results.append(text)
            return results

        # 4) Case B: inline links
        if links := container.find_all("a"):
            for a in links:
                text = a.get_text(strip=True)
                if not text or a.find_parent("s"):
                    continue
                results.append(text)
            return results

        # 5) Case C: fallback to text
        raw = container.get_text(" ", strip=True)
        return [p.strip() for p in re.split(r"[;/,()]+", raw) if p.strip()]