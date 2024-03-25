import requests
from bs4 import BeautifulSoup
from enum import Enum
from pydantic import BaseModel
from typing import List, Optional, Tuple
from consumet.html.flixhq_html import SearchParser, PageParser
import concurrent.futures

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

    def parse_page(self, media_html: str, id: str, url: str) -> FlixHQResult: 
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

    def parse_trending_movies(self, page_html: str) -> List[str]:
        soup = BeautifulSoup(page_html, "html.parser")
        page_parser = SearchParser(soup)

        return page_parser.trending_movies()

    def parse_trending_shows(self, page_html: str) -> List[str]:
        soup = BeautifulSoup(page_html, "html.parser")
        page_parser = SearchParser(soup)

        return page_parser.trending_shows()
                
class FlixHQ:
    """
    Finds film details, parses data and returns film info
    """

    def __init__(self):
        self.base_url = "https://flixhq.to"

    def load_url(self, url, timeout=5):
        try:
            response = requests.get(url, timeout=timeout).text
            return response
        except Exception as e:
            print(f"Error fetching URL {url}: {e}")
            return None

    async def search(self, query: str, page: Optional[int]) -> FlixHQSearchResults:
        page = int(page) if page else 1

        searchHtml = requests.get(
            f"{self.base_url}/search/{query.replace(' ', '-')}?page={page}", timeout=10
        ).text

        flixhq_parser = FlixHQHTML()

        (ids, has_next_page, total_pages) = flixhq_parser.parse_search(searchHtml)

        urls = []

        for id in ids:
            url = f'{self.base_url}/{id}'
            urls.append(url)

        html = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            future_to_url = (executor.submit(self.load_url, url, 5) for url in urls)
            for future in concurrent.futures.as_completed(future_to_url):
                try:
                    data = future.result()
                except Exception as exc:
                    data = str(type(exc))
                finally:
                    html.append(data)

        results = []

        for i, media_html in enumerate(html):
            result = flixhq_parser.parse_page(media_html, ids[i], str(urls[i]))
            results.append(result)

        filmResponse = FlixHQSearchResults(
            CurrentPage=page,
            HasNextPage=has_next_page,
            TotalPages=total_pages,
            TotalResults=len(ids),
            Results=results
        )

        return filmResponse.dict()

    async def trending_movies(self) -> List[FlixHQResult]:
        trendingHtml = requests.get(
            f"{self.base_url}/home"
        )
        flixhq_parser = FlixHQHTML()
        ids = flixhq_parser.parse_trending_movies(trendingHtml.text)

        urls = []

        for id in ids:
            url = f'{self.base_url}/{id}'
            urls.append(url)

        html = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            future_to_url = (executor.submit(self.load_url, url, 5) for url in urls)
            for future in concurrent.futures.as_completed(future_to_url):
                try:
                    data = future.result()
                except Exception as exc:
                    data = str(type(exc))
                finally:
                    html.append(data)

        results = []

        for i, media_html in enumerate(html):
            result = flixhq_parser.parse_page(media_html, ids[i], str(urls[i]))
            results.append(result.dict())

        return results


    async def trending_shows(self) -> List[FlixHQResult]:
        trendingHtml = requests.get(
            f"{self.base_url}/home"
        )
        flixhq_parser = FlixHQHTML()
        ids = flixhq_parser.parse_trending_shows(trendingHtml.text)

        urls = []

        for id in ids:
            url = f'{self.base_url}/{id}'
            urls.append(url)

        html = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            future_to_url = (executor.submit(self.load_url, url, 5) for url in urls)
            for future in concurrent.futures.as_completed(future_to_url):
                try:
                    data = future.result()
                except Exception as exc:
                    data = str(type(exc))
                finally:
                    html.append(data)

        results = []

        for i, media_html in enumerate(html):
            result = flixhq_parser.parse_page(media_html, ids[i], str(urls[i]))
            results.append(result.dict())

        return results