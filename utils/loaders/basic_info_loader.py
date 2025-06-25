import re
import requests
from utils.handlers.print_handler import PrintHandler
from utils.handlers.progress_handler import ProgressHandler
from utils.loaders.base_loader import BaseLoader

class BasicInfoLoader(BaseLoader):
    ROLE = "Loader"
    BASE_URL = "https://ddragon.leagueoflegends.com/cdn"
    VERSIONS_URL = "https://ddragon.leagueoflegends.com/api/versions.json"

    def __init__(self, verbose=True):
        super().__init__(verbose=verbose)
        self.version = self.fetch_latest_version()

    def fetch_latest_version(self):
        PrintHandler.section("Loading Basic Champion Info")
        self.log("Fetching latest DDragon version...")
        if not (response := requests.get(self.VERSIONS_URL)).ok:
            PrintHandler.error(f"Failed to fetch DDragon versions (status {response.status_code})")
            return "latest"
        latest_version = (versions := response.json())[0]
        PrintHandler.success(f"Latest version: {latest_version}")
        return latest_version

    def fetch_champion_data(self):
        url = f"{self.BASE_URL}/{self.version}/data/en_US/champion.json"
        self.log(f"Fetching champion data for patch {self.version}...")
        if not (response := requests.get(url)).ok:
            PrintHandler.error(f"Failed to fetch DDragon data (status {response.status_code})")
            return None
        return response.json()

    def guess_gender(self, blurb: str):
        b = blurb.lower()
        key = next((w.strip() for w in b.split() if w.strip() in self.GENDER_MAP), "")
        return self.GENDER_MAP.get(key, "")

    def build_champion_list(self, raw_data):
        champions = []
        data = raw_data.get("data", {})
        for champ in ProgressHandler.wrap(data.values(), description="Parsing champions"):
            champions.append({
                "name": champ.get("name"),
                "resource": champ.get("partype"),
                "tags": champ.get("tags", []),
                "gender": self.guess_gender(champ.get("blurb", ""))
            })
        return champions

    def run(self):
        raw_data = self.fetch_champion_data() or {}
        champions = self.build_champion_list(raw_data)
        PrintHandler.success(f"Loaded {len(champions)} champions")
        return self.version, champions

