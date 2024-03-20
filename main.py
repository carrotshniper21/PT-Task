import requests
import PySimpleGUI as sg

# Function to fetch movie data from OMDB API
def search_movies(search_term):
    url = "http://www.omdbapi.com/"
    params = {
        "apikey": "YOUR_OMDB_API_KEY",  # Replace 'YOUR_OMDB_API_KEY' with your actual OMDB API key
        "s": search_term,
        "type": "movie"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if 'Search' in data:
        return data['Search']
    else:
        return None

# Function to display search results
def display_results(results):
    layout = [
        [sg.Text("Search Results", font=("Helvetica", 16), text_color="white")],
        [sg.HorizontalSeparator(color="white")],
        [sg.Column([[sg.Image(data=result['Poster'], key=f"poster_{i}", size=(200, 300))],
                    [sg.Text(result['Title'], size=(20, 1), text_color="white", font=("Helvetica", 12), justification="center")]],
                   element_justification='center', pad=(10, 10))
         for i, result in enumerate(results)]
    ]

    window = sg.Window("Movie Search Results", layout, background_color="black")

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break

    window.close()

# Main function
def main():
    sg.theme('DarkBlack')  # Set the theme to black

    layout = [
        [sg.Text("Movie Search", font=("Helvetica", 16), text_color="white")],
        [sg.InputText(key='search_term', size=(30, 1)), sg.Button("Search")],
    ]

    window = sg.Window("Movie Search", layout, background_color="black")

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Search":
            search_term = values['search_term']
            results = search_movies(search_term)

            if results:
                display_results(results)
            else:
                sg.popup("No results found!")

    window.close()

if __name__ == "__main__":
    main()

