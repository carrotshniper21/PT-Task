# Import necessary libraries
from consumet.movies.flixhq import FlixHQ
import PySimpleGUI as sg
from PIL import Image, ImageDraw
import asyncio
import requests
from io import BytesIO

current_page = 1


# Asynchronous function to fetch movie data using FlixHQ API
async def search_movies(query, page):
    """
    Fetch movie data based on a search query and page number.

    Args:
        query (str): The search query.
        page (int): The page number for pagination.

    Returns:
        dict: The response containing movie data.
    """
    flixhq = FlixHQ()
    response = await flixhq.search(query, page)
    return response


# Asynchronous function to get trending movies using FlixHQ API
async def get_trending_movies():
    """
    Fetch trending movies using the FlixHQ API.

    Returns:
        dict: The response containing trending movie data.
    """
    flixhq = FlixHQ()
    response = await flixhq.trending_movies()
    return response


def display_movie_details(movie):
    # Fetch and resize the movie image
    image_url = movie["Image"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(image_url, headers=headers)
    image = Image.open(BytesIO(response.content)).resize((100, 150))
    bio = BytesIO()
    image.save(bio, format="PNG")
    image_data = bio.getvalue()

    # Create the GUI layout for displaying movie details
    layout = [
        [
            sg.Text(
                f"{movie['Title']} ({movie['ReleaseDate'].split('-')[0]})",
                font=("Jetbrains Mono", 20, "bold"),
                text_color="white",
                background_color="#2a2a2a",
            )
        ],
        [sg.HorizontalSeparator(color="white")],
        [
            sg.Image(data=image_data),
            sg.Text(
                movie["Description"],
                font=("Jetbrains Mono", 14),
                text_color="white",
                size=(50, 5),
                auto_size_text=True,
                background_color="#2a2a2a",
            ),
        ],
        [
            sg.Text(
                f"Duration: {movie['Duration']}",
                font=("Jetbrains Mono", 10),
                text_color="white",
                background_color="#2a2a2a",
            ),
        ],
        [
            sg.Text(
                f"Rating: {movie['Rating']}",
                font=("Jetbrains Mono", 10),
                text_color="white",
                background_color="#2a2a2a",
            ),
        ],
        [
            sg.Text(
                f"Casts: {', '.join([str(elem) for elem in movie['Casts']])}",
                font=("Jetbrains Mono", 10),
                text_color="white",
                background_color="#2a2a2a",
            )
        ],
        [
            sg.Text(
                f"Genres: {', '.join([str(elem) for elem in movie['Genres']])}",
                font=("Jetbrains Mono", 10),
                text_color="white",
                background_color="#2a2a2a",
            )
        ],
        [
            sg.Text(
                f"Production: {', '.join([str(elem) for elem in movie['Production']])}",
                font=("Jetbrains Mono", 10),
                text_color="white",
                background_color="#2a2a2a",
            )
        ],
        [
            sg.Text(
                f"Country: {', '.join([str(elem) for elem in movie['Country']])}",
                font=("Jetbrains Mono", 10),
                text_color="white",
                background_color="#2a2a2a",
            )
        ],
        [
            sg.Button(
                "Close",
                font=("Jetbrains Mono", 14),
                button_color=("white", "#2a2a2a"),
                pad=(10, 20),
            )
        ],
    ]

    # Create and display the GUI window for movie details
    window = sg.Window(
        "Movie Details",
        layout,
        size=(950, 520),
        finalize=True,
        background_color="#2a2a2a",
    )

    window.TKroot.iconbitmap("./logo.ico")

    try:
        make_background(window, movie["Cover"], window[0])
    except:
        print("INFO: Failed to fetch background image. Falling back to default.")

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == "Close":
            break

    window.close()


# Function to display search results
async def display_results(results, query):
    """
    Display search results in a GUI window.

    Args:
        results (dict): The dictionary containing search results.
        query (str): The search query.
    """

    global current_page

    # Create the GUI layout for displaying search results
    layout = [
        [
            sg.Text(
                f'Search Results for "{query}"',
                font=("Jetbrains Mono", 20),
                text_color="white",
                background_color="#2a2a2a",
            )
        ],
    ]

    movie_layout = []

    # Iterate through each movie in the results and create a layout for it
    for movie in results["Results"]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

        try:
            response = requests.get(movie["Image"], headers=headers)
        except:
            print(f"INFO: Failed to parse ({movie['Id']})")

        image = Image.open(BytesIO(response.content)).resize((100, 150))
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

    layout.append(
        [
            sg.Column(
                movie_layout,
                size=(1040, 550),
                scrollable=True,
                background_color="#2a2a2a",
                vertical_scroll_only=True,
                sbar_background_color="#262626",
                sbar_trough_color="#2a2a2a",
                sbar_arrow_width=0,
                sbar_frame_color="#2a2a2a",
            ),
        ]
    )

    layout.append(
        [
            sg.Button(
                "<<<",
                font=("Jetbrains Mono", 14),
                button_color=("white", "#2a2a2a"),
            ),
            sg.Button(
                "Previous",
                font=("Jetbrains Mono", 14),
                button_color=("white", "#2a2a2a"),
            ),
            sg.Button(
                "Next",
                font=("Jetbrains Mono", 14),
                button_color=("white", "#2a2a2a"),
            ),
            sg.Button(
                ">>>",
                font=("Jetbrains Mono", 14),
                button_color=("white", "#2a2a2a"),
            ),
            sg.Text(
                f"Page {current_page} of {results['TotalPages']}",
                font=("Jetbrains Mono", 14),
                text_color="white",
                background_color="#2a2a2a",
            ),
        ],
    )

    window = sg.Window(
        "Search Results",
        layout,
        size=(1080, 720),
        background_color="#2a2a2a",
        finalize=True,
    )

    window.TKroot.iconbitmap("./logo.ico")

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
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

        elif event == "<<<" and current_page > 1:
            current_page = 1

            try:
                results = await search_movies(query, current_page)
            except:
                sg.popup("No results found! Try Again", background_color="#2a2a2a")
                continue

            await display_results(results, query)
        elif event == "Previous" and current_page > 1:
            current_page -= 1

            try:
                results = await search_movies(query, current_page)
            except:
                sg.popup("No results found! Try Again", background_color="#2a2a2a")
                continue

            await display_results(results, query)
        elif event == "Next" and current_page < results["TotalPages"]:
            current_page += 1

            try:
                results = await search_movies(query, current_page)
            except:
                sg.popup("No results found! Try Again", background_color="#2a2a2a")
                continue

            await display_results(results, query)
        elif event == ">>>":
            current_page = results["TotalPages"]

            try:
                results = await search_movies(query, current_page - 1)
            except:
                sg.popup("No results found! Try Again", background_color="#2a2a2a")
                continue

            await display_results(results, query)

    window.close()


def roundImage(img_path, color):
    def roundCorners(im, rad):
        """
        Rounds the corners of an image to given radius
        """
        mask = Image.new("L", im.size)
        if rad > min(*im.size) // 2:
            rad = min(*im.size) // 2
        draw = ImageDraw.Draw(mask)

        draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
        draw.ellipse((0, im.height - rad * 2 - 2, rad * 2, im.height - 1), fill=255)
        draw.ellipse((im.width - rad * 2, 1, im.width, rad * 2), fill=255)
        draw.ellipse(
            (im.width - rad * 2, im.height - rad * 2, im.width - 1, im.height - 1),
            fill=255,
        )
        draw.rectangle([rad, 0, im.width - rad, im.height], fill=255)
        draw.rectangle([0, rad, im.width, im.height - rad], fill=255)

        mask = superSample(mask, 8)
        im.putalpha(mask)

        return im

    def superSample(image, sample):
        """
        Supersample an image for better edges
        image: image object
        sample: sampling multiplicator int(suggested: 2, 4, 8)
        """
        w, h = image.size

        image = image.resize((int(w * sample), int(h * sample)), resample=Image.LANCZOS)
        image = image.resize(
            (image.width // sample, image.height // sample), resample=Image.LANCZOS
        )

        return image

    def image_to_data(im):
        """
        Converts image into data to be used inside GUIs
        """
        from io import BytesIO

        with BytesIO() as output:
            im.save(output, format="PNG")
            data = output.getvalue()
        return data

    im = Image.open(img_path).convert("RGBA")
    im = roundCorners(im, 35)  # Adjust the radius for rounding
    im = superSample(im, 2)  # Adjust the sampling for better edges
    im = im.resize((50, 50), resample=Image.LANCZOS)  # Resize the image to 50x50
    im_data = image_to_data(im)

    return sg.Image(data=im_data, size=(50, 50), background_color=color)


def image_to_data(im):
    with BytesIO() as output:
        im.save(output, format="PNG")
        data = output.getvalue()
    return data


def make_background(window, file, main_frame):
    global images

    def find_frames(widget):
        widgets = list(widget.children.values())
        if isinstance(widget, (sg.tk.Frame, sg.tk.LabelFrame)):
            widget.update()
            x, y = widget.winfo_rootx() - x0, widget.winfo_rooty() - y0
            width, height = widget.winfo_width(), widget.winfo_height()
            new_im = im_.crop((x, y, x + width, y + height))
            image = sg.tk.PhotoImage(data=image_to_data(new_im))
            images.append(image)
            label = sg.tk.Label(
                widget,
                image=image,
                padx=0,
                pady=0,
                bd=0,
                bg=sg.theme_background_color(),
            )
            label.place(x=0, y=0)
            label.lower()
        for widget in widgets:
            find_frames(widget)

    size = window.size
    response = requests.get(
        file,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        },
    )
    im_ = Image.open(BytesIO(response.content)).resize(size)
    root = window.TKroot
    widgets = list(root.children.values())
    x0, y0 = root.winfo_rootx(), root.winfo_rooty()

    frame = sg.tk.Frame(root, padx=0, pady=0, bd=0)
    frame.place(x=0, y=0)
    images = []
    image = sg.tk.PhotoImage(data=image_to_data(im_))
    images.append(image)
    label = sg.tk.Label(
        frame, image=image, padx=0, pady=0, bd=0, bg=sg.theme_background_color()
    )
    label.pack()
    main_frame.Widget.master.place(in_=frame, anchor="center", relx=0.5, rely=0.5)
    frame.lower()
    frame.update()
    for widget in widgets:
        find_frames(widget)


# Main asynchronous function to run the application
async def main():
    """
    Main function to run the movie search application.
    """
    # Set GUI options
    sg.set_options(dpi_awareness=True)
    sg.theme("DarkGrey7")

    # Create the initial GUI layout
    layout = [
        [
            roundImage("./logo.ico", "#2a2a2a"),
            sg.Text(
                "Consumet Movies",
                font=("Jetbrains Mono", 24, "bold"),
                text_color="white",
                background_color="#2a2a2a",
                pad=((0, 0), 20),
            ),
        ],
        [
            sg.InputText(
                "Search Here",
                key="query",
                size=(30, 1),
                font=("Jetbrains Mono", 14, "italic"),
                background_color="#3a3a3a",
                text_color="white",
                border_width=0,
                enable_events=True,
            )
        ],
    ]

    movie_layout = []

    try:
        # Fetch trending movies
        results = await get_trending_movies()

        # Add trending movies to the GUI layout
        movie_layout.append(
            [
                sg.Text(
                    "Trending Movies",
                    font=("Jetbrains Mono", 20),
                    text_color="white",
                    background_color="#2a2a2a",
                ),
            ]
        )

        # Iterate through trending movies and add them to the GUI layout
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
                        background_color="#2a2a2a",
                        key=f"title_{movie['Id']}",
                    ),
                ]
            )
    except:
        sg.popup("Failed to fetch trending movies! Try Again Later")

    # Add movie layout to the main layout
    layout.append(
        [
            sg.Column(
                movie_layout,
                size=(1040, 600),
                scrollable=True,
                background_color="#2a2a2a",
                vertical_scroll_only=True,
                sbar_background_color="#262626",
                sbar_trough_color="#2a2a2a",
                sbar_arrow_width=0,
                sbar_frame_color="#2a2a2a",
            ),
        ],
    )

    # Create the main GUI window
    window = sg.Window(
        "Consumet Movies",
        layout,
        size=(1080, 720),
        background_color="#2a2a2a",
        finalize=True,
    )

    # Set the icon for the window
    window.TKroot.iconbitmap("./logo.ico")

    # Bind the Enter key to the search query input
    window["query"].bind("<Return>", "_Enter")
    window["query"].bind("<FocusIn>", "+FOCUS IN+")
    frame = sg.tk.Frame(
        window.TKroot, padx=0, pady=0, bd=0, bg=sg.theme_background_color()
    )
    frame.place(x=700, y=0)
    window["query"].Widget.master.place(in_=frame, x=10, y=30)

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

            await display_results(results, query)
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
        elif event == "query" + "+FOCUS IN+":
            window["query"].update("")

    window.close()


if __name__ == "__main__":
    asyncio.run(main())
