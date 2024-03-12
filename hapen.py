from dataclasses import dataclass
from file_management import load_from_url
from random import choice

@dataclass
class Hapen:
    hapens: list[str]

    def __init__(self):
        URL = "https://pastebin.com/raw/KGBi4MQx"
        all_hapens = load_from_url(url=URL)
        all_hapens = all_hapens.replace("\r", "")
        self.hapens = all_hapens.split("\n")


    def get_random_hapen(self) -> str:
        return choice(self.hapens)
