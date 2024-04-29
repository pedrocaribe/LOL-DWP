from flask import Flask, request, jsonify, render_template
import logging

import smtplib, ssl
from email.message import EmailMessage

from settings import *
from utils import *

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)-8s] %(name)-2s:%(module)-1s : %(message)s", style="%",
    datefmt='%m/%d/%Y %I:%M:%S %p'
    )
logger = logging.getLogger(__name__)

logger.info(RIOT_TOKEN)
app = Flask(__name__, static_folder='static', template_folder='Templates')

RIOT_DATA = ddragon_data()

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

    if players[0]['puuid'] and players[1]['puuid']:

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

            logger.info(f'Processed {matches_count} matches') # Logging

            matches = []
            for match_id, data in match_data.items():
                match = await match_dict(match_id, data, players)
                await get_image_path(match=match, RIOT_DATA=RIOT_DATA)


                matches.append(match)

            def date_sort(e):
                return e['creation']

            matches.sort(reverse=True, key=date_sort)

            logger.info(f'{fy + bg + sb}Preparing to send data to Website{sres}') # Logging
            
            end = time.time()
            logger.info(f"{fw + bb + sb}Execution of backend took {round((end-start), 2)} seconds{sres}") # Logging

            return jsonify({'matches':matches, 'players':players})
        else:
            return players
        
    else:
        logger.error(f'{fr + bw}DID NOT FIND PLAYER{sres}') # Logging
        return players


@app.route('/send-email', methods=['POST'])
async def send_email():
    
    sender, recv = "dev.pcaribe@gmail.com"
    passwd = MAIL_PASSWD
    subj = "Contact From DWP"

    data = request.get_json()
    name = data['name']
    email = data['email']
    message = data['message']

    em = EmailMessage()
    em['From'] = sender
    em['to'] = recv
    em['Subject'] = subj
    em.set_content(f"Name: {name}\nEmail: {email}\nMessage: {message}")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        try:
            smtp.login(sender, passwd)
            smtp.sendmail(sender, recv, em.as_string())
            return jsonify({"message":"E-mail sent successfully"}), 200
        
        except Exception as e:
            return jsonify({"message":"E-mail failed to send", "error":str(e)}), 500
    
if __name__ == "__main__":
    app.run(port=8080)
