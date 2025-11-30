import requests

API_KEY = "54373471" #"YOUR_KEY_HERE"


class MovieAPIError(Exception):
    """Custom exception for OMDb API errors."""
    pass


def fetch_movie(title):
    """
    Fetch a movie from OMDb API by title.
    Returns a dict with movie data, or None if movie not found.
    Raises MovieAPIError if the API is not accessible.
    """
    url = f"http://www.omdbapi.com/?apikey={API_KEY}&t={title}"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Network error, timeout, DNS error, etc.
        raise MovieAPIError(f"Failed to access OMDb API: {e}") from e

    data = response.json()

    # OMDb-specific "movie not found"
    if data.get("Response") == "False":
        return None

    return data
