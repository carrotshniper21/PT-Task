from consumet.movies.flixhq import FlixHQ
import PySimpleGUI as sg
from PIL import Image
import asyncio
import requests
from io import BytesIO
import os


# Function to fetch movie data via FlixHQ
async def search_movies(query, page):
    flixhq = FlixHQ()
    response = await flixhq.search(query, page)
    return response


async def get_trending_movies():
    flixhq = FlixHQ()
    response = await flixhq.trending_movies()
    return response


# Function to display movie details
def display_movie_details(movie):
    image_url = movie["Image"]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(image_url, headers=headers)

    image = Image.open(BytesIO(response.content)).resize(
        (100, 150)
    )  
    bio = BytesIO()
    image.save(bio, format="PNG")
    image_data = bio.getvalue()

    layout = [
        [
            sg.Text(
                f"{movie['Title']} ({movie['ReleaseDate'].split('-')[0]})",
                font=("Jetbrains Mono", 20),
                text_color="white",
                background_color="#2a2a2a",
                pad=((20, 0), 20),
            )
        ],
        [sg.HorizontalSeparator(color="white")],
        [
            sg.Image(data=image_data),
            sg.Text(
                movie["Description"],
                font=("Jetbrains Mono", 14),
                text_color="white",
                background_color="#2a2a2a",
                size=(50, 5),
                auto_size_text=True,
            ),
        ],
        [
            sg.Text(
                ", ".join([str(elem) for elem in movie["Production"]]),
                text_color="white",
                background_color="#2a2a2a",
            )
        ],
        [
            sg.Text(
                ", ".join([str(elem) for elem in movie["Country"]]),
                text_color="white",
                background_color="#2a2a2a",
            )
        ],
        [
            sg.Button(
                "Back",
                font=("Jetbrains Mono", 14),
                button_color=("white", "#007bff"),
                pad=((10, 20), 20),
            )
        ],
    ]

    window = sg.Window(
        "Movie Details",
        layout,
        size=(950, 520),
        background_color="#2a2a2a",
        finalize=True,
    )

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == "Back":
            break

    window.close()


# Function to display search results
def display_results(results, query):
    layout = [
        [
            sg.Text(
                f'Search Results for "{query}"',
                font=("Jetbrains Mono", 20),
                text_color="white",
                background_color="#2a2a2a",
                pad=((20, 0), 20),
            )
        ],
        [sg.HorizontalSeparator(color="white")],
    ]

    movie_layout = []

    for movie in results["Results"]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

        response = requests.get(movie["Image"], headers=headers)

        image = Image.open(BytesIO(response.content)).resize(
            (100, 150)
        )  
        bio = BytesIO()
        image.save(bio, format="PNG")
        image_data = bio.getvalue()

        movie_layout.append(
            [
                sg.Image(
                    data=image_data, key=f"image_{movie['Id']}", enable_events=True
                ),
                sg.Text(
                    movie["Title"],
                    font=("Jetbrains Mono", 12),
                    background_color="#2a2a2a",
                    text_color="white",
                    key=f"title_{movie['Id']}",
                ),
                sg.Text(
                    movie["Description"],
                    font=("Jetbrains Mono", 10),
                    text_color="white",
                    background_color="#2a2a2a",
                    visible=False,
                    key=f"description_{movie['Id']}",
                ),
            ]
        )

    movie_layout.append(
        [
            sg.Button(
                "Close",
                font=("Jetbrains Mono", 14),
                button_color=("white", "#007bff"),
                pad=((10, 20), 20),
            )
        ]
    )

    layout.append(
        [
            sg.Column(
                movie_layout,
                size=(1040, 600),
                background_color="#2a2a2a",
                scrollable=True,
                vertical_scroll_only=True,
            )
        ]
    )

    window = sg.Window(
        "Search Results",
        layout,
        size=(1080, 720),
        background_color="#2a2a2a",
        finalize=True,
    )

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == "Close":
            break
        elif event.startswith("image_"):
            movie_id = event.split("_")[1]
            try:
                selected_movie = [
                    movie for movie in results["Results"] if movie["Id"] == movie_id
                ][0]
            except:
                sg.popup(
                    "Failed to select movie! Try Again", background_color="#2a2a2a"
                )
                continue

            display_movie_details(selected_movie)

    window.close()


async def main():
    sg.set_options(dpi_awareness=True)
    sg.theme("DarkGrey7")

    icon_path = os.path.join(os.getcwd(), "icon.ico")  # Using relative path

    layout = [
        [
            sg.Text(
                "Movie Search",
                font=("Jetbrains Mono", 24),
                text_color="white",
                background_color="#2a2a2a",
                pad=((20, 0), 20),
            )
        ],
        [
            sg.InputText(
                key="query",
                size=(30, 1),
                font=("Jetbrains Mono", 14),
                background_color="#3a3a3a",
                text_color="white",
                border_width=0,
                pad=((700, 0), 0),
                enable_events=True,
            )
        ],
    ]

    movie_layout = []

    try:
        results = await get_trending_movies()

        movie_layout.append(
            [
                sg.Text(
                    "Trending Movies",
                    font=("Jetbrains Mono", 20),
                    text_color="white",
                    background_color="#2a2a2a",
                )
            ]
        )
        movie_layout.append([sg.HorizontalSeparator(color="white")])

        for movie in results:
            response = requests.get(
                movie["Image"],
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
                },
            )

            image = Image.open(BytesIO(response.content)).resize((100, 150))
            bio = BytesIO()
            image.save(bio, format="PNG")
            image_data = bio.getvalue()

            movie_layout.append(
                [
                    sg.Image(
                        data=image_data,
                        key=f"image_{movie['Id']}",
                        pad=5,
                        enable_events=True,
                    ),
                    sg.Text(
                        movie["Title"],
                        font=("Jetbrains Mono", 12),
                        text_color="white",
                        key=f"title_{movie['Id']}",
                        background_color="#2a2a2a",
                    ),
                    sg.Text(
                        movie["Description"],
                        font=("Jetbrains Mono", 10),
                        text_color="white",
                        background_color="#2a2a2a",
                        visible=False,
                        key=f"description_{movie['Id']}",
                    ),
                ]
            )
    except:
        sg.popup("Failed to fetch trending movies! Try Again Later")

    layout.append(
        [
            sg.Column(
                movie_layout,
                size=(1040, 600),
                scrollable=True,
                background_color="#2a2a2a",
                vertical_scroll_only=True,
            )
        ]
    )

    window = sg.Window(
        "Consumet Movies",
        layout,
        icon=icon_path,
        size=(1080, 720),
        background_color="#2a2a2a",
        finalize=True,
    )
    window["query"].bind("<Return>", "_Enter")
    frame = sg.tk.Frame(
        window.TKroot, padx=0, pady=0, bd=0, bg=sg.theme_background_color()
    )
    frame.place(x=0, y=0)
    window["query"].Widget.master.place(in_=frame, x=10, y=55)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break
        elif event == "query" + "_Enter":
            query = values["query"].strip()
            try:
                results = await search_movies(query, None)
            except:
                sg.popup("No results found! Try Again", background_color="#2a2a2a")
                continue

            display_results(results, query)
        elif event.startswith("image_"):
            movie_id = event.split("_")[1]
            try:
                selected_movie = [
                    movie for movie in results if movie["Id"] == movie_id
                ][0]
            except:
                sg.popup(
                    "Failed to select movie! Try Again", background_color="#2a2a2a"
                )
                continue

            display_movie_details(selected_movie)

    window.close()


if __name__ == "__main__":
    asyncio.run(main())
