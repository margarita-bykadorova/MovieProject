import requests

API_KEY = "YOUR_KEY"

def fetch_movie(title):
    """Fetch a movie from OMDb API by title. Return None if not found."""
    url = f"http://www.omdbapi.com/?apikey={API_KEY}&t={title}"
    response = requests.get(url)
    data = response.json()

    if data.get("Response") == "False":
        return None

    return data