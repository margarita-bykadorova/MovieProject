# My Movie App

A console-based movie management application with user profiles, SQL storage, OMDb API integration, and static website generation.

## Features

- **User Profiles**: Each user has their own separate movie collection.
- **SQLite Storage** (via SQLAlchemy).
- **Add Movies Automatically** using OMDb API (title, year, rating, poster).
- **Notes on Movies** displayed as hover tooltips on website posters.
- **Generate a Static Website** for each user.
- **Search, Sort, Delete, Random movie selection**, and more.
- Clean project structure with dedicated storage package and data directory.

## Project Structure

```
.
├── data/
│   └── movies.db
├── storage/
│   └── movie_storage_sql.py
├── _static/
│   ├── index_template.html
│   ├── style.css
│   └── <user>.html (generated websites)
├── movies.py
├── README.md
└── requirements.txt
```

## Installation

1. Clone the repository:
```
git clone <your-repo-url>
```

2. Install dependencies:
```
pip install -r requirements.txt
```

## Usage

Run the main app:

```
python movies.py
```

### On Startup
You will be prompted to **select or create a user**.  
Each user's movies are stored separately.

### Commands
Inside the app, you can:

- Add movies (auto-fetched from OMDb by title)
- Delete movies
- Update movie notes
- List or search your movies
- Sort movies by rating
- Generate a personalized website

### Generate Website

Choose option **9** in the app to create a static HTML website.  
The file is saved as:

```
_static/<username>.html
```

Open it in your browser to view your movie collection.

## Requirements

See `requirements.txt`  
Contains:
```
SQLAlchemy>=2.0
requests>=2.0
colorama>=0.4
```

## OMDb API Key

You must create a free OMDb API key:  
https://www.omdbapi.com/

Place your key inside `movie_api.py`.

## License

This project is for educational purposes.

## 💡 Author

Created by **[margarita-bykadorova](https://github.com/margarita-bykadorova)**  
