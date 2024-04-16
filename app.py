from flask import Flask, request, jsonify, render_template

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
    print(data)
    return render_template('search.html', form_data=data)


@app.route('/fetch-data', methods=['GET', 'POST'])
async def fetch_data():
    form_data = request.get_json()
    region = form_data['selected-region']

    ACCOUNT_V1 = await get_url(riot_api="ACCOUNT_V1", region=region)

    players = {}

    for i in range(1,3):
        player = Player()

        player.name, player.tag = form_data[f'game_name_{i}'].strip().split('#')
        player.region = region

        processed_data = await fetch_riot_data(f'{ACCOUNT_V1}{player.name}/{player.tag}?api_key={RIOT_TOKEN}')

        if processed_data:
            player.puuid = processed_data['puuid']
        else:
            player = None
        
        players[f'player{i}'] = player

    if players['player1'] and players['player2']:
        current_version = (await fetch_riot_data(await get_url(riot_api="VERSION_API")))[0]

        if current_version != RIOT_DATA.latest_version:
            RIOT_DATA.fetch_latest_data()
        
        for puuid, player in players.items():
            await player.get_matches()

        matches_container = list((set(players['player1'].matches).intersection(players['player2'].matches)))
        
        if matches_container:

            start = time.time()
            print(start)
            match_data = await fetch_all_matches(matches_container, region=region)
            end = time.time()
            print(end)
            timeee = round(end-start, 4)
            print("Time to process all matches", timeee)

            print(match_data)


        
    else:
        failed_player1 = True if not players['player1'] else False
        print(failed_player1)
        failed_player2 = True if not players['player2'] else False
        print(failed_player2)
    return processed_data















if __name__ == "__main__":
    app.run(port=8080)
