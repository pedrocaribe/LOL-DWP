
import asyncio, time, datetime, requests, functools, logging

from settings import *
from classes import Player


from contextlib import contextmanager
from datetime import datetime
from typing import Awaitable, Any
from colorama import Back, Fore,Style
from fastapi import FastAPI


# Console Styling
fy = Fore.YELLOW
fw = Fore.WHITE
fg = Fore.GREEN
fr = Fore.RED
bg = Back.GREEN
br = Back.RED
bb = Back.BLACK
bw = Back.WHITE
bres = Back.RESET
sb = Style.BRIGHT
sres = Style.RESET_ALL


def duration(func):
    @contextmanager
    def wrapping_logic():
        start_ts = time.time()
        yield
        dur = time.time() - start_ts
        logging.info('Function {} took {:.2} seconds to execute'.format(func.__name__, dur)) # Logging

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


# Asyncio function to run functions in parallel thread
@duration
async def run_parallel(*functions: Awaitable[Any]) -> None:
    await asyncio.gather(*functions)

# Function to run functions in sequence
@duration
async def run_sequence(*functions: Awaitable[Any]) -> None:
    for function in functions:
        await function


async def ddragon_data(app: FastAPI) -> dict:

    VERSION_API = "https://ddragon.leagueoflegends.com/api/versions.json"
    latest_version = requests.get(VERSION_API).json()[0]

    CHAMPIONS_URL = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion.json"
    SPELLS_URL = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/summoner.json"
    ITEMS_URL = f"http://ddragon.leagueoflegends.com/cdn/{latest_version}/img/item/"
    RUNES_URL = f"http://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/runesReforged.json"
    
    
    champions = (await fetch_riot_data(url=CHAMPIONS_URL, app=app))["data"]
    spells = (await fetch_riot_data(url=SPELLS_URL, app=app))["data"]
    runes = (await fetch_riot_data(url=RUNES_URL, app=app))

    return {
        'version': latest_version,
        'champions': champions,
        'spells': spells,
        'ITEMS_URL': ITEMS_URL,
        'runes': runes
    }

async def fetch_riot_data(url: str, app: FastAPI):

    async def retry_after_sleep():
        await asyncio.sleep(10)
        return await fetch_riot_data(url, app)
    
    async with app.session.get(url) as response:
        codes = {
            200: lambda: response.json(),
            400: None,
            404: None,
            420: retry_after_sleep
        }

        action = codes.get(response.status, lambda: response.raise_for_status())
        return await action()
    

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
        'ACCOUNT_V1_riotid':f"https://{regional_choice}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/",
        'ACCOUNT_V1_puuid':f"https://{regional_choice}.api.riotgames.com/riot/account/v1/accounts/by-puuid/",
        'MATCH_V5':f"https://{regional_choice}.api.riotgames.com/lol/match/v5/matches/",
        'SUMMONER_V4':f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/",
        'CHAMPIONS_URL':f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json",
        'SPELLS_URL':f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/summoner.json",
        'ITEMS_URL':f"http://ddragon.leagueoflegends.com/cdn/{version}/img/item/",
        'VERSION_API':"https://ddragon.leagueoflegends.com/api/versions.json",
        'LEAGUE_V4':f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/"
    }

    # selected_url = next(value for key, value in urls.items() if riot_api in key)
    selected_url = urls.get(riot_api)

    if selected_url:
        return selected_url
    else:
        raise Exception(f"Unknown Riot API {riot_api}")


async def validate_players(players, region, app):

    ACCOUNT_V1 = await get_url(riot_api="ACCOUNT_V1_riotid", region=region)

    async def validate_puuid(player):

        name, tag = player.strip().split('#')
        data = await fetch_riot_data(url=f'{ACCOUNT_V1}{name}/{tag}?api_key={RIOT_TOKEN}', app=app)

        validated_player = Player(
            name=name,
            tag=tag,
            region=region,
            puuid=data['puuid'] if data else None
        )
        return validated_player

    tasks = [validate_puuid(player) for _, player in players.items()]
    results = await asyncio.gather(*tasks)

    return results


async def fetch_account_summoner(player, region, app):

    async def process_accounts(player):
        data = (await fetch_riot_data(url=f"{await get_url(riot_api="SUMMONER_V4", region=region)}{player.puuid}?api_key={RIOT_TOKEN}", app=app))
        player.summoner = data

    async def process_rank(player):
        data = (await fetch_riot_data(url=f"{await get_url(riot_api="LEAGUE_V4", region=region)}{player.summoner['id']}?api_key={RIOT_TOKEN}", app=app))
        player.league = data
    
    await run_sequence(
        process_accounts(player),
        process_rank(player)
    )


async def get_matches(player, app):
    MATCH_V5 = await get_url(riot_api="MATCH_V5", region=player.region)
    player.matches = (await fetch_riot_data(url=f'{MATCH_V5}by-puuid/{player.puuid}/ids?start=0&count=100&api_key={RIOT_TOKEN}', app=app))


async def fetch_match_data(match_id, region, app):
    url = await get_url(riot_api="MATCH_V5", region=region)
    match_data = await fetch_riot_data(url=f'{url}{match_id}?api_key={RIOT_TOKEN}', app=app)
    return match_data


async def fetch_all_matches(match_list, region, app):
    return_value = []

    async def fetch_and_process(match):
        data = await fetch_match_data(match, region, app)
        return_value.append(data)

    tasks = [fetch_and_process(match) for match in match_list]
    results = await asyncio.gather(*tasks)

    return return_value


async def match_dict(id, data, players):
    
    ret_dict = {}

    # Player 1
    ret_dict['puuid_p1'] = players[0].puuid
    ret_dict['summ_name_p1'] = players[0].name
    ret_dict['tag_line_p1'] = players[0].tag
    ret_dict['idx_p1'] = data['metadata']['participants'].index(players[0].puuid)
    ret_dict['stats_p1'] = data['info']['participants'][ret_dict['idx_p1']]
    ret_dict['level_p1'] = ret_dict['stats_p1']['champLevel']
    ret_dict['champion_id_p1'] = ret_dict['stats_p1']['championId']
    ret_dict['champion_name_p1'] = ret_dict['stats_p1']['championName']
    ret_dict['lane_position_p1'] = ret_dict['stats_p1']['lane']
    ret_dict['items_p1'] = ['{}'.format(ret_dict['stats_p1']["item{}".format(i)]) for i in range(7)]
    ret_dict['team_id_p1'] = ret_dict['stats_p1']['teamId']
    ret_dict['win_lose_p1'] = ret_dict['stats_p1']['win']
    ret_dict['kills_p1'] = ret_dict['stats_p1']['kills']
    ret_dict['deaths_p1'] = ret_dict['stats_p1']['deaths']
    ret_dict['assists_p1'] = ret_dict['stats_p1']['assists']
    ret_dict['kda_p1'] = f"{round(((ret_dict['kills_p1'] + ret_dict['assists_p1'])/max(ret_dict['deaths_p1'], 1)), 2):.2f}"
    ret_dict['spell_1_p1'] = ret_dict['stats_p1']['summoner1Id']
    ret_dict['spell_2_p1'] = ret_dict['stats_p1']['summoner2Id']
    ret_dict['rune_1_p1'] = ret_dict['stats_p1']['perks']['styles'][0]['selections'][0]['perk']
    ret_dict['rune_2_p1'] = ret_dict['stats_p1']['perks']['styles'][1]['selections'][0]['perk']

    # Player 2
    ret_dict['puuid_p2'] = players[1].puuid
    ret_dict['summ_name_p2'] = players[1].name
    ret_dict['tag_line_p2'] = players[1].tag
    ret_dict['idx_p2'] = data['metadata']['participants'].index(players[1].puuid)
    ret_dict['stats_p2'] = data['info']['participants'][ret_dict['idx_p2']]
    ret_dict['level_p2'] = ret_dict['stats_p2']['champLevel']
    ret_dict['champion_id_p2'] = ret_dict['stats_p2']['championId']
    ret_dict['champion_name_p2'] = ret_dict['stats_p2']['championName']
    ret_dict['lane_position_p2'] = ret_dict['stats_p2']['lane']
    ret_dict['items_p2'] = ['{}'.format(ret_dict['stats_p2']["item{}".format(i)]) for i in range(7)]
    ret_dict['team_id_p2'] = ret_dict['stats_p2']['teamId']
    ret_dict['win_lose_p2'] = ret_dict['stats_p2']['win']
    ret_dict['kills_p2'] = ret_dict['stats_p2']['kills']
    ret_dict['deaths_p2'] = ret_dict['stats_p2']['deaths']
    ret_dict['assists_p2'] = ret_dict['stats_p2']['assists']
    ret_dict['kda_p2'] = f"{round(((ret_dict['kills_p2'] + ret_dict['assists_p2'])/max(ret_dict['deaths_p2'], 1)), 2):.2f}"
    ret_dict['spell_1_p2'] = ret_dict['stats_p2']['summoner1Id']
    ret_dict['spell_2_p2'] = ret_dict['stats_p2']['summoner2Id']
    ret_dict['rune_1_p2'] = ret_dict['stats_p2']['perks']['styles'][0]['selections'][0]['perk']
    ret_dict['rune_2_p2'] = ret_dict['stats_p2']['perks']['styles'][1]['selections'][0]['perk']

    # Match
    ret_dict['match_id'] = id
    ret_dict['region'] = players[0].region
    ret_dict['same_team'] = True if ret_dict['win_lose_p1'] == ret_dict['win_lose_p2'] else False
    ret_dict['creation'] = datetime.fromtimestamp(data['info']['gameCreation']/1000).strftime("%Y-%m-%d %H:%M")
    ret_dict['creation_time_ago'] = await time_ago(data['info']['gameCreation'])
    ret_dict['duration'] = f"{data['info']['gameDuration']//60}:{data['info']['gameDuration']%60:02}" # use zfill to fill with 0
    ret_dict['game_mode'] = data['info']['gameMode']
    return ret_dict



async def get_image_path(match=None, RIOT_DATA=None):

    async def get_data_id(data_type, data_id):
        data = next((d for d in RIOT_DATA[data_type].values() if d['key'] == str(data_id)), None)
        return data if data else None

    async def get_image_list(item_numbers):
        async def get_image_path_item(key_number):
            return f"{RIOT_DATA['ITEMS_URL']}{key_number}.png"

        return [await get_image_path_item(item_number) for item_number in item_numbers if item_number != str(0)]

    async def get_image_url(data, url_prefix):
        return f"{url_prefix}{data['id']}.png" if data else None
    
    async def find_icon_by_id(key):
        for style in RIOT_DATA['runes']:
            for slot in style["slots"]:
                for rune in slot["runes"]:
                    if rune["id"] == key:
                        return rune["icon"]

        # If target rune ID not found: 
        return None

    champ_p1_data = await get_data_id('champions', match['champion_id_p1'])
    champ_p2_data = await get_data_id('champions', match['champion_id_p2'])
    spell_1_p1_data = await get_data_id('spells', match['spell_1_p1'])
    spell_2_p1_data = await get_data_id('spells', match['spell_2_p1'])
    spell_1_p2_data = await get_data_id('spells', match['spell_1_p2'])
    spell_2_p2_data = await get_data_id('spells', match['spell_2_p2'])
    image_list_p1 = await get_image_list(match['items_p1'])
    image_list_p2 = await get_image_list(match['items_p2'])
    rune_1_p1 = await find_icon_by_id(match['rune_1_p1'])
    rune_2_p1 = await find_icon_by_id(match['rune_2_p1'])
    rune_1_p2 = await find_icon_by_id(match['rune_1_p2'])
    rune_2_p2 = await find_icon_by_id(match['rune_2_p2'])

    champion_url = f"https://ddragon.leagueoflegends.com/cdn/{RIOT_DATA['version']}/img/champion/"
    spell_url = f"http://ddragon.leagueoflegends.com/cdn/{RIOT_DATA['version']}/img/spell/"
    runes_url = f"https://ddragon.leagueoflegends.com/cdn/img/"

    match['champ_p1_data'] = champ_p1_data
    match['champ_p2_data'] = champ_p2_data
    match['champ_p1_img'] = await get_image_url(champ_p1_data, champion_url)
    match['champ_p2_img'] = await get_image_url(champ_p2_data, champion_url)
    match['spell_1_p1_img'] = await get_image_url(spell_1_p1_data, spell_url)
    match['spell_2_p1_img'] = await get_image_url(spell_2_p1_data, spell_url)
    match['spell_1_p2_img'] = await get_image_url(spell_1_p2_data, spell_url)
    match['spell_2_p2_img'] = await get_image_url(spell_2_p2_data, spell_url)
    match['items_p1_img'] = image_list_p1 if image_list_p1 else None
    match['items_p2_img'] = image_list_p2 if image_list_p2 else None
    match['rune_1_p1_img'] = f"{runes_url}{rune_1_p1}"
    match['rune_2_p1_img'] = f"{runes_url}{rune_2_p1}"
    match['rune_1_p2_img'] = f"{runes_url}{rune_1_p2}"
    match['rune_2_p2_img'] = f"{runes_url}{rune_2_p2}"

async def time_ago(match_time):
    """Calculates the time difference from the match event time in Unix time.
    
    Args:
        match_time = The Unix time for specific match.
    
    Returns:
        A string representing the time difference in the format of "x days ago", "x hours ago", or "x minutes ago".
    """

    match_time = match_time / 1000
    now = time.time()
    difference = now - match_time

    days = difference // (24 * 3600)
    difference %= (24 * 3600)
    hours = difference // 3600
    difference %= 3600
    minutes = difference // 60

    if days > 0:
        return f"{int(days)} days ago"
    elif hours > 0:
        return f"{int(hours)} hours ago"
    elif minutes > 0:
        return f"{int(minutes)} minutes ago"
    else:
        return "Just Now"