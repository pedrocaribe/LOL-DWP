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

- Threading / ASYNCIO
https://www.youtube.com/watch?v=2IW-ZEui4h4



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

    start = time.time()

    form_data = request.get_json()
    region = form_data.pop('selected-region')

    players = await validate_all_players(form_data, region)

    if players[0] and players[1]:

        current_version = (await fetch_riot_data(await get_url(riot_api="VERSION_API")))[0]
        
        if current_version != RIOT_DATA["version"]:
            RIOT_DATA = ddragon_data()

        await run_parallel(
            fetch_account_summoner(players[0], region),
            fetch_account_summoner(players[1], region),
            get_matches(players[0]),
            get_matches(players[1])
            )
        
        played_with = list((set(players[0]["matches"]).intersection(players[1]["matches"])))
        
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
            
            end = time.time()
            print(f"{fw + bb + sb}Execution of backend took {round((end-start), 2)} seconds{sres}")
            
            return jsonify({'matches':matches, 'players':players})
                
    else:
        return print("DIDNT FIND PLAYER")

        failed_player1 = True if not players['player1'] else False
        print(failed_player1)
        failed_player2 = True if not players['player2'] else False
        print(failed_player2)
    return None















if __name__ == "__main__":
    app.run(port=8080)
