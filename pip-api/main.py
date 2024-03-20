from vipstream.pip_api_films import FilmAPI
from vipstream.util import mvbasemodel
from vipstream.pip_api_shows import ShowAPI
from fastapi import FastAPI

# pip-api/main.py
# new-pipebomb branch

app = FastAPI(
    title="Pip API",
    description="""
Pip API is a RESTful API designed for films and shows. 🎥
## Films/Shows
You can retrieve film/show data by making API calls to endpoints.
## Users
Users will be able to fetch show and film data, as well as stream sources.
""",
    version="0.0.1",
)

@app.get("/")
async def get_routes():
    return {
        "intro": "Welcome to pip-api. UWU",
        "documentation": "http://pipebomb.bytecats.codes:8000/docs"
    }

@app.get("/films/vip/search", response_model=mvbasemodel.FilmResponse)
async def get_film(q: str):
    return FilmAPI.get_film_data(q)

@app.get("/series/vip/search", response_model=mvbasemodel.ShowResponse)
async def get_shows(q: str):
    return ShowAPI.get_show_data(q)

@app.get("/series/vip/id")
async def get_show_info(q: str):
    return ShowAPI.get_sources(q)

@app.get("/series/vip/episode")
async def get_episode_id(q: str):
    return ShowAPI.get_episodes(q)

@app.get("/films/vip/source")
async def get_sources(q: str):
    return FilmAPI.get_sources(q)
