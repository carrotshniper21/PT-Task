import requests
from bs4 import BeautifulSoup
from enum import Enum
from pydantic import BaseModel
from typing import List, Optional, Tuple
from consumet.html.flixhq_html import SearchParser, PageParser
import concurrent.futures


# Enum to represent media types
class MediaType(Enum):
    TV = "tv"
    MOVIE = "movie"


# Defines the structure of a single FlixHQ result
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
    Casts: List[str]
    Tags: List[str]


# Defines the structure of a entire FlixHQ page
class FlixHQSearchResults(BaseModel):
    CurrentPage: int
    HasNextPage: bool
    TotalPages: int
    TotalResults: int
    Results: List[FlixHQResult]


# Parses the HTML content from FlixHQ
class FlixHQHTML:
    """
    A class to parse HTML content from FlixHQ website.
    """

    def parse_search(self, page_html: str) -> Tuple[List[str], bool, int]:
        """
        Parse search page HTML to extract movie/TV show IDs, pagination info.

        Args:
            page_html (str): The HTML content of the search page.

        Returns:
            Tuple[List[str], bool, int]: A tuple containing the list of IDs,
                                          a boolean indicating if there's a next page,
                                          and the total number of pages.
        """
        soup = BeautifulSoup(page_html, "html.parser")
        search_parser = SearchParser(soup)
        return (
            search_parser.page_ids(),
            search_parser.has_next_page(),
            search_parser.total_pages(),
        )

    def parse_page(self, media_html: str, id: str, url: str) -> FlixHQResult:
        """
        Parse media page HTML to extract movie/TV show details.

        Args:
            media_html (str): The HTML content of the media page.
            id (str): The ID of the media.
            url (str): The URL of the media.

        Returns:
            FlixHQResult: An instance of FlixHQResult containing the parsed details.
        """
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
            Casts=page_parser.label(5, "Casts:"),
            Tags=page_parser.label(6, "Tags:"),
        )

        return result

    def parse_trending_movies(self, page_html: str) -> List[str]:
        """
        Parse trending movies page HTML to extract movie IDs.

        Args:
            page_html (str): The HTML content of the trending movies page.

        Returns:
            List[str]: A list of trending movie IDs.
        """
        soup = BeautifulSoup(page_html, "html.parser")
        page_parser = SearchParser(soup)
        return page_parser.trending_movies()

    def parse_trending_shows(self, page_html: str) -> List[str]:
        """
        Parse trending shows page HTML to extract TV show IDs.

        Args:
            page_html (str): The HTML content of the trending shows page.

        Returns:
            List[str]: A list of trending TV show IDs.
        """
        soup = BeautifulSoup(page_html, "html.parser")
        page_parser = SearchParser(soup)
        return page_parser.trending_shows()


# Class to interact with FlixHQ API
class FlixHQ:
    """
    Main code to scrape from FlixHQ
    """

    def __init__(self):
        self.base_url = "https://flixhq.to"

    def load_url(self, url, timeout=5) -> str:
        """
        Load a URL and return its content.

        Args:
            url (str): The URL to fetch.
            timeout (int, optional): The timeout for the request. Defaults to 5.

        Returns:
            str: The content of the URL.
        """
        try:
            response = requests.get(url, timeout=timeout).text
            return response
        except Exception as e:
            print(f"Error fetching URL {url}: {e}")
            return None

    async def search(self, query: str, page: Optional[int]) -> FlixHQSearchResults:
        """
        Search for movies/TV shows on FlixHQ.

        Args:
            query (str): The search query.
            page (Optional[int]): The page number for pagination.

        Returns:
            FlixHQSearchResults: A list of search results.
        """
        page = int(page) if page else 1

        searchHtml = requests.get(
            f"{self.base_url}/search/{query.replace(' ', '-')}?page={page}", timeout=10
        ).text

        flixhq_parser = FlixHQHTML()

        (ids, has_next_page, total_pages) = flixhq_parser.parse_search(searchHtml)

        urls = [f"{self.base_url}/{id}" for id in ids]

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

        results = [
            flixhq_parser.parse_page(media_html, ids[i], str(urls[i])).dict()
            for i, media_html in enumerate(html)
        ]

        filmResponse = FlixHQSearchResults(
            CurrentPage=page,
            HasNextPage=has_next_page,
            TotalPages=total_pages,
            TotalResults=len(ids),
            Results=results,
        )

        return filmResponse.dict()

    async def trending_movies(self) -> List[FlixHQResult]:
        """
        Fetch trending movies from FlixHQ.

        Returns:
            List[FlixHQResult]: A list of trending movie details.
        """
        trendingHtml = requests.get(f"{self.base_url}/home").text
        flixhq_parser = FlixHQHTML()
        ids = flixhq_parser.parse_trending_movies(trendingHtml)

        urls = [f"{self.base_url}/{id}" for id in ids]

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

        results = [
            flixhq_parser.parse_page(media_html, ids[i], str(urls[i])).dict()
            for i, media_html in enumerate(html)
        ]

        return results

    async def trending_shows(self) -> List[FlixHQResult]:
        """
        Fetch trending TV shows from FlixHQ.

        Returns:
            List[FlixHQResult]: A list of trending TV show details.
        """
        trendingHtml = requests.get(f"{self.base_url}/home").text
        flixhq_parser = FlixHQHTML()
        ids = flixhq_parser.parse_trending_shows(trendingHtml)

        urls = [f"{self.base_url}/{id}" for id in ids]

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

        results = [
            flixhq_parser.parse_page(media_html, ids[i], str(urls[i])).dict()
            for i, media_html in enumerate(html)
        ]

        return results
