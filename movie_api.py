"""OMDb API client used to fetch movie metadata."""

import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# OMDb API key
API_KEY = os.getenv("OMDB_API_KEY")


class MovieAPIError(Exception):
    """Custom exception for OMDb API errors."""
    pass


def fetch_movie(title):
    """
    Fetch a movie from the OMDb API by title.

    Returns:
        dict: Movie data if found.
        None: If the movie does not exist in OMDb.

    Raises:
        MovieAPIError: If the API is not accessible or returns an error.
    """
    base_url = "http://www.omdbapi.com/"
    url = f"{base_url}?apikey={API_KEY}&t={title}"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise MovieAPIError(f"Failed to access OMDb API: {e}") from e

    data = response.json()

    # OMDb-specific "movie not found"
    if data.get("Response") == "False":
        return None

    return data
