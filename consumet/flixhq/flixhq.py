import httpx
from bs4 import BeautifulSoup
from enum import Enum
from pydantic import BaseModel
from typing import List, Optional, Tuple
from consumet.flixhq.html.flixhq_html import SearchParser, PageParser

class MediaType(Enum):
    TV = "tv"
    MOVIE = "movie"

class FlixHQResult(BaseModel):
    Id: str
    Cover: str
    Title: str
    Url: str
    Image: str
    ReleaseDate: str
    MediaType: MediaType
    Genres: List[str]
    Description: str
    Rating: str
    Quality: str
    Duration: str
    Country: List[str]
    Production: List[str]
    Cast: List[str]
    Tags: List[str]

class FlixHQSearchResults(BaseModel):
    CurrentPage: int
    HasNextPage: bool
    TotalPages: int
    TotalResults: int
    Results: List[FlixHQResult]

class FlixHQHTML:
    def parse_search(self, page_html: str) -> Tuple[List[str], bool, int]:
        soup = BeautifulSoup(page_html, "html.parser")
        search_parser = SearchParser(soup)
        return ( search_parser.page_ids(), search_parser.has_next_page(), search_parser.total_pages()) 

    def single_page(self, media_html: str, id: str, url: str) -> FlixHQResult: 
        soup = BeautifulSoup(media_html, "html.parser")
        page_parser = PageParser(soup)

        result = FlixHQResult(
            Id=id,
            Cover=page_parser.cover(),
            Title=page_parser.title(),
            Url=url,
            Image=page_parser.image(),
            ReleaseDate=page_parser.label(3, "Released:")[0],
            MediaType=page_parser.media_type(id),
            Genres=page_parser.label(2, "Genre:"),
            Description=page_parser.description(),
            Rating=page_parser.rating(),
            Quality=page_parser.quality(),
            Duration=page_parser.duration(),
            Country=page_parser.label(1, "Country:"),
            Production=page_parser.label(4, "Production:"),
            Cast=page_parser.label(5, "Casts:"),
            Tags=page_parser.label(6, "Tags:")
        )

        return result
                
class FlixHQ:
    """
    Finds film details, parses data and returns film info
    """

    def __init__(self):
        self.base_url = "https://flixhq.to"

    async def processResults(self, searchResults: str, url: str, page: int) -> FlixHQSearchResults:
        async with httpx.AsyncClient() as client:
            flixhq_parser = FlixHQHTML()
            search_info = flixhq_parser.parse_search(searchResults)

            results = []

            for id in search_info[0]:
                media_html = await client.get(f"{self.base_url}/{id}", timeout=10)
                result = flixhq_parser.single_page(media_html, id, str(media_html.url))
                results.append(result.dict())

            filmResponse = FlixHQSearchResults(
                CurrentPage=page,
                HasNextPage=search_info[1],
                TotalPages=search_info[2],
                TotalResults=len(search_info[0]),
                Results=results
            )

            return filmResponse.dict()

    async def search(self, query: str, page: Optional[int]) -> FlixHQSearchResults:
        async with httpx.AsyncClient() as client:
            page = int(page) if page else 1

            searchResults = await client.get(
                f"{self.base_url}/search/{query.replace(' ', '-')}?page={page}", timeout=10
            )
            return await self.processResults(searchResults.text, str(searchResults.url), page)
