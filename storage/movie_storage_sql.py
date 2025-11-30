# movie_storage_sql.py

from sqlalchemy import create_engine, text

# Define the database URL
DB_URL = "sqlite:///data/movies.db"

# Create the engine (echo=True so we see the SQL in the console)
engine = create_engine(DB_URL, echo=True)

# Create the table if it does not exist
with engine.connect() as connection:
    # Create users table
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """))

    # Create movies table with a foreign key to users
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            poster TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE (user_id, title)
        )
    """))

    connection.commit()


def list_users():
    """Return a list of all users as rows (id, name)."""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT id, name FROM users"))
        return result.fetchall()


def create_user(name):
    """Create a new user. Return the ID of the created user."""
    with engine.connect() as connection:
        connection.execute(
            text("INSERT INTO users (name) VALUES (:name)"),
            {"name": name}
        )
        connection.commit()

        # return the new user's id
        result = connection.execute(
            text("SELECT id FROM users WHERE name = :name"),
            {"name": name}
        )
        return result.fetchone()[0]


def get_user_by_name(name):
    """Return user record (id, name) or None."""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT id, name FROM users WHERE name = :name"),
            {"name": name}
        ).fetchone()
        return result


def list_movies(user_id):
    """Return all movies for a specific user."""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT title, year, rating, poster FROM movies WHERE user_id = :uid"),
            {"uid": user_id}
        )
        rows = result.fetchall()

    return {
        row[0]: {"year": row[1], "rating": row[2], "poster": row[3]}
        for row in rows
    }


def add_movie(user_id, title, year, rating, poster=None):
    with engine.connect() as connection:
        connection.execute(
            text("""
                INSERT INTO movies (user_id, title, year, rating, poster)
                VALUES (:uid, :title, :year, :rating, :poster)
            """),
            {
                "uid": user_id,
                "title": title,
                "year": year,
                "rating": rating,
                "poster": poster
            }
        )
        connection.commit()


def delete_movie(user_id, title):
    with engine.connect() as connection:
        connection.execute(
            text("DELETE FROM movies WHERE user_id = :uid AND title = :title"),
            {"uid": user_id, "title": title}
        )
        connection.commit()


def update_movie(user_id, title, rating):
    with engine.connect() as connection:
        connection.execute(
            text("""
                UPDATE movies
                SET rating = :rating
                WHERE user_id = :uid AND title = :title
            """),
            {"uid": user_id, "title": title, "rating": rating}
        )
        connection.commit()
