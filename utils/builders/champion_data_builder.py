import requests
from utils.scrapers.ddragon import DDragonChampionList
from utils.scrapers.fandom import FandomChampionPage
from utils.scrapers.lolalytics import LolalyticsChampionPage
from utils.handlers.print_handler import PrintHandler
from utils.handlers.progress_handler import ProgressHandler
from utils.handlers.json_handler import JsonHandler

class ChampionDataBuilder:
    """
    Orchestrates data collection:
    1. DDragon list for basic info
    2. Fandom page for extra fields
    3. Merge and save to JSON
    """
    def __init__(self, output_path="data/champions_data.json", verbose=True):
        self.output_path = output_path
        self.verbose = verbose
        self.session = requests.Session()
        # tracks site-specific URL outcomes
        self.url_report: dict[str, dict[str, list[str] | str]] = {}

    def run(self):
        PrintHandler.header("LoLdle Solver: Champion Data Build")

        # 1. DDragon
        PrintHandler.section("Step 1: DDragon basic info")
        ddragon = DDragonChampionList(session=self.session, verbose=self.verbose)
        champions = ddragon.fetch_all_champions()

        # 2 & 3. Fandom enrichment + Lolalytics positions in one loop
        PrintHandler.section("Step 2: Enrich and fetch positions")
        fandom_report: dict[str, dict] = {}
        lol_report: dict[str, dict] = {}

        i = 0

        for champ in ProgressHandler.wrap(champions, description="Processing champions"):
            # Fandom
            fpage = FandomChampionPage(champ['name'], session=self.session, verbose=self.verbose)
            fandom_report[champ['name']] = {'failed': fpage.failed_urls, 'success': fpage.success_url}
            if champ.get('gender') is None:
                champ['gender'] = fpage.gender
            champ['region'] = fpage.region
            champ['species'] = fpage.species

            # Lolalytics
            lpage = LolalyticsChampionPage(champ['name'], session=self.session, verbose=self.verbose)
            lol_report[champ['name']] = {'failed': lpage.failed_urls, 'success': lpage.success_url}
            champ['positions'] = lpage.positions or []

            i += 1
            if i >= 120:
                break

        self.url_report['fandom'] = fandom_report
        self.url_report['lolalytics'] = lol_report

        # 4. Save outputs
        JsonHandler.save(self.output_path, champions)
        report_path = self.output_path.replace("champions_data.json", "url_report.json")
        JsonHandler.save(report_path, self.url_report)
        PrintHandler.success(f"Saved champion data to {self.output_path}")
        PrintHandler.success(f"Saved URL report to {report_path}")

if __name__ == "__main__":
    print("hello world")
    exit()
    builder = ChampionDataBuilder()
    builder.run()