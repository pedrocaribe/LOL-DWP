import aiohttp, asyncio, time, datetime, requests, concurrent.futures, functools

from settings import *

from contextlib import contextmanager
from datetime import datetime
from typing import Awaitable, Any

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


"""Usage:

Run function_1 and function_2 in parallel through threading:

await run_parallel(
    function_1(args),
    function_2(args)
)

Run function_3 and function_4 in sequence, one after the other:

await run_sequence(
    function_3(args),
    function_4(args)
)

Nested:
Run function_1, function_2 and run_sequence in parallel, 
inside run_sequence run function_3 and function_4 in sequence.

await run_parallel(
    function_1(args),
    function_2(args),
    run_sequence(
        function_3,
        function_4
    )
)
"""

# Asyncio function to run functions in parallel thread
@duration
async def run_parallel(*functions: Awaitable[Any]) -> None:
    await asyncio.gather(*functions)

# Function to run functions in sequence
@duration
async def run_sequence(*functions: Awaitable[Any]) -> None:
    for function in functions:
        await function


@duration
def ddragon_data():

    VERSION_API = "https://ddragon.leagueoflegends.com/api/versions.json"
    latest_version = requests.get(VERSION_API).json()[0]

    CHAMPIONS_URL = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion.json"
    SPELLS_URL = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/summoner.json"
    ITEMS_URL = f"http://ddragon.leagueoflegends.com/cdn/{latest_version}/img/item/"
    RUNES_URL = f"http://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/runesReforged.json"
    
    
    champions = requests.get(CHAMPIONS_URL).json()["data"]
    spells = requests.get(SPELLS_URL).json()["data"]
    runes = requests.get(RUNES_URL).json()

    return {
        'version': latest_version,
        'champions': champions,
        'spells': spells,
        'ITEMS_URL': ITEMS_URL,
        'runes': runes
    }


async def get_matches(player):
    MATCH_V5 = await get_url(riot_api="MATCH_V5", region=player["region"])
    player["matches"] = (await fetch_riot_data(f'{MATCH_V5}by-puuid/{player["puuid"]}/ids?start=0&count=100&api_key={RIOT_TOKEN}'))


async def match_dict(id, data, players):
    ret_dict = {}

    # Player 1
    ret_dict['puuid_p1'] = players[0]['puuid']
    ret_dict['summ_name_p1'] = players[0]['name']
    ret_dict['tag_line_p1'] = players[0]['tag']
    ret_dict['idx_p1'] = data['metadata']['participants'].index(players[0]['puuid'])
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
    ret_dict['puuid_p2'] = players[1]['puuid']
    ret_dict['summ_name_p2'] = players[1]['name']
    ret_dict['tag_line_p2'] = players[1]['tag']
    ret_dict['idx_p2'] = data['metadata']['participants'].index(players[1]['puuid'])
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
    ret_dict['region'] = players[0]['region']
    ret_dict['same_team'] = True if ret_dict['win_lose_p1'] == ret_dict['win_lose_p2'] else False
    ret_dict['creation'] = datetime.fromtimestamp(data['info']['gameCreation']/1000).strftime("%Y-%m-%d %H:%M")
    ret_dict['creation_time_ago'] = await time_ago(data['info']['gameCreation'])
    ret_dict['duration'] = f"{data['info']['gameDuration']//60}:{data['info']['gameDuration']%60:02}" # use zfill to fill with 0
    ret_dict['game_mode'] = data['info']['gameMode']
    return ret_dict




async def fetch_match_data(match_id, region):
    url = await get_url(riot_api="MATCH_V5", region=region)
    match_data = await fetch_riot_data(f'{url}{match_id}?api_key={RIOT_TOKEN}')
    return match_data


@duration
async def fetch_all_matches(match_list, region):
    return_value = {}

    # Processing time 1.25 sec
    async def fetch_and_process(match):
        data = await fetch_match_data(match, region)
        return_value[match] = data

    tasks = [fetch_and_process(match) for match in match_list]
    results = await asyncio.gather(*tasks)

    return return_value

@duration
async def validate_all_players(players, region):

    ACCOUNT_V1 = await get_url(riot_api="ACCOUNT_V1", region=region)

    async def validate_puuid(player):

        name, tag = player.strip().split('#')
        data = await fetch_riot_data(f'{ACCOUNT_V1}{name}/{tag}?api_key={RIOT_TOKEN}')
        print(data)
        ret = {
            'name':name,
            'tag':tag,
            'region':region,
            'puuid':data['puuid'] if data else None
        }
        return ret

    tasks = [validate_puuid(player) for _, player in players.items()]
    results = await asyncio.gather(*tasks)

    return results


@duration
async def fetch_account_summoner(player, region):

    async def process_accounts(player):
        data = (await fetch_riot_data(f"{await get_url(riot_api="SUMMONER_V4", region=region)}{player['puuid']}?api_key={RIOT_TOKEN}"))
        player['summoner'] = data

    async def process_rank(player):
        data = (await fetch_riot_data(f"{await get_url(riot_api="LEAGUE_V4", region=region)}{player['summoner']['id']}?api_key={RIOT_TOKEN}"))
        player['league'] = data

    
    await run_sequence(
        process_accounts(player),
        process_rank(player)
    )


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
        'VERSION_API':"https://ddragon.leagueoflegends.com/api/versions.json",
        'LEAGUE_V4':f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/"
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