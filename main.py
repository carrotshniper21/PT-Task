PySimpleGUI_License = "eeysJwMbaHWaNilIbjneN7lUVCHelOw1ZcSDI562Ivk0RJlLdKmeVSsBba3zBzl7cYiJIjspIZkyxZppYO2pVxu8cn22V3JvR9CIIo6SM4TFcmw6OZT5cT3GMZzwAAwYMdCswzi3TsGxljjbZ6W355zYZMUERnlycYGwxOvse7W41dlxbinqRlW2ZEXPJhzcaRW29yunIJjLoWxmLuC1JtOfYEW51WlcRJmclDyfcg3BQLiaONifJoKdYGXdN1vrbCinIKsoICkE5VhqbwW5V5M0YuXPN90BIOj5olitUc39BihobSHmRxpNI9iNwgibQC209otvcpGlFjuIenSdIE65IfiKIpsxIZk2NQ1WcK3nRtvfbeW9VnytSSUbQgiPOTiyIT3sMZz2MG3hIpiLw1i3RXGMFH0PZXU3lXzBcV30VjlMZOCdI760I9jfAgzJLmzHAF3SLwzWIbwKMPjoQ5iqLXC1JtEPYkXzRDl0RLXyhdwOaUXUJWltcyypIV6KI1jZAgznLpzFAm34LizBIDwkMgjgU3ilLCClJzFMbSW0F1pwbVEcFnkcZHH3J5l8cq3DMeijO1ijJ72TabXEB9lbcnn8NVoFbImjlpwxZ1X7I1wzNL06B7nIb0W7FNp3bPCa5vjkbd2m0hiTLfCJJLJrUPExF4kZZ8HxJkl9cg3XMlihOjiaIQ0YN9yL4lxnOODzU5utNCTKEduBMOTokK3hIcng0q=l35bb15d43653095620de8a5edd0508a97787bf03d799d8c6102891da20ddeb21d2ec1c682d3fe36a1be8a709aef52e6df459b2c1768f4e1147c85eef40089e088c4f6d5253f3e4affb1a57ca3bed6d5df9ceb19b37db70202b93ed36a4ba494d76c42db945ba89e63dd2a1836be8f4babd830252925b10e2e495c8758e71d9f5c3c6f13fcff8b3f680b393017c97e77da599e815d13c27c0390db19315fd246febc196c8e0c3e50f00184044eb144c140496ed9a2f00327813c7d1c68b24dd377a345af8d6ec3dcd3826cb40662229905f37347c6938740c07a61646438d0015d4bd8c5182dbffb42e194aa806c6e5763b8fea7a1e9f7f434354d481e1ca3328e823d6e0579ba7f059ac44a2c6cc9c4e2e4beccaa00243d9738d2329a6e284c2e195f35ef74c7559dd04d44e07ed593bc12b7521d20c36f9737f62cc221c78d6cf217ac56534fc43bcaf8617800ed3726502147063ff19d09c8c1fa1894e9837b18e4cd8512c28e2ff52a3f9f5b820c24f7b74c5c8a50c18d096f46fac9a47ff20806c034a5e90543181bd909005f321e8f535ca3bc4608298cdd2e314cb8f781c5c0bf929ce01a18185a1d8ea7565594907f5d806885ede370dbe3a574f527071fa4c03f1ee767f239d7ad2d422855acbbde0a070daad5d568ba5497f1715ec582ae71443363b578315357187703f0e627ebe80e334c4f59a6fa05d32b54e48"
from consumet.movies.flixhq import FlixHQ
import PySimpleGUI as sg
from PIL import Image
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
    image_url = movie['Image']
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    response = requests.get(image_url, headers=headers)
    
    image = Image.open(BytesIO(response.content)).resize((100, 150))  # Resizing the image
    bio = BytesIO()
    image.save(bio, format="PNG")
    image_data = bio.getvalue()

    layout = [
        [sg.Text(movie['Title'], font=("Jetbrains Mono", 20), text_color="white", background_color="#2a2a2a", pad=((20,0),20))],
        [sg.HorizontalSeparator(color="white")],
        [sg.Image(data=image_data), sg.Text(movie['Description'], font=("Jetbrains Mono", 14), text_color="white", background_color="#2a2a2a", size=(50, 5), auto_size_text=True)],
        [sg.Button("Back", font=("Jetbrains Mono", 14), button_color=("white", "#007bff"), pad=((10,20),20))]
    ]

    window = sg.Window("Movie Details", layout, size=(720, 520), background_color="#2a2a2a", finalize=True)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == "Back":
            break

    window.close()

# Function to display search results
def display_results(results, query):
    layout = [
        [sg.Text(f'Search Results for "{query}"', font=("Jetbrains Mono", 20), text_color="white", background_color="#2a2a2a", pad=((20,0),20))],
        [sg.HorizontalSeparator(color="white")],
    ]

    movie_layout = []

    for movie in results['Results']:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        
        response = requests.get(movie['Image'], headers=headers)
        
        image = Image.open(BytesIO(response.content)).resize((100, 150))  # Resizing the image
        bio = BytesIO()
        image.save(bio, format="PNG")
        image_data = bio.getvalue()

        movie_layout.append([
            sg.Image(data=image_data, key=f"image_{movie['Id']}", enable_events=True),
            sg.Text(movie['Title'], font=("Jetbrains Mono", 12), background_color="#2a2a2a", text_color="white", key=f"title_{movie['Id']}"),
            sg.Text(movie['Description'], font=("Jetbrains Mono", 10), text_color="white", background_color="#2a2a2a", visible=False, key=f"description_{movie['Id']}")
        ])

    movie_layout.append([sg.Button("Close", font=("Jetbrains Mono", 14), button_color=("white", "#007bff"), pad=((10,20),20))])

    layout.append([
        sg.Column(movie_layout, size=(1040, 600), background_color="#2a2a2a", scrollable=True, vertical_scroll_only=True)
    ])

    window = sg.Window("Search Results", layout, size=(1080, 720), background_color="#2a2a2a", finalize=True)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == "Close":
            break
        elif event.startswith("image_"):
            movie_id = event.split("_")[1]
            selected_movie = [movie for movie in results['Results'] if movie['Id'] == movie_id][0]
            display_movie_details(selected_movie)

    window.close()

async def main():
    sg.set_options(dpi_awareness=True)
    sg.theme('DarkGrey7')

    icon_path = os.path.join(os.getcwd(), "icon.ico")  # Using relative path

    layout = [
        [sg.Text("Movie Search", font=("Jetbrains Mono", 24), text_color="white", background_color="#2a2a2a", pad=((20,0),20))],
        [sg.InputText(key='query', size=(30, 1), font=("Jetbrains Mono", 14), background_color="#3a3a3a", text_color="white", border_width=0, pad=((700,0),0), enable_events=True)],  
    ]

    movie_layout = []

    results = await get_trending_movies()

    movie_layout.append([
        sg.Text("Trending Movies", font=("Jetbrains Mono", 20), text_color="white", background_color="#2a2a2a")
    ])
    movie_layout.append([
        sg.HorizontalSeparator(color="white")
    ])
    
    for movie in results:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        
        response = requests.get(movie['Image'], headers=headers)
        
        image = Image.open(BytesIO(response.content)).resize((100, 150))  # Resizing the image
        bio = BytesIO()
        image.save(bio, format="PNG")
        image_data = bio.getvalue()

        movie_layout.append([
            sg.Image(data=image_data, key=f"image_{movie['Id']}", pad=5, enable_events=True),
            sg.Text(movie['Title'], font=("Jetbrains Mono", 12), text_color="white", key=f"title_{movie['Id']}", background_color="#2a2a2a"),
            sg.Text(movie['Description'], font=("Jetbrains Mono", 10),  text_color="white", background_color="#2a2a2a", visible=False, key=f"description_{movie['Id']}")
        ])

    layout.append([
        sg.Column(movie_layout, size=(1040, 600), scrollable=True, background_color="#2a2a2a", vertical_scroll_only=True)
    ])

    window = sg.Window("Consumet Movies", layout, icon=icon_path, size=(1080,720), background_color="#2a2a2a", finalize=True)
    window['query'].bind("<Return>", "_Enter")
    frame = sg.tk.Frame(window.TKroot, padx=0, pady=0, bd=0, bg=sg.theme_background_color())
    frame.place(x=0, y=0)
    window['query'].Widget.master.place(in_=frame, x=10, y=55)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break
        elif event == "query" + "_Enter":
            query = values['query'].strip()
            results = await search_movies(query, None)

            if results and 'Results' in results:
                display_results(results, query)
            else:
                sg.popup("No results found!", background_color="#2a2a2a")
        elif event.startswith("image_"):
            movie_id = event.split("_")[1]
            selected_movie = [movie for movie in results if movie['Id'] == movie_id][0]
            display_movie_details(selected_movie)

    window.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

