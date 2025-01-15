# Howland_retirement
Solving the mystery put forth by my AP Macroeconomics teacher, Mr. Howland
<br/>

## Given Information
**Retirement Poster Mystery:** Why does he call the poster by his desk his "retirement poster".

**Clue 1:** The name of the piece.

**Clue 2:** He got the idea from watching a Humphrey Bogart movie that is **not** Casablanca.

**Prize:** Avengers Poster or Plaque with your name on it. (We want the plaque, obviously.)

## Repository Contents
- `data`: Contains data tables relating to the mystery
    - [`howland_ratings.csv`](data/howland_ratings.csv): Formatted data of each movie rating posted to [Mr.Howland's website](https://sites.google.com/hpisd.org/howlandsmoviereviews/home?pli=1)
    - [`hb_movies.csv`](data/hb_movies.csv): Formatted data of each movie that Humphrey Bogart has appeared in. Scraped from [Wikipedia](https://en.wikipedia.org/wiki/Humphrey_Bogart_on_stage,_screen,_radio_and_television#List_of_feature_films) using [WikiTable2CSV](https://github.com/gambolputty/wikitable2csv). Scraped data needs some manual editing to make it RBQL/SQL-friendly
    - [`data_analysis`](data/data_analysis.md): Analysis & comparisons of the data tables
- `poster`: Contains high-rez image of the poster, a short written analysis, and any other poster-related files
    - [`poster.jpg`](poster/poster.jpg): Image of the poster
    - [`poster_analysis.md`](poster/poster_analysis.md): Written analysis of the poster
- `scripts`: Contains scripts used for repository setup and data gathering/analysis
    - [`get_ratings.py`](scripts/get_ratings.py): Python script to scrape and organize movie ratings from Mr.Howland's website
    - [`install_reqs.py`](scripts/install_reqs.py): Simple helper script for installing required packages and setting up git hooks. Standard practice for my repos
    - [`tmdb_ratings.py`](scripts/tmdb_ratings.py): Python script to fetch movie ratings, official name, and other useful tidbits from [The Movie Database API](https://developer.themoviedb.org/docs/getting-started)
