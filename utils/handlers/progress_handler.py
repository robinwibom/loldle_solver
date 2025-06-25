from tqdm import tqdm

class ProgressHandler:
    @staticmethod
    def wrap(sequence, description="Processing"):
        return tqdm(sequence, desc=description)
