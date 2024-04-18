import aiohttp, asyncio, time
import requests
import concurrent.futures
import functools

from settings import *



class RiotData():
    def __init__(self) -> None:
        self.fetch_latest_data()

    def latest_version(self):
        VERSION_API = "https://ddragon.leagueoflegends.com/api/versions.json"
        return requests.get(VERSION_API).json()[0]
    
    def fetch_latest_data(self):
        # Retrieve current version of LOL
        self.latest_version = self.latest_version()

        # Retrieve champions from Riot API
        CHAMPIONS_URL = f"https://ddragon.leagueoflegends.com/cdn/{self.latest_version}/data/en_US/champion.json"
        self.champions = requests.get(CHAMPIONS_URL).json()["data"]

        # Retrieve spells from Riot API
        SPELLS_URL = f"https://ddragon.leagueoflegends.com/cdn/{self.latest_version}/data/en_US/summoner.json"
        self.spells = requests.get(SPELLS_URL).json()["data"]
        
        # Generic Items URL for icon images
        self.ITEMS_URL = f"http://ddragon.leagueoflegends.com/cdn/{self.latest_version}/img/item/"
    

class Player():
    def __init__(self) -> None:
        self.name = None
        self.tag = None
        self.puuid = None
        self.region = None
        self.matches = []

    async def get_matches(self):
        MATCH_V5 = await get_url(riot_api="MATCH_V5", region=self.region)
        self.matches = (await fetch_riot_data(f'{MATCH_V5}by-puuid/{self.puuid}/ids?start=0&count=100&api_key={RIOT_TOKEN}'))


class Match():
    def __init__(self) -> None:
        self.id = None


async def fetch_match_data(match_id, region):
    url = await get_url(riot_api="MATCH_V5", region=region)
    match_data = await fetch_riot_data(f'{url}{match_id}?api_key={RIOT_TOKEN}')
    return match_data



async def fetch_all_matches(match_list, region):
    return_value = {}

    # Processing time 1.25 sec
    async def fetch_and_process(match):
        data = await fetch_match_data(match, region)
        return_value[match] = data

    tasks = [fetch_and_process(match) for match in match_list]
    results = await asyncio.gather(*tasks)

    return return_value
    

async def get_url(riot_api: str = None, region: str = None, version: str = None):

    """https://leagueoflegends.fandom.com/wiki/Servers"""

    regional = {
    "AMERICAS":['BR1','LA1','LA2','NA1',],
    "ASIA":['JP1','KR','PH2','SG2','TW2','TH2','VN2','PH1','SG1','TW1','VN1','TH1'],
    "EUROPE":['EUN1','EUW1','RU1','TR1'],
    "SEA":['OC1']
    }

    regional_choice = next((key for key, regions in regional.items() if region in regions), None)

    urls = {
        'ACCOUNT_V1':f"https://{regional_choice}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/",
        'MATCH_V5':f"https://{regional_choice}.api.riotgames.com/lol/match/v5/matches/",
        'SUMMONER_V4':f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/",
        'CHAMPIONS_URL':f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json",
        'SPELLS_URL':f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/summoner.json",
        'ITEMS_URL':f"http://ddragon.leagueoflegends.com/cdn/{version}/img/item/",
        'VERSION_API':"https://ddragon.leagueoflegends.com/api/versions.json"
    }

    selected_url = next(value for key, value in urls.items() if riot_api in key)

    if selected_url:
        return selected_url
    else:
        raise Exception(f"Unknown Riot API {riot_api}")
    

async def fetch_riot_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 400 or response.status == 404:
                return None
            else:
                raise Exception(f"Riot API request failed with status: {response.status}")
            
