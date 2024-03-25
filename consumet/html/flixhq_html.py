import re
from enum import Enum


class MediaType(Enum):
    TV = "tv"
    MOVIE = "movie"


class SearchParser:
    def __init__(self, elements):
        self.elements = elements

    def page_ids(self):
        return [
            a.get("href", "").lstrip("/").strip()
            for a in self.elements.select("div.film-poster > a")
        ]

    def total_pages(self):
        total_pages_attr = self.elements.select_one(
            "div.pre-pagination:nth-child(3) > nav:nth-child(1) > ul:nth-child(1) > li.page-item:last-child a"
        )["href"]

        page_number_match = re.search(r"page=(\d+)$", total_pages_attr)

        if page_number_match:
            total_pages = int(page_number_match.group(1))
            return total_pages

        return 1

    def has_next_page(self):
        element = self.elements.select_one(
            "div.pre-pagination:nth-child(3) > nav:nth-child(1) > ul:nth-child(1) > li:nth-child(1)"
        )
        return "active" in element.get("class", [])

    def trending_movies(self):
        return [
            a.get("href", "").lstrip("/").strip()
            for a in self.elements.select(
                "div#trending-movies div.film_list-wrap div.flw-item div.film-poster a"
            )
        ]

    def trending_shows(self):
        return [
            a.get("href", "").lstrip("/").strip()
            for a in self.elements.select(
                "div#trending-tv div.film_list-wrap div.flw-item div.film-poster a"
            )
        ]


class PageParser:
    def __init__(self, elements):
        self.elements = elements

    def image(self):
        image_element = self.elements.select_one("div.m_i-d-poster > div > img")

        if image_element:
            image_src = image_element.get("src", "")
            return image_src

        return ""

    def title(self):
        title_element = self.elements.select_one(
            "#main-wrapper > div.movie_information > div > div.m_i-detail > div.m_i-d-content > h2"
        )

        if title_element:
            return title_element.get_text().strip()

        return ""

    def cover(self):
        cover_attr = self.elements.select_one("div.w_b-cover")["style"]

        if cover_attr:
            cover_url = cover_attr.replace("background-image: url(", "").replace(
                ")", ""
            )
            return cover_url

        return ""

    def media_type(self, id):
        id_parts = id.split("/")
        if id_parts[0] == MediaType.TV.value:
            return MediaType.TV.value
        elif id_parts[0] == MediaType.MOVIE.value:
            return MediaType.MOVIE.value
        else:
            raise ValueError("Invalid media type")

    def label(self, index, label):
        elements = self.elements.select(
            f"div.m_i-d-content > div.elements > div:nth-child({index})"
        )

        if elements:
            return [
                s.strip() for s in elements[0].get_text().replace(label, "").split(",")
            ]

        return []

    def description(self):
        description_element = self.elements.select_one(
            "#main-wrapper > div.movie_information > div > div.m_i-detail > div.m_i-d-content > div.description"
        )

        if description_element:
            return description_element.get_text().strip()

        return ""

    def quality(self):
        quality_element = self.elements.select_one("span.item:nth-child(1)")

        if quality_element:
            return quality_element.get_text().strip()

        return ""

    def rating(self):
        rating_element = self.elements.select_one("span.item:nth-child(2)")

        if rating_element:
            return rating_element.get_text().strip()

        return ""

    def duration(self):
        duration_element = self.elements.select_one("span.item:nth-child(3)")

        if duration_element:
            return duration_element.get_text().strip()

        return ""
