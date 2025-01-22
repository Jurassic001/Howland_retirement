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
    - [`popular_ratings.csv`](data/popular_ratings.csv): Formatted data of each movie that Mr. Howland has rated, sourced from [The Movie Database](https://www.themoviedb.org/?language=en-US)'s API. Includes the "popular" rating (aka the rating given to the movie by TMDB users) and the movie's ID in the database for future reference
    - [`compared_ratings.csv`](data/compared_ratings.csv): Combined data of each movie that Mr. Howland has rated w/ the popular rating from TMDB included. Also features genres and official title (all sourced from TMDB)
    - [`hb_movies.csv`](data/hb_movies.csv): Formatted data of each movie that Humphrey Bogart has appeared in. Scraped from [Wikipedia](https://en.wikipedia.org/wiki/Humphrey_Bogart_on_stage,_screen,_radio_and_television#List_of_feature_films) using [WikiTable2CSV](https://github.com/gambolputty/wikitable2csv). Scraped data needs some manual editing to make it RBQL/SQL-friendly
    - [`data_analysis`](data/data_analysis.md): Analysis & comparisons of the data tables
- `poster`: Contains high-rez image of the poster, a short written analysis, and any other poster-related files
    - [`poster.jpg`](poster/poster.jpg): Image of the poster
    - [`poster_analysis.md`](poster/poster_analysis.md): Written analysis of the poster
- `scripts`: Contains scripts used for repository setup and data gathering/analysis
    - [`install_reqs.py`](scripts/install_reqs.py): Simple helper script for installing required packages and setting up git hooks. Standard practice for my repos
    - [`get_ratings.py`](scripts/get_ratings.py): Python script to scrape and organize movie ratings from Mr.Howland's website
    - [`tmdb_ratings.py`](scripts/tmdb_ratings.py): Python script to fetch movie ratings, official name, and other useful tidbits from [The Movie Database API](https://developer.themoviedb.org/docs/getting-started)
    - [`compare_ratings.py`](scripts/compare_ratings.py): Python script to combine Mr. Howland's ratings with the popular ratings from TMDB, as well as source additional information like movie genre and official title
