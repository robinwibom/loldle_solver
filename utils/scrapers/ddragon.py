import requests
from typing import Optional
from utils.handlers.print_handler import PrintHandler
from utils.handlers.progress_handler import ProgressHandler

class DDragonChampionList():
    """
    Fetches the latest Data Dragon version and downloads
    the champion list with basic properties (name & resource).
    """
    VERSIONS_URL = "https://ddragon.leagueoflegends.com/api/versions.json"
    BASE_URL = "https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
    GENDER_MAP   = {
        "she": "Female",
        "her": "Female",
        "he":  "Male",
        "his": "Male",
    }

    def __init__(self, session=None, verbose=True):
        self.session = session or requests.Session()
        self.verbose = verbose
        self.version = None

    def fetch_latest_version(self) -> str:
        PrintHandler.info("FQetching latest DDragon version...")
        resp = self.session.get(self.VERSIONS_URL)
        resp.raise_for_status()
        version = resp.json()[0]
        PrintHandler.success(f"Latest version: {version}")
        return version
    
    def guess_gender(self, blurb: str) -> Optional[str]:
        """
        Scan the blurb for any known pronoun keywords and map to Male/Female.
        """
        text = blurb.lower()
        for key, gender in self.GENDER_MAP.items():
            # look for standalone words, not substrings
            if f" {key} " in f" {text} ":
                return gender
        return None

    def fetch_all_champions(self) -> list[dict]:
        if not self.version:
            self.version = self.fetch_latest_version()
        url = self.BASE_URL.format(version=self.version)
        PrintHandler.info(f"Downloading champion data for patch {self.version}...")
        resp = self.session.get(url)
        resp.raise_for_status()
        data = resp.json().get("data", {})
        champions = []
        for champ in ProgressHandler.wrap(data.values(), description="Parsing champions"):
            blurb = champ.get("blurb", "")
            gender = self.guess_gender(blurb)

            champions.append({
                "name": champ.get("name"),
                "resource": champ.get("partype"),
                "gender": gender
            })
        PrintHandler.success(f"Loaded {len(champions)} champions from DDragon.")
        return champions