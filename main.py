from consumet.flixhq.flixhq import FlixHQ
import PySimpleGUI as sg
import asyncio

# Function to fetch movie data via FlixHQ
async def search_movies(search_term):
    flixhq = FlixHQ()
    response = await flixhq.search(search_term, None)
    return response['Results']

# Function to display search results
async def display_results(results):
    layout = [
        [sg.Text("Search Results", font=("Helvetica", 16), text_color="white")],
        [sg.HorizontalSeparator(color="white")],
        [sg.Column([[sg.Text(result['Title'], size=(20, 1), text_color="white", font=("Helvetica", 12), justification="center")]],
                   element_justification='center', pad=(10, 10))
         for i, result in enumerate(results)]
    ]

    window = sg.Window("Movie Search Results", layout, background_color="black")

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break

    window.close()

async def main():
    sg.theme('DarkBlack')

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
            results = await search_movies(search_term)

            if results:
                await display_results(results)
            else:
                sg.popup("No results found!")

    window.close()

if __name__ == "__main__":
    asyncio.run(main())
