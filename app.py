
import requests
import time
from datetime import datetime

from flask_session import Session
from flask import Flask, flash, redirect, render_template, session, request
from settings import *
import flask

# Configure application
app = flask.Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/", methods=['GET', 'POST'])
def index():
    """Show index page"""
    return render_template("index.html", gn1="Summoner 1 Game Name", gn2="Summoner 2 Game Name", tg1="Tag", tg2="Tag", failed_game_name_1=False, failed_game_name_2=False)


@app.route("/search", methods=['GET','POST'])
def search():
    """Perform Search within RIOT API"""

    game_name_1 = request.form.get("game_name_1")
    tag_line_1 = request.form.get("tag_line_1")
    game_name_2 = request.form.get("game_name_2")
    tag_line_2 = request.form.get("tag_line_2")

    start1 = time.time()
    req1 = requests.get(ACCOUNT_V1+game_name_1+'/'+tag_line_1+'?api_key='+RIOT_TOKEN)
    
    puuid_1 = req1.json()['puuid'] if req1 else False

    end1 = time.time()
    time_process_player__info_1 = round(end1 - start1, 2)

    start2 = time.time()
    req2 = requests.get(ACCOUNT_V1+game_name_2+'/'+tag_line_2+'?api_key='+RIOT_TOKEN)
    puuid_2 = req2.json()['puuid'] if req2 else False

    end2 = time.time()
    time_process_player__info_2 = round(end2 - start2, 2)

    #account_id = requests.get(SUMMONER_V4+puuid+'?api_key='+RIOT_TOKEN).json()['accountId']

    if puuid_1 and puuid_2:

        start3 = time.time()
        matches_player_1 = requests.get(MATCH_V5+'by-puuid/'+puuid_1+'/ids?start=0&count=100&api_key='+RIOT_TOKEN).json()
        end3 = time.time()
        time_process_player_1_matches = round(end3 - start3, 2)

        start4 = time.time()
        matches_player_2 = requests.get(MATCH_V5+'by-puuid/'+puuid_2+'/ids?start=0&count=100&api_key='+RIOT_TOKEN).json()
        end4 = time.time()
        time_process_player_2_matches = round(end4 - start4, 2)

        played_with = list((set(matches_player_1).intersection(matches_player_2)))

        if played_with:

            match_stats = list()

            for each in played_with:
                req = requests.get(MATCH_V5+each+'?api_key='+RIOT_TOKEN).json()
                p1 = req['metadata']['participants'].index(puuid_1)
                p2 = req['metadata']['participants'].index(puuid_2)
                p1_stats_per_match = req['info']['participants'][p1]
                p2_stats_per_match = req['info']['participants'][p2]

                match_stats.append({
                    "data":req,
                    "p1":p1_stats_per_match,
                    "p2":p2_stats_per_match
                })

            
            match_info = list()

            for each in match_stats:

                match_info.append({
                    "match_id":each['data']['metadata']['matchId'],
                    'match_date':datetime.fromtimestamp(each['data']['info']['gameCreation']/1000).strftime("%Y-%m-%d %H:%M:%S"), 
                    "match_duration":f"{each['data']['info']['gameDuration']//60}:{each['data']['info']['gameDuration']%60} min",
                    "match_type":each['data']['info']['gameMode'],
                    "s1_champion_name":each['p1']['championName'],
                    "s1_player_name":each['p1']['summonerName'],
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

                    
                    "s2_champion_name":each['p2']['championName'],
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

            return render_template("result.html", h="No, both players have Not played togheter in the last 100 games")
    
    else:
        failed_game_name_1 = True if not req1 else False
        failed_game_name_2 = True if not req2 else False

        return render_template("index.html", gn1=game_name_1, gn2=game_name_2, tg1=tag_line_1, tg2=tag_line_2, failed_game_name_1=failed_game_name_1, failed_game_name_2=failed_game_name_2)
