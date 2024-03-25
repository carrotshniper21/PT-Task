import re
from enum import Enum
from typing import List


class MediaType(Enum):
    TV = "tv"
    MOVIE = "movie"


class SearchParser:
    """
    Parses the search page HTML content from FlixHQ.
    """

    def __init__(self, elements):
        """
        Initialize the SearchParser with the given elements.

        Args:
            elements: BeautifulSoup elements from the search page.
        """
        self.elements = elements

    def page_ids(self) -> List[str]:
        """
        Extract movie/TV show IDs from the search page.

        Returns:
            List[str]: A list of movie/TV show IDs.
        """
        return [
            a.get("href", "").lstrip("/").strip()
            for a in self.elements.select("div.film-poster > a")
        ]

    def total_pages(self) -> int:
        """
        Extract the total number of pages from the search page.

        Returns:
            int: Total number of pages.
        """
        total_pages_attr = self.elements.select_one(
            "div.pre-pagination:nth-child(3) > nav:nth-child(1) > ul:nth-child(1) > li.page-item:last-child a"
        )["href"]

        page_number_match = re.search(r"page=(\d+)$", total_pages_attr)

        if page_number_match:
            total_pages = int(page_number_match.group(1))
            return total_pages

        return 1

    def has_next_page(self) -> bool:
        """
        Check if there is a next page available.

        Returns:
            bool: True if there is a next page, otherwise False.
        """
        element = self.elements.select_one(
            "div.pre-pagination:nth-child(3) > nav:nth-child(1) > ul:nth-child(1) > li:nth-child(1)"
        )
        return "active" in element.get("class", [])

    def trending_movies(self) -> List[str]:
        """
        Extract trending movie IDs.

        Returns:
            List[str]: A list of trending movie IDs.
        """
        return [
            a.get("href", "").lstrip("/").strip()
            for a in self.elements.select(
                "div#trending-movies div.film_list-wrap div.flw-item div.film-poster a"
            )
        ]

    def trending_shows(self) -> List[str]:
        """
        Extract trending TV show IDs.

        Returns:
            List[str]: A list of trending TV show IDs.
        """
        return [
            a.get("href", "").lstrip("/").strip()
            for a in self.elements.select(
                "div#trending-tv div.film_list-wrap div.flw-item div.film-poster a"
            )
        ]


# Class to parse movie/TV show page HTML content from FlixHQ
class PageParser:
    """
    A class to parse the movie/TV show page HTML content from FlixHQ.
    """

    def __init__(self, elements):
        """
        Initialize the PageParser with the given elements.

        Args:
            elements: BeautifulSoup elements from the movie/TV show page.
        """
        self.elements = elements

    def image(self) -> str:
        """
        Extract the image URL of the movie/TV show.

        Returns:
            str: The image URL.
        """
        image_element = self.elements.select_one("div.m_i-d-poster > div > img")

        if image_element:
            image_src = image_element.get("src", "")
            return image_src

        return ""

    def title(self) -> str:
        """
        Extract the title of the movie/TV show.

        Returns:
            str: The title.
        """
        title_element = self.elements.select_one(
            "#main-wrapper > div.movie_information > div > div.m_i-detail > div.m_i-d-content > h2"
        )

        if title_element:
            return title_element.get_text().strip()

        return ""

    def cover(self) -> str:
        """
        Extract the cover URL of the movie/TV show.

        Returns:
            str: The cover URL.
        """
        cover_attr = self.elements.select_one("div.w_b-cover")["style"]

        if cover_attr:
            cover_url = cover_attr.replace("background-image: url(", "").replace(
                ")", ""
            )
            return cover_url

        return ""

    def media_type(self, id) -> str:
        """
        Determine the media type (TV or Movie) based on the ID.

        Args:
            id (str): The movie/TV show ID.

        Returns:
            str: The media type ("tv" or "movie").

        Raises:
            ValueError: If the media type is invalid.
        """
        id_parts = id.split("/")
        if id_parts[0] == MediaType.TV.value:
            return MediaType.TV.value
        elif id_parts[0] == MediaType.MOVIE.value:
            return MediaType.MOVIE.value
        else:
            raise ValueError("Invalid media type")

    def label(self, index, label) -> List[str]:
        """
        Extract a specific label's content from the movie/TV show page.

        Args:
            index (int): The index of the label.
            label (str): The label to extract.

        Returns:
            List[str]: A list of label content.
        """
        elements = self.elements.select(
            f"div.m_i-d-content > div.elements > div:nth-child({index})"
        )

        if elements:
            return [
                s.strip() for s in elements[0].get_text().replace(label, "").split(",")
            ]

        return [""]

    def description(self) -> str:
        """
        Extract the description of the movie/TV show.

        Returns:
            str: The description.
        """
        description_element = self.elements.select_one(
            "#main-wrapper > div.movie_information > div > div.m_i-detail > div.m_i-d-content > div.description"
        )

        if description_element:
            return description_element.get_text().strip()

        return ""

    def quality(self) -> str:
        """
        Extract the quality of the movie/TV show.

        Returns:
            str: The quality.
        """
        quality_element = self.elements.select_one("span.item:nth-child(1)")

        if quality_element:
            return quality_element.get_text().strip()

        return ""

    def rating(self) -> str:
        """
        Extract the rating of the movie/TV show.

        Returns:
            str: The rating.
        """
        rating_element = self.elements.select_one("span.item:nth-child(2)")

        if rating_element:
            return rating_element.get_text().strip()

        return ""

    def duration(self) -> str:
        """
        Extract the duration of the movie/TV show.

        Returns:
            str: The duration.
        """
        duration_element = self.elements.select_one("span.item:nth-child(3)")

        if duration_element:
            return duration_element.get_text().strip()

        return ""
