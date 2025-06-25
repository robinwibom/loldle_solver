import re
import requests
from utils.handlers.print_handler import PrintHandler

class BaseLoader:
    GENDER_MAP = {
        "she": "Female",
        "her": "Female",
        "he": "Male",
        "his": "Male",
    }

    def __init__(self, champions=None, verbose=True):
        self.champions = champions or []
        self.verbose = verbose

    def log(self, message, indent=0):
        if self.verbose:
            PrintHandler.info(message, indent=indent)

    def success(self, message, indent=0):
        if self.verbose:
            PrintHandler.success(message, indent=indent)

    def make_slug_variants(self, name):
        base = re.sub(r"[^a-zA-Z0-9\s]", "", name).strip().lower()
        parts = base.split()
        variants = []

        # If '&' is present -> add first part first
        if "&" in name:
            first = name.split("&")[0].strip()
            first_slug = re.sub(r"[^a-zA-Z0-9]", "", first).lower()
            variants.append(first_slug)

        # Single word
        if len(parts) == 1:
            variants.append("".join(parts))
        else:
            variants.append("".join(parts))    # full slug first
            variants.append(parts[0])          # first word

        return list(dict.fromkeys(variants))

    
    def try_urls(self, url_template, champ_name):
        for slug in self.make_slug_variants(champ_name):
            url = url_template.format(slug)
            if (response := requests.get(url)).ok:
                return url, response
        PrintHandler.error(f"Failed to find URL for {champ_name}")
        return None, None


