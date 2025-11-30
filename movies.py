"""
Movies Database Application

A console-based Python program that allows users to manage a personal movie collection.
Users can list, add, delete, update, and search for movies, view statistics, or generate
a rating histogram saved as an image file. The data is stored in memory while the
program is running, and all user interactions are handled through a simple text menu.
"""

import sys
import statistics
import random
import difflib
import matplotlib.pyplot as plt
from colorama import Fore, init
import movie_storage
init(autoreset=True)

MIN_YEAR = 1900
MAX_YEAR = 2025
MIN_RATING = 0
MAX_RATING = 10
MIN_MENU_CHOICE = 0
MAX_MENU_CHOICE = 11


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


def get_optional_number(prompt, cast_type):
    """Ask the user for a number or allow them to leave it blank."""

    while True:
        value = input(Fore.GREEN + prompt).strip()
        if value == "":
            return None  # user skipped the filter
        try:
            return cast_type(value)  # convert to int or float depending on the case
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a valid number or leave blank.")


# ------------------ menu helpers ------------------

def show_menu():
    """Display the main menu, prompt the user for a choice,
    and return the selected option as an integer."""

    print("\n"+ Fore.CYAN + "-" * 40 + "\n")
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
    print(Fore.CYAN + "9. Movies sorted by release year")
    print(Fore.CYAN + "10. Filter movies")
    print(Fore.CYAN + "11. Create Rating Histogram")
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
        9: sort_by_release,
        10: filter_movies,
        11: create_rating_histogram
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


# ------------------ movie functions ------------------

def exit_program():
    """Exit the program after printing a farewell message."""

    print(Fore.WHITE + "\nBye! 👋")
    sys.exit()


def list_movies():
    """Display all movies in the database, showing each title,
    release year, and rating."""

    movies = movie_storage.get_movies()
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
    """Prompt the user for a new movie's title, release year, and rating.
    Add new movie to the database if it doesn't already exist."""

    movies = movie_storage.get_movies()
    title = get_nonempty_string("\nEnter new movie title: ")

    if title in movies:
        print(Fore.RED + f"\nMovie '{title}' is already in the database.\n")
        return

    year = get_valid_int(
        f"Enter the year of release ({MIN_YEAR}–{MAX_YEAR}): ",
        MIN_YEAR,
        MAX_YEAR
    )
    rating = get_valid_float(
        f"Enter movie rating ({MIN_RATING}–{MAX_RATING}): ",
        MIN_RATING,
        MAX_RATING
    )
    movie_storage.add_movie(title, year, round(rating, 1))
    print(Fore.MAGENTA + f"\nMovie '{title}' added successfully 🎉\n")


def delete_movie():
    """Delete an existing movie by title, giving the user a chance to retry if not found."""

    movies = movie_storage.get_movies()
    if not movies:
        print(Fore.RED + "No movies in the database yet.\n")
        return

    while True:
        title = get_nonempty_string("\nEnter movie title to delete (or 'q' to cancel): ").strip()
        if title.lower() == "q":
            print(Fore.YELLOW + "Cancelled.\n")
            break
        if title in movies:
            movie_storage.delete_movie(title)
            print(Fore.MAGENTA + f"\nMovie '{title}' deleted ✅\n")
            break
        print(Fore.RED + f"\nMovie '{title}' not found 👀")


def update_movie():
    """Update the rating of an existing movie
    by prompting the user for its title and a new rating."""

    movies = movie_storage.get_movies()
    if not movies:
        print(Fore.RED + "No movies in the database yet.\n")
        return

    while True:
        title = get_nonempty_string("\nEnter movie title to update (or 'q' to cancel): ").strip()
        if title.lower() == "q":
            print(Fore.YELLOW + "Cancelled.\n")
            break
        if title in movies:
            rating = get_valid_float(
                f"Enter new rating ({MIN_RATING}–{MAX_RATING}): ",
                MIN_RATING,
                MAX_RATING
            )
            movie_storage.update_movie(title, round(rating, 1))
            print(Fore.MAGENTA + f"\nMovie '{title}' updated successfully 🎉\n")
            break
        print(Fore.RED + f"\nMovie '{title}' not found ❌")


def stats():
    """Calculate and display movie statistics including the average,
    median, highest, and lowest ratings. Also list the best and worst
    movies based on their ratings."""

    movies = movie_storage.get_movies()
    if not movies:
        print(Fore.RED + "No movies in the database yet.\n")
        return

    ratings = []
    for info in movies.values():
        ratings.append(info["rating"])

    average = statistics.mean(ratings)
    median = statistics.median(ratings)
    max_rating = max(ratings)
    min_rating = min(ratings)

    best_movies = []
    for movie, info in movies.items():
        if info["rating"] == max_rating:
            best_movies.append(movie)

    worst_movies = []
    for movie, info in movies.items():
        if info["rating"] == min_rating:
            worst_movies.append(movie)

    print(f"\n📊 {Fore.YELLOW}Average rating: {average:.1f}")
    print(f"📈 {Fore.YELLOW}Median rating: {median:.1f}")
    print(f"🌟 {Fore.YELLOW}Best movie(s): {', '.join(best_movies)} ({max_rating})")
    print(f"💩 {Fore.YELLOW}Worst movie(s): {', '.join(worst_movies)} ({min_rating})")
    print()


def random_movie():
    """Select and display a random movie from the database,
    along with its rating."""

    movies = movie_storage.get_movies()
    if not movies:
        print(Fore.RED + "No movies in the database yet.\n")
        return
    movie, info = random.choice(list(movies.items()))
    print(f"\n{Fore.MAGENTA}Your movie for tonight is: {movie} 🍿 (rated {info['rating']})\n")


def search_movie():
    """Search for a movie by title or partial match.
    If not found, suggest similar titles using fuzzy matching."""

    movies = movie_storage.get_movies()
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

    movies = movie_storage.get_movies()
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


def sort_by_release():
    """Display all movies sorted by release year,
    optionally showing the newest movies first or last.
    Each entry includes the title, release year, and rating."""

    movies = movie_storage.get_movies()
    if not movies:
        print(Fore.RED + "No movies in the database yet.")
        return

    sort_order = get_nonempty_string("\nDo you want the latest movies first? (Y/N): ").lower()
    while sort_order not in ("y", "n"):
        sort_order = get_nonempty_string("Please enter either 'y' or 'n': ").strip().lower()

    sort = sort_order == "y"
    print(f"\n{Fore.WHITE}{len(movies)} movies listed in chronological order:")
    print('\n' + Fore.WHITE + '-' * 30 + '\n')
    for movie, info in sorted(movies.items(), key=lambda item: item[1]["year"], reverse=sort):
        print(f"{Fore.BLUE}{movie} ({info['year']}): {Fore.YELLOW}{info['rating']}")


def filter_movies():
    """Display movies filtered by rating and year of release based on user request."""

    movies = movie_storage.get_movies()
    if not movies:
        print(Fore.RED + "No movies in the database yet.")
        return

    min_rating = get_optional_number("\nEnter min rating (leave blank for no min rating): ", float)
    start_year = get_optional_number("Enter start year (leave blank for no start year): ", int)
    end_year = get_optional_number("Enter end year (leave blank for no end year): ", int)

    matches = []
    for movie, info in movies.items():
        matches_rating = min_rating is None or info["rating"] >= min_rating
        matches_start = start_year is None or info["year"] >= start_year
        matches_end = end_year is None or info["year"] <= end_year
        if matches_rating and matches_start and matches_end:
            matches.append((movie, info))

    if matches:
        print(f"\n{Fore.WHITE}{len(matches)} movies were found:")
        print('\n' + Fore.WHITE + '-' * 30 + '\n')
        for movie, info in matches:
            print(f"{Fore.BLUE}{movie} ({info['year']}): {Fore.YELLOW}{info['rating']}")
    else:
        print(Fore.RED + "\nNo movies matching the given criteria were found.")


def create_rating_histogram():
    """Create a histogram showing the distribution of movie ratings.
    Prompt the user for a filename and save the plot as an image file."""

    movies = movie_storage.get_movies()
    if not movies:
        print(Fore.RED + "No movies in the database yet.\n")
        return

    ratings = []
    for info in movies.values():
        ratings.append(info["rating"])

    filename = get_nonempty_string("\nEnter filename to save the histogram (e.g., hist.png): ")
    if not filename.lower().endswith(".png"):
        filename += ".png"

    plt.hist(ratings, bins=20, edgecolor="black")
    plt.xlabel("Rating")
    plt.ylabel("Number of Movies")
    plt.title("Movie Ratings Histogram")
    plt.savefig(filename)
    plt.close()
    print(f"\n{Fore.MAGENTA}Histogram saved to {filename} 🎉\n")


# ------------------ main ------------------

def main():
    """Run the main loop of the Movies Database application:
    display the menu, process user choices, and manage movie data."""

    print("🎬 Welcome to My Movies Database!")
    while True:
        choice = show_menu()
        handle_choice(choice)
        press_enter_to_continue()


if __name__ == "__main__":
    main()
