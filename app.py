from flask import Flask, request, jsonify, render_template
from colorama import Back, Fore,Style

import json

# Styling
fy = Fore.YELLOW
fw = Fore.WHITE
fg = Fore.GREEN
fr = Fore.RED
bg = Back.GREEN
br = Back.RED
bb = Back.BLACK
bres = Back.RESET
sb = Style.BRIGHT
sres = Style.RESET_ALL

from settings import *
from utils import *

app = Flask(__name__, static_folder='static', template_folder='Templates')

app.config["TEMPLATES_AUTO_RELOAD"] = True

RIOT_DATA = ddragon_data()

"""Documentation consulted

- Difference between HTTPX, requests and AIOHTTP
https://oxylabs.io/blog/httpx-vs-requests-vs-aiohttp

- AIOHTTP Documentation
https://docs.aiohttp.org/en/stable/

- Riot Data Dragon Docs
https://developer.riotgames.com/docs/lol#data-dragon

- Riot API Docs
https://developer.riotgames.com/docs/lol


"""

@app.route('/')
async def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
async def search():
    data = request.form.to_dict()
    return render_template('search.html', form_data=data)

@app.route('/fetch-data', methods=['GET', 'POST'])
async def fetch_data(RIOT_DATA=RIOT_DATA):
    form_data = request.get_json()
    region = form_data['selected-region']

    ACCOUNT_V1 = await get_url(riot_api="ACCOUNT_V1", region=region)

    players = {}

    for i in range(1,3):
        player = {}

        player["name"], player["tag"] = form_data[f'game_name_{i}'].strip().split('#')
        player["region"] = region

        player_account = await fetch_riot_data(f'{ACCOUNT_V1}{player["name"]}/{player["tag"]}?api_key={RIOT_TOKEN}')

        if player_account:
            player["puuid"] = player_account['puuid']
        else:
            player = None
        
        players[f'player{i}'] = player

    if players['player1'] and players['player2']:
        current_version = (await fetch_riot_data(await get_url(riot_api="VERSION_API")))[0]

        player_1_summoner = (await fetch_riot_data(f"{await get_url(riot_api="SUMMONER_V4", region=region)}{players['player1']['puuid']}?api_key={RIOT_TOKEN}"))
        player_1_rank = (await fetch_riot_data(f"{await get_url(riot_api="LEAGUE_V4", region=region)}{player_1_summoner['id']}?api_key={RIOT_TOKEN}"))
        player_2_summoner = (await fetch_riot_data(f"{await get_url(riot_api="SUMMONER_V4", region=region)}{players['player2']['puuid']}?api_key={RIOT_TOKEN}"))
        player_2_rank = (await fetch_riot_data(f"{await get_url(riot_api="LEAGUE_V4", region=region)}{player_2_summoner['id']}?api_key={RIOT_TOKEN}"))

        print(player_1_rank, player_2_rank)

        if current_version != RIOT_DATA["version"]:
            RIOT_DATA = ddragon_data()
        
        for id_key, player in players.items():
            await get_matches(player)

        played_with = list((set(players['player1']["matches"]).intersection(players['player2']["matches"])))
        
        if played_with:
            
            match_data = await fetch_all_matches(played_with, region=region)
            
            matches_count = len(match_data)

            print(f'{fy + bg + sb}Processed {matches_count} matches{sres}')

            matches = []
            for match_id, data in match_data.items():
                match = await match_dict(match_id, data, players)
                await get_image_path(match=match, RIOT_DATA=RIOT_DATA)


                matches.append(match)

            def date_sort(e):
                return e['creation']

            matches.sort(reverse=True, key=date_sort)

            print(f'{fy + bg + sb}Preparing to send data to Website{sres}')
            return matches
                
    else:
        failed_player1 = True if not players['player1'] else False
        print(failed_player1)
        failed_player2 = True if not players['player2'] else False
        print(failed_player2)
        print("NOT FOUND ANY MATCHES")
    return None















if __name__ == "__main__":
    app.run(port=8080)
