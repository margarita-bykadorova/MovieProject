"""
Movies Database Application

Console-based Python program to manage a personal movie collection.
Features:
- SQL-based storage using SQLite
- Movie data fetched from the OMDb API
- CLI for listing, adding, deleting, updating, searching, and analyzing movies
- Static website generation (HTML + CSS) showing the movie library
"""

import sys
import statistics
import random
import difflib
from colorama import Fore, init
from storage import movie_storage_sql as movie_storage
import movie_api
init(autoreset=True)

MIN_YEAR = 1900
MAX_YEAR = 2025
MIN_RATING = 0
MAX_RATING = 10
MIN_MENU_CHOICE = 0
MAX_MENU_CHOICE = 9

active_user_id = None
active_user_name = ""

# ------------------ input helpers ------------------

def get_nonempty_string(prompt):
    """Ask the user for a non-empty string."""

    while True:
        value = input(Fore.GREEN + prompt).strip()
        if not value:
            print(Fore.WHITE + "Input cannot be empty. Please try again.")
            continue
        return value


def get_valid_int(prompt, min_value, max_value):
    """Ask the user for an integer between min_value and max_value (inclusive)."""

    while True:
        try:
            value = int(input(Fore.GREEN + prompt))
            if value < min_value or value > max_value:
                print(f"{Fore.WHITE}Please enter a number between {min_value} and {max_value}.")
                continue
            return value
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter an integer.")


def get_valid_float(prompt, min_value, max_value):
    """Ask the user for a float between min_value and max_value (inclusive)."""

    while True:
        try:
            value = float(input(Fore.GREEN + prompt))
            if value < min_value or value > max_value:
                print(f"{Fore.WHITE}Please enter a number between {min_value} and {max_value}.")
                continue
            return value
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a number.")


# ------------------ menu helpers ------------------

def show_menu():
    """Display the main menu, prompt the user for a choice,
    and return the selected option as an integer."""

    print("\n" + Fore.CYAN + "-" * 40 + "\n")
    print(Fore.CYAN + "*" * 10 + " My Movies Database " + "*" * 10 + "\n")
    print(Fore.CYAN + "0. Exit")
    print(Fore.CYAN + "1. List movies")
    print(Fore.CYAN + "2. Add movie")
    print(Fore.CYAN + "3. Delete movie")
    print(Fore.CYAN + "4. Update movie")
    print(Fore.CYAN + "5. Stats")
    print(Fore.CYAN + "6. Random movie")
    print(Fore.CYAN + "7. Search movie")
    print(Fore.CYAN + "8. Movies sorted by rating")
    print(Fore.CYAN + "9. Generate website")
    print()
    return get_valid_int(
        f"Enter choice ({MIN_MENU_CHOICE}–{MAX_MENU_CHOICE}): ",
        MIN_MENU_CHOICE,
        MAX_MENU_CHOICE
    )


def handle_choice(choice):
    """Run the appropriate function based on the user's menu selection."""

    actions = {
        0: exit_program,
        1: list_movies,
        2: add_movie,
        3: delete_movie,
        4: update_movie,
        5: stats,
        6: random_movie,
        7: search_movie,
        8: sort_by_rating,
        9: generate_website,
    }

    func = actions.get(choice)
    if func:
        func()
    else:
        print(Fore.RED + "Invalid choice ❌")
    print()


def press_enter_to_continue():
    """Wait for the user to press Enter to continue."""

    print("[Press Enter to return to the menu]", end="", flush=True)
    input()  # just to fix a bug with Enter not working properly


def select_user():
    """
    Let the user select an existing profile or create a new one.
    Sets global active_user_id and active_user_name.
    """
    global active_user_id, active_user_name

    while True:
        users = movie_storage.list_users()

        if not users:
            print(Fore.CYAN + "No users found. Let's create your profile.\n")
            name = get_nonempty_string("Enter user name: ")
            user_id = movie_storage.create_user(name)
            active_user_id = user_id
            active_user_name = name
            print(f"\nWelcome, {name}! 🎬\n")
            return

        print(Fore.CYAN + "\n🎬 Select a user profile:\n")
        for idx, (uid, name) in enumerate(users, start=1):
            print(Fore.YELLOW + f"{idx}. {name}")
        print(Fore.YELLOW + f"{len(users) + 1}. Create new user")

        choice = get_valid_int(
            f"Enter choice (1-{len(users) + 1}): ",
            1,
            len(users) + 1
        )

        if choice == len(users) + 1:
            # Create new user
            name = get_nonempty_string("Enter new user name: ")
            user_id = movie_storage.create_user(name)
            active_user_id = user_id
            active_user_name = name
            print(Fore.MAGENTA + f"\nWelcome, {name}! 🎬\n")
            return
        else:
            # Existing user
            uid, name = users[choice - 1]
            active_user_id = uid
            active_user_name = name
            print(Fore.MAGENTA + f"\nWelcome back, {name}! 🎬\n")
            return

# ------------------ movie functions ------------------

def exit_program():
    """Exit the program after printing a farewell message."""

    print(Fore.WHITE + "\nBye! 👋")
    sys.exit()


def list_movies():
    """Display all movies in the database, showing each title,
    release year, and rating."""

    movies = movie_storage.list_movies(active_user_id)
    if not movies:
        print(Fore.RED + "No movies in the database yet.\n")
        return
    print(f"\n{Fore.WHITE}{len(movies)} movies in total")
    print('\n' + Fore.WHITE + '-' * 30 + '\n')
    for movie, info in movies.items():
        year = info["year"]
        rating = info["rating"]
        print(f"{Fore.BLUE}{movie} ({year}): {Fore.YELLOW}{rating}")
    print()


def add_movie():
    """
    Add a new movie using the OMDb API.
    The user only enters the title; year, rating and poster URL are fetched.
    """
    movies = movie_storage.list_movies(active_user_id)
    title = get_nonempty_string("\nEnter movie title: ")

    if title in movies:
        print(Fore.RED + f"\nMovie '{title}' is already in the database.\n")
        return

    # Try to fetch from API
    try:
        data = movie_api.fetch_movie(title)
    except movie_api.MovieAPIError as e:
        print(Fore.RED + f"\nCould not reach OMDb API. Please try again later.\nDetails: {e}\n")
        return

    # Movie not found
    if data is None:
        print(Fore.RED + f"\nMovie '{title}' was not found in OMDb.\n")
        return

    # Use the “official” title from API (correct casing)
    api_title = data.get("Title", title)

    # Year (string in API)
    year_str = data.get("Year", "")
    try:
        year = int(year_str)
    except ValueError:
        year = get_valid_int(
            f"Could not read year from API. Enter the year ({MIN_YEAR}–{MAX_YEAR}): ",
            MIN_YEAR,
            MAX_YEAR
        )

    # IMDB rating
    rating_str = data.get("imdbRating", "N/A")
    if rating_str == "N/A":
        rating = get_valid_float(
            f"Could not read rating from API. Enter movie rating ({MIN_RATING}–{MAX_RATING}): ",
            MIN_RATING,
            MAX_RATING
        )
    else:
        try:
            rating = float(rating_str)
        except ValueError:
            rating = get_valid_float(
                f"API rating invalid. Enter movie rating ({MIN_RATING}–{MAX_RATING}): ",
                MIN_RATING,
                MAX_RATING
            )

    # Poster URL
    poster_url = data.get("Poster")
    if not poster_url or poster_url == "N/A":
        poster_url = None  # we can still store movie without poster

    # Save to database (note: add_movie now accepts poster=None by default)
    movie_storage.add_movie(active_user_id, api_title, year, round(rating, 1), poster_url)
    print(Fore.MAGENTA + f"\nMovie '{api_title}' added successfully from OMDb 🎉\n")


def delete_movie():
    """Delete an existing movie by title, giving the user a chance to retry if not found."""

    movies = movie_storage.list_movies(active_user_id)
    if not movies:
        print(Fore.RED + "No movies in the database yet.\n")
        return

    while True:
        title = get_nonempty_string("\nEnter movie title to delete (or 'q' to cancel): ").strip()
        if title.lower() == "q":
            print(Fore.YELLOW + "Cancelled.\n")
            break
        if title in movies:
            movie_storage.delete_movie(active_user_id, title)
            print(Fore.MAGENTA + f"\nMovie '{title}' deleted ✅\n")
            break
        print(Fore.RED + f"\nMovie '{title}' not found 👀")


def update_movie():
    """
    Update the note of an existing movie by prompting the user
    for its title and a new note.
    """
    movies = movie_storage.list_movies(active_user_id)
    if not movies:
        print(Fore.RED + "No movies in the database yet.\n")
        return

    while True:
        title = get_nonempty_string("\nEnter movie title to update (or 'q' to cancel): ").strip()
        if title.lower() == "q":
            print(Fore.YELLOW + "Cancelled.\n")
            break

        if title in movies:
            note = get_nonempty_string("Enter movie note: ")
            rows = movie_storage.update_movie(active_user_id, title, note)

            if rows > 0:
                print(Fore.MAGENTA + f"\nMovie '{title}' successfully updated with a note 📝\n")
            else:
                print(Fore.RED + f"\nMovie '{title}' could not be updated.\n")
            break

        print(Fore.RED + f"\nMovie '{title}' not found ❌")


def stats():
    """Calculate and display movie statistics."""
    movies = movie_storage.list_movies(active_user_id)
    if not movies:
        print(Fore.RED + "No movies in the database yet.\n")
        return

    ratings = [info["rating"] for info in movies.values()]

    average = statistics.mean(ratings)
    median = statistics.median(ratings)
    max_rating = max(ratings)
    min_rating = min(ratings)

    best_movies = [movie for movie, info in movies.items() if info["rating"] == max_rating]
    worst_movies = [movie for movie, info in movies.items() if info["rating"] == min_rating]

    print(f"\n📊 {Fore.YELLOW}Average rating: {average:.1f}")
    print(f"📈 {Fore.YELLOW}Median rating: {median:.1f}")
    print(f"🌟 {Fore.YELLOW}Best movie(s): {', '.join(best_movies)} ({max_rating})")
    print(f"💩 {Fore.YELLOW}Worst movie(s): {', '.join(worst_movies)} ({min_rating})")
    print()


def random_movie():
    """Select and display a random movie from the database,
    along with its rating."""

    movies = movie_storage.list_movies(active_user_id)
    if not movies:
        print(Fore.RED + "No movies in the database yet.\n")
        return
    movie, info = random.choice(list(movies.items()))
    print(f"\n{Fore.MAGENTA}Your movie for tonight is: {movie} 🍿 (rated {info['rating']})\n")


def search_movie():
    """Search for a movie by title or partial match.
    If not found, suggest similar titles using fuzzy matching."""

    movies = movie_storage.list_movies(active_user_id)
    if not movies:
        print(Fore.RED + "No movies in the database yet.\n")
        return

    query = get_nonempty_string("\nEnter a part of the movie title: ")
    # check normal substring search first
    matches = [movie for movie in movies.keys() if query.lower() in movie.lower()]
    if matches:
        for movie in matches:
            print(f"{Fore.BLUE}{movie}: {Fore.YELLOW}{movies[movie]['rating']}")
    else:
        # if nothing found, try fuzzy match
        close_matches = difflib.get_close_matches(query, movies.keys(), n=5, cutoff=0.4)
        if close_matches:
            print(f'{Fore.YELLOW}The movie "{query}" does not exist. Did you mean:')
            for movie in close_matches:
                print(f"- {Fore.BLUE}{movie}")
        else:
            print(f'\n{Fore.RED}No matches found for "{query}".')
    print()


def sort_by_rating():
    """Display all movies sorted by rating in descending order,
    showing their title, release year, and rating."""

    movies = movie_storage.list_movies(active_user_id)
    if not movies:
        print(Fore.RED + "No movies in the database yet.")
        return

    sorted_movies = sorted(
        movies.items(),
        key=lambda item: item[1]["rating"],
        reverse=True
    )
    print(f"\n{Fore.WHITE}{len(movies)} movies sorted by rating in descending order:")
    print("\n" + Fore.WHITE + "-" * 30 + "\n")
    for movie, info in sorted_movies:
        print(f"{Fore.BLUE}{movie} ({info['year']}): {Fore.YELLOW}{info['rating']}")
    print()


def _generate_movie_grid_html(movies):
    """
    Build the HTML for all movies to insert into __TEMPLATE_MOVIE_GRID__.
    `movies` is the dict returned by movie_storage.list_movies(active_user_id).
    """
    items = []

    for title, info in movies.items():
        year = info["year"]
        rating = info["rating"]
        poster_url = info.get("poster") or ""
        note = info.get("note") or ""

        # If note exists, use it as a tooltip (title attribute) on the poster
        title_attr = f' title="{note}"' if note else ""

        item_html = f"""
        <li>
            <div class="movie">
                <img class="movie-poster" src="{poster_url}" alt="Poster for {title}"{title_attr}>
                <div class="movie-title">{title}</div>
                <div class="movie-year">{year}</div>
                <div class="movie-year">Rating: {rating}</div>
            </div>
        </li>
        """
        items.append(item_html)

    return "\n".join(items)


def generate_website():
    """
    Generate the HTML website from the template and save it as
    _static/<username>.html for the currently active user.
    """
    # Get movies for the active user only
    movies = movie_storage.list_movies(active_user_id)

    # 1. Read the template file
    try:
        with open("_static/index_template.html", "r", encoding="utf-8") as f:
            template = f.read()
    except FileNotFoundError:
        print("\nTemplate file not found. Make sure _static/index_template.html exists.\n")
        return

    # 2. Generate the movie grid HTML
    movie_grid_html = _generate_movie_grid_html(movies)

    # 3. Replace placeholders
    html_content = (
        template
        .replace("__TEMPLATE_TITLE__", "My Movie App")
        .replace("__TEMPLATE_MOVIE_GRID__", movie_grid_html)
    )

    # 4. Build a per-user output filename, e.g. _static/John.html
    safe_name = active_user_name.strip() or "index"
    safe_name = safe_name.replace(" ", "_")
    output_path = f"_static/{safe_name}.html"

    # 5. Write the final HTML file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(Fore.MAGENTA + f"\nWebsite for {active_user_name} was generated successfully! 🚀")
    print(Fore.CYAN + f"Saved to: {output_path}\n")


# ------------------ main ------------------

def main():
    """Run the main loop of the Movies Database application:
    select user, then display the menu, process choices, and manage movie data."""

    print(Fore.CYAN + "🎬 Welcome to My Movies Database!")
    select_user()

    while True:
        print(Fore.GREEN + f"\n👤 Current user: {active_user_name}")
        choice = show_menu()
        handle_choice(choice)
        press_enter_to_continue()


if __name__ == "__main__":
    main()
