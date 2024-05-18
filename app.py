import requests

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
from contextlib import asynccontextmanager
from aiohttp import ClientSession
import asyncio

from utils import *

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.session = ClientSession()
    app.state.RIOT_DATA = await ddragon_data(app=app)
    yield
    await app.session.close()

app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates/")
app.mount('/static', StaticFiles(directory='static'), name="static")

@app.get("/")
async def index(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("index.html", context=context)

@app.post("/search")
async def search(request: Request):
    data = dict(await request.form())
    return templates.TemplateResponse("search.html", {'request':request, 'form_data':data})

@app.api_route('/fetch-data', methods=['GET', 'POST'])
async def fetch_data(request: Request):
    form_data = await request.json()
    region = form_data.pop("selected-region")

    main_players = await validate_players(form_data, region, app)

    if main_players[0].puuid and main_players[1].puuid:
        current_version = (await fetch_riot_data(url=await get_url(riot_api="VERSION_API"), app=app))[0]

        if current_version != app.state.RIOT_DATA["version"]:
            app.state.RIOT_DATA = await ddragon_data(app=app)

        await run_parallel(
            get_matches(main_players[0], app),
            get_matches(main_players[1], app)
        )

        played_with = list((set(main_players[0].matches).intersection(main_players[1].matches)))

        if played_with:
            
            
            match_data = await fetch_all_matches(match_list=played_with, region=region, app=app)
            matches_count = len(match_data)

            # logger.info(f'Processed {matches_count} matches') # Logging

            matches = []
            for match in match_data:
                # return print(match_id)
                match = await match_dict(match['metadata']['matchId'], match, main_players)
                await get_image_path(match=match, RIOT_DATA=app.state.RIOT_DATA)


                matches.append(match)

            def date_sort(e):
                return e['creation']

            matches.sort(reverse=True, key=date_sort)

            return JSONResponse(content={'matches':matches, 'players':[(player.model_dump()).pop('matches') for player in main_players]}) #issue to pass main_players
        else:
            return JSONResponse(content=[player.model_dump() for player in main_players]) #issue to pass main_players


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)