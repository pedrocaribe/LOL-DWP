import os

SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SETTINGS_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "data")

ACCOUNT_V1 = os.getenv("ACCOUNT_V1", False)
SUMMONER_V4 = os.getenv("SUMMONER_V4")
MATCH_V5 = os.getenv("MATCH_V5", False)

RIOT_TOKEN = os.getenv("RIOT_TOKEN", False)
