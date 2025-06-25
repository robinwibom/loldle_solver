from utils.loaders.basic_info_loader import BasicInfoLoader
from utils.loaders.gender_updater import GenderUpdater
from utils.loaders.position_updater import PositionUpdater
from utils.handlers.print_handler import PrintHandler
from utils.handlers.json_handler import JsonHandler

class ChampionDataBuilder:
    def __init__(self, output_path="data/champions_data.json", verbose=True):
        self.output_path = output_path
        self.verbose = verbose
        self.version = None
        self.champions = []

    def run(self):
        PrintHandler.header("LoLdle Solver: Champion Data Build")

        # Step 1: Load basic info
        PrintHandler.section("Step 1: Basic Info")
        self.version, self.champions = BasicInfoLoader(verbose=self.verbose).run()

        # Step 2: Update gender
        PrintHandler.section("Step 2: Gender Updater")
        GenderUpdater(self.champions, verbose=self.verbose).run()

        # Step 3: Update positions
        PrintHandler.section("Step 3: Position Updater")
        PositionUpdater(self.champions, verbose=self.verbose).run()

        # Final save
        JsonHandler.save(self.output_path, {
            "version": self.version,
            "champions": self.champions
        })

        PrintHandler.success(f"Saved {len(self.champions)} champions to {self.output_path}")
        PrintHandler.header("Build completed")
