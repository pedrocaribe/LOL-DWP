
import requests
import time
from datetime import datetime

from flask_session import Session
from flask import Flask, flash, redirect, render_template, session, request
from settings import *
import flask
from bs4 import BeautifulSoup

# Configure application
app = flask.Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/", methods=['GET', 'POST'])
async def index():
    """Show index page"""
    return render_template("index.html", failed_game_name_1=False, failed_game_name_2=False)


@app.route("/search", methods=['GET','POST'])
async def search():
    """Perform Search within RIOT API"""

    gn1 = request.form["game_name_1"]
    gn2 = request.form["game_name_2"]
    game_name_1, tag_line_1 = gn1.split("#")
    game_name_2, tag_line_2 = gn2.split("#")
    region = request.form["selected-region"]

    """https://leagueoflegends.fandom.com/wiki/Servers"""
    
    regional = {
    "AMERICAS":['BR1','LA1','LA2','NA1',],
    "ASIA":['JP1','KR','PH2','SG2','TW2','TH2','VN2','PH1','SG1','TW1','VN1','TH1'],
    "EUROPE":['EUN1','EUW1','RU1','TR1'],
    "SEA":['OC1']
    }

    regional_choice = next(key for key, regions in regional.items())

    ACCOUNT_V1 = f"https://{regional_choice}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"
    MATCH_V5 = f"https://{regional_choice}.api.riotgames.com/lol/match/v5/matches/"
    SUMMONER_V4 = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/"

    start1 = time.time()
    req1 = requests.get(f'{ACCOUNT_V1}{game_name_1}/{tag_line_1}?api_key={RIOT_TOKEN}')
    
    puuid_1 = req1.json()['puuid'] if req1 else False

    end1 = time.time()
    time_process_player_info_1 = round(end1 - start1, 2)
    print("Time spent to get game name and tag line player 1:", time_process_player_info_1)

    start2 = time.time()
    req2 = requests.get(f'{ACCOUNT_V1}{game_name_2}/{tag_line_2}?api_key={RIOT_TOKEN}')
    puuid_2 = req2.json()['puuid'] if req2 else False

    end2 = time.time()
    time_process_player_info_2 = round(end2 - start2, 2)
    print("Time spent to get game name and tag line player 2:", time_process_player_info_2)

    if puuid_1 and puuid_2:


        # Retrieve current version of LOL
        VERSION_API = "https://ddragon.leagueoflegends.com/api/versions.json"
        latest_version = requests.get(VERSION_API).json()[0]


        # Retrieve champions from Riot API
        CHAMPIONS_URL = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion.json"
        champions = requests.get(CHAMPIONS_URL).json()["data"]


        # Retrieve spells from Riot API
        SPELLS_URL = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/summoner.json"
        spells = requests.get(SPELLS_URL).json()["data"]

        # Generic Items URL for icon images
        ITEMS_URL = f"http://ddragon.leagueoflegends.com/cdn/{latest_version}/img/item/"


        # Retrieve list of past 100 games for Player 1
        start3 = time.time()
        matches_player_1 = requests.get(f'{MATCH_V5}by-puuid/{puuid_1}/ids?start=0&count=100&api_key={RIOT_TOKEN}').json()
        end3 = time.time()
        time_process_player_1_matches = round(end3 - start3, 2)
        print("Time spent to get matches player 1:", time_process_player_1_matches)

        # Retrieve list of past 100 games for Player 2
        start4 = time.time()
        matches_player_2 = requests.get(f'{MATCH_V5}by-puuid/{puuid_2}/ids?start=0&count=100&api_key={RIOT_TOKEN}').json()
        end4 = time.time()
        time_process_player_2_matches = round(end4 - start4, 2)
        print("Time spent to get matches player 2:", time_process_player_2_matches)

        # Join both lists of matches and check if interesects
        played_with = list((set(matches_player_1).intersection(matches_player_2)))

        if played_with:

            match_stats = list()

            # Retrieve game information for each match intersected
            start5 = time.time()
            for each in played_with:
                req = requests.get(f'{MATCH_V5}{each}?api_key={RIOT_TOKEN}').json()

                p1 = req['metadata']['participants'].index(puuid_1)
                p2 = req['metadata']['participants'].index(puuid_2)
                p1_stats_per_match = req['info']['participants'][p1]
                p2_stats_per_match = req['info']['participants'][p2]

                match_stats.append({
                    "data":req,
                    "p1":p1_stats_per_match,
                    "p2":p2_stats_per_match
                })
            end5 = time.time()
            time_process_matches_info = round(end5 - start5, 2)
            print("Time spent to matches info:", time_process_matches_info)

            def date_sort(e):
                return e['data']['info']['gameCreation']

            match_stats.sort(reverse=True, key=date_sort)
            
            match_info = list()

            for each in match_stats:

                item_numbers_p1 = [each['p1'][f'item{i}'] for i in range(6)]
                item_numbers_p2 = [each['p2'][f'item{i}'] for i in range(6)]


                async def get_champions_by_key(key):
                    
                    for champion in champions:
                        if champions[champion]["key"] == str(key):
                            return champions[champion]
                
                async def get_spell_by_key(key):
                    
                    for spell in spells:
                        if spells[spell]["key"] == str(key):
                            return spells[spell]
                        


                async def get_image_path(key_number, package=None):
                    
                    if package == "champion":
 
                        champion = await get_champions_by_key(key_number)
 
                        champion_name = champion["id"]

                        base_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/img/champion/"

                        return f"{base_url}{champion_name}.png"
                    
                    if package == "spell":
                        
                        spell = await get_spell_by_key(key_number)

                        spell_name = spell["id"]

                        base_url = f"http://ddragon.leagueoflegends.com/cdn/{latest_version}/img/spell/"

                        return f"{base_url}{spell_name}.png"
                    
                    if package == "item":
                        return f"{ITEMS_URL}{key_number}.png"
                        
                    return None
                

                async def get_image_list(item_numbers):
                    image_paths = []
                    for item_number in item_numbers:
                        if item_number != 0:
                            image_path = await get_image_path(item_number, "item")
                            if image_path:
                                image_paths.append(image_path)
                    
                    return image_paths
                
                image_list_p1 = await get_image_list(item_numbers_p1)
                image_list_p2 = await get_image_list(item_numbers_p2)


                champion_image_p1 = await get_image_path(each['p1']['championId'], "champion")
                champion_image_p2 = await get_image_path(each['p2']['championId'], "champion")
                s1_summ1_img = await get_image_path(each['p1']['summoner1Id'], "spell")
                s1_summ2_img = await get_image_path(each['p1']['summoner2Id'], "spell")
                s2_summ1_img = await get_image_path(each['p2']['summoner1Id'], "spell")
                s2_summ2_img = await get_image_path(each['p2']['summoner2Id'], "spell")

                match_info.append({
                    "match_id":each['data']['metadata']['matchId'],
                    'match_date':datetime.fromtimestamp(each['data']['info']['gameCreation']/1000).strftime("%Y-%m-%d %H:%M"), 
                    "match_duration":f"{each['data']['info']['gameDuration']//60}:{each['data']['info']['gameDuration']%60}",
                    "match_type":each['data']['info']['gameMode'],



                    # P1
                    "p1_win_lose":"Win" if each['p1']['win'] else "Lose",
                    "s1_champion_name":each['p1']['championName'],
                    "s1_champion_img":champion_image_p1,
                    "s1_player_name":each['p1']['riotIdGameName'],
                    "s1_player_tag":each['p1']['riotIdTagline'],
                    "s1_kills":each['p1']['kills'],
                    "s1_deaths":each['p1']['deaths'],
                    "s1_assists":each['p1']['assists'],
                    "s1_kda":each['p1']['challenges']['kda'],
                    "s1_item0":each['p1']['item0'],
                    "s1_item1":each['p1']['item1'],
                    "s1_item2":each['p1']['item2'],
                    "s1_item3":each['p1']['item3'],
                    "s1_item4":each['p1']['item4'],
                    "s1_item5":each['p1']['item5'],
                    "s1_item6":each['p1']['item6'],
                    "s1_lane":each['p1']['lane'],
                    "s1_items":image_list_p1,
                    "s1_summ1_img":s1_summ1_img,
                    "s1_summ2_img":s1_summ2_img,





                    # MUDAR TUDO PRA BAIXO PRA INCLUIR DADOS DO P2

                    "p2_win_lose":"Win" if each['p2']['win'] else "Lose",
                    "s2_champion_name":each['p2']['championName'],
                    "s2_champion_img":champion_image_p2,
                    "s2_player_name":each['p2']['riotIdGameName'],
                    "s2_player_tag":each['p2']['riotIdTagline'],
                    "s2_player_name":each['p2']['summonerName'],
                    "s2_kills":each['p2']['kills'],
                    "s2_deaths":each['p2']['deaths'],
                    "s2_assists":each['p2']['assists'],
                    "s2_kda":each['p2']['challenges']['kda'],
                    "s2_item0":each['p2']['item0'],
                    "s2_item1":each['p2']['item1'],
                    "s2_item2":each['p2']['item2'],
                    "s2_item3":each['p2']['item3'],
                    "s2_item4":each['p2']['item4'],
                    "s2_item5":each['p2']['item5'],
                    "s2_item6":each['p2']['item6'],
                    "s2_lane":each['p2']['lane'],
                    "s2_items":image_list_p2,
                    "s2_summ1_img":s2_summ1_img,
                    "s2_summ2_img":s2_summ2_img
                    
                    })

            return render_template("result.html", h=f"Yes, both players have played with each other in {len(played_with)} games", matches=match_info)

            start5 = time.time()
            print(played_with[0])
            cached_matches = requests.get(MATCH_V5+played_with[0]+'?api_key='+RIOT_TOKEN).json()['info']['participants']
            end5 = time.time()
            print(end5 - start5)
            if resp == "yes":
                print(cached_matches)
        else:

            return render_template("result.html", h="No, both players have Not played togheter in the last 100 games", loading=False)
    
    else:
        failed_game_name_1 = True if not req1 else False
        failed_game_name_2 = True if not req2 else False

        # return render_template("index.html", gn1=game_name_1, gn2=game_name_2, tg1=tag_line_1, tg2=tag_line_2, failed_game_name_1=failed_game_name_1, failed_game_name_2=failed_game_name_2, loading=False)
        return render_template("index.html", failed_game_name_1=failed_game_name_1, failed_game_name_2=failed_game_name_2, loading=False)
