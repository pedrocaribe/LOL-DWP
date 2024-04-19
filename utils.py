import aiohttp, asyncio, time
import requests
import concurrent.futures
import functools

from settings import *


from contextlib import contextmanager


def duration(func):
    @contextmanager
    def wrapping_logic():
        start_ts = time.time()
        yield
        dur = time.time() - start_ts
        print('Function {} took {:.2} seconds to execute'.format(func.__name__, dur))

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not asyncio.iscoroutinefunction(func):
            with wrapping_logic():
                return func(*args, **kwargs)
        else:
            async def tmp():
                with wrapping_logic():
                    return (await func(*args, **kwargs))
            return tmp()
    return wrapper


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
    

async def create_player():
    created_dict = {}
    return created_dict
    
async def get_matches(player):
    MATCH_V5 = await get_url(riot_api="MATCH_V5", region=player["region"])
    player["matches"] = (await fetch_riot_data(f'{MATCH_V5}by-puuid/{player["puuid"]}/ids?start=0&count=100&api_key={RIOT_TOKEN}'))


class Match():
    def __init__(self, id , data, players) -> None:
        self.id = id
        self.data = data
        self.players = players
    
    async def process_match_data(self):
        
        # Player 1
        self.idx_p1 = self.data['metadata']['participants'].index(self.players['player1']['puuid'])
        self.stats_p1 = self.data['info']['participants'][self.idx_p1]
        self.level_p1 = self.stats_p1['champLevel']
        self.champion_id_p1 = self.stats_p1['championId']
        self.champion_name_p1 = self.stats_p1['championName']
        self.lane_position_p1 = self.stats_p1['lane']
        self.items_p1 = ['{}'.format(self.stats_p1["item{}".format(i)]) for i in range(7)]
        self.team_id_p1 = self.stats_p1['teamId']
        self.win_lose_p1 = self.stats_p1['win']
        self.kills_p1 = self.stats_p1['kills']
        self.deaths_p1 = self.stats_p1['deaths']
        self.assists_p1 = self.stats_p1['assists']
        self.kda_p1 = ((self.kills_p1 + self.assists_p1)/max(self.deaths_p1, 1))

        # Player 2
        self.idx_p2 = self.data['metadata']['participants'].index(self.players['player2']['puuid'])
        self.stats_p2 = self.data['info']['participants'][self.idx_p2]
        self.level_p2 = self.stats_p2['champLevel']
        self.champion_id_p2 = self.stats_p2['championId']
        self.champion_name_p2 = self.stats_p2['championName']
        self.lane_position_p2 = self.stats_p2['lane']
        self.items_p2 = ['{}'.format(self.stats_p2["item{}".format(i)]) for i in range(7)]
        self.team_id_p2 = self.stats_p2['teamId']
        self.win_lose_p2 = self.stats_p2['win']
        self.kills_p2 = self.stats_p2['kills']
        self.deaths_p2 = self.stats_p2['deaths']
        self.assists_p2 = self.stats_p2['assists']
        self.kda_p2 = ((self.kills_p2 + self.assists_p2)/max(self.deaths_p2, 1))

        # Match
        self.same_team = True if self.win_lose_p1 == self.win_lose_p2 else False
        self.creation = self.data['info']['gameCreation'] # Transform into readable time
        self.duration = self.data['info']['gameDuration'] # Transform into readable time
        self.game_mode = self.data['info']['gameMode']



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
    
@duration
async def fetch_riot_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 400 or response.status == 404:
                return None
            else:
                raise Exception(f"Riot API request failed with status: {response.status}")
            
