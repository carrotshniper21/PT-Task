from consumet.movies.flixhq import FlixHQ
import PySimpleGUI as sg
from PIL import Image
import requests
from io import BytesIO
import os
import asyncio

# Function to fetch movie data via FlixHQ
async def search_movies(search_term, page):
    flixhq = FlixHQ()
    response = await flixhq.search(search_term, page)
    return response

async def get_trending_movies():
    flixhq = FlixHQ()
    response = await flixhq.trending_movies()
    return response

# Function to display movie details
def display_movie_details(movie):
    image_url = movie['Image']
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    response = requests.get(image_url, headers=headers)
    
    image = Image.open(BytesIO(response.content)).resize((100, 150))  # Resizing the image
    bio = BytesIO()
    image.save(bio, format="PNG")
    image_data = bio.getvalue()

    layout = [
        [sg.Text(movie['Title'], font=("Helvetica", 20), text_color="white", background_color="#2a2a2a", pad=((20,0),20))],
        [sg.HorizontalSeparator(color="white")],
        [sg.Image(data=image_data), sg.Text(movie['Description'], font=("Helvetica", 14), text_color="white", background_color="#2a2a2a", size=(50, 5), auto_size_text=True)],
        [sg.Button("Back", font=("Helvetica", 14), button_color=("white", "#007bff"), pad=((10,20),20))]
    ]

    window = sg.Window("Movie Details", layout, size=(720, 520), background_color="#2a2a2a", finalize=True)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == "Back":
            break

    window.close()

# Function to display search results
def display_results(results):
    layout = [
        [sg.Text("Search Results", font=("Helvetica", 20), text_color="white", background_color="#2a2a2a", pad=((20,0),20))],
        [sg.HorizontalSeparator(color="white")],
    ]

    movie_layout = []

    for movie in results['Results']:
        image_url = movie['Image']
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        
        response = requests.get(image_url, headers=headers)
        
        image = Image.open(BytesIO(response.content)).resize((100, 150))  # Resizing the image
        bio = BytesIO()
        image.save(bio, format="PNG")
        image_data = bio.getvalue()

        movie_layout.append([
            sg.Image(data=image_data, key=f"image_{movie['Id']}", enable_events=True),
            sg.Text(movie['Title'], font=("Helvetica", 12), text_color="white", background_color="#2a2a2a", key=f"title_{movie['Id']}"),
            sg.Text(movie['Description'], font=("Helvetica", 10), text_color="white", background_color="#2a2a2a", visible=False, key=f"description_{movie['Id']}")
        ])

    movie_layout.append([sg.Button("Close", font=("Helvetica", 14), button_color=("white", "#007bff"), pad=((10,20),20))])

    layout.append([
        sg.Column(movie_layout, size=(800, 400), scrollable=True, vertical_scroll_only=True)
    ])

    window = sg.Window("Movie Search Results", layout, size=(1080, 720), background_color="#2a2a2a", finalize=True)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == "Close":
            break
        elif event.startswith("image_"):
            movie_id = event.split("_")[1]
            selected_movie = next(movie for movie in results['Results'] if movie['Id'] == movie_id)
            display_movie_details(selected_movie)

    window.close()


async def main():
    sg.set_options(dpi_awareness=True)
    sg.theme('DarkGrey7')

    icon_path = os.path.join(os.getcwd(), "icon.ico")  # Using relative path

    layout = [
        [sg.Text("Movie Search", font=("Helvetica", 24), text_color="white", background_color="#2a2a2a", pad=((20,0),20))],
        [sg.InputText(key='search_term', size=(30, 1), font=("Helvetica", 14), background_color="#3a3a3a", text_color="white", border_width=0, pad=((700,0),0), enable_events=True)],  
    ]

    movie_layout = []

    results = await get_trending_movies()

    movie_layout.append([
        sg.Text("Trending Movies", font=("Helvetica", 20), text_color="white", background_color="#2a2a2a")
    ])
    movie_layout.append([
        sg.HorizontalSeparator(color="white")
    ])

    for movie in results:
        image_url = movie['Image']
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        
        response = requests.get(image_url, headers=headers)
        
        image = Image.open(BytesIO(response.content)).resize((100, 150))  # Resizing the image
        bio = BytesIO()
        image.save(bio, format="PNG")
        image_data = bio.getvalue()

        movie_layout.append([
            sg.Image(data=image_data, key=f"image_{movie['Id']}", enable_events=True),
            sg.Text(movie['Title'], font=("Helvetica", 12), text_color="white", background_color="#2a2a2a", key=f"title_{movie['Id']}"),
            sg.Text(movie['Description'], font=("Helvetica", 10), text_color="white", background_color="#2a2a2a", visible=False, key=f"description_{movie['Id']}")
        ])

    layout.append([
        sg.Column(movie_layout, size=(800, 400), scrollable=True, vertical_scroll_only=True)
    ])

    window = sg.Window("Movie Search", layout, icon=icon_path, size=(1080,720), background_color="#2a2a2a", finalize=True)
    window['search_term'].bind("<Return>", "_Enter")
    frame = sg.tk.Frame(window.TKroot, padx=0, pady=0, bd=0, bg=sg.theme_background_color())
    frame.place(x=0, y=0)
    window['search_term'].Widget.master.place(in_=frame, x=10, y=55)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break
        elif event == "search_term" + "_Enter":
            search_term = values['search_term'].strip()
            results = await search_movies(search_term, None)

            if results:
                display_results(results)
            else:
                sg.popup("No results found!", background_color="#2a2a2a")
        elif event.startswith("image_"):
            movie_id = event.split("_")[1]
            selected_movie = next(movie for movie in results if movie['Id'] == movie_id)
            display_movie_details(selected_movie)

    window.close()

if __name__ == "__main__":
    asyncio.run(main())
