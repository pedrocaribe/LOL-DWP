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

RIOT_DATA = RiotData()

"""Documentation consulted

- Difference between HTTPX, requests and AIOHTTP
https://oxylabs.io/blog/httpx-vs-requests-vs-aiohttp
- AIOHTTP Documentation
https://docs.aiohttp.org/en/stable/


"""

@app.route('/')
async def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
async def search():
    data = request.form.to_dict()
    return render_template('search.html', form_data=data)

@app.route('/fetch-data', methods=['GET', 'POST'])
async def fetch_data():
    form_data = request.get_json()
    region = form_data['selected-region']

    ACCOUNT_V1 = await get_url(riot_api="ACCOUNT_V1", region=region)

    players = {}

    for i in range(1,3):
        player = await create_player()

        player["name"], player["tag"] = form_data[f'game_name_{i}'].strip().split('#')
        player["region"] = region

        processed_data = await fetch_riot_data(f'{ACCOUNT_V1}{player["name"]}/{player["tag"]}?api_key={RIOT_TOKEN}')

        if processed_data:
            player["puuid"] = processed_data['puuid']
        else:
            player = None
        
        players[f'player{i}'] = player

    if players['player1'] and players['player2']:
        current_version = (await fetch_riot_data(await get_url(riot_api="VERSION_API")))[0]

        if current_version != RIOT_DATA.latest_version:
            RIOT_DATA.fetch_latest_data()
        
        for id_key, player in players.items():
            await get_matches(player)

        matches_container = list((set(players['player1']["matches"]).intersection(players['player2']["matches"])))
        
        if matches_container:
            start = time.time()
            match_data = await fetch_all_matches(matches_container, region=region)
            end = time.time()
            matches_count = len(match_data)

            print(f'{fy + bg + sb}Processed {matches_count} matches in {round(end-start, 4)} seconds{sres}')

            matches = []
            for match_id, data in match_data.items():
                match = Match(match_id, data, players)
                await match.process_match_data()

                matches.append(match)

            def date_sort(e):
                return e.creation

            matches.sort(reverse=True, key=date_sort)
            
            matches_data = [{key: value for key, value in match.__dict__.items() if key != 'players'} for match in matches]

            print(f'{fy + bg + sb}Preparing to send data to Website{sres}')
            return jsonify(matches=matches_data)
                
    else:
        failed_player1 = True if not players['player1'] else False
        print(failed_player1)
        failed_player2 = True if not players['player2'] else False
        print(failed_player2)
    















if __name__ == "__main__":
    app.run(port=8080)
