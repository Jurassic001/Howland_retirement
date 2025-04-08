import argparse
import csv
import json
import re
import sys
import time

import requests

START_TIME = time.time()
H_RANKS = "data/howland_ratings.csv"
POP_RANKS = "data/popular_ratings.csv"
COMP_RANKS = "data/compared_ratings.csv"

# Color constants
RED = "\033[0;31m"
BOLDRED = "\033[1;31m"
GREEN = "\033[0;32m"
LIGHTGREEN = "\033[2;32m"
YELLOW = "\033[0;33m"
CYAN = "\033[0;36m"
NC = "\033[0m"


def get_howland_ratings() -> dict[str, int]:
    howland_ratings = {}
    with open(H_RANKS, "r", encoding="utf-8") as howland_ratings_file:
        reader = csv.reader(howland_ratings_file)
        next(reader)  # Skip header row
        for row in reader:
            name, rating, _ = row
            # replace the /10 at the end of the rating with nothing and convert to an int
            rating = int(re.sub("/10", "", rating))
            howland_ratings[name] = rating
    print(f"{CYAN}Successfully retrieved Howland's ratings{NC}")
    return howland_ratings


def get_popular_ratings() -> dict[str, tuple[float, int]]:
    popular_ratings = {}
    with open(POP_RANKS, "r", encoding="utf-8") as popular_ratings_file:
        reader = csv.reader(popular_ratings_file)
        next(reader)  # Skip header row
        for row in reader:
            name, rating, tmdb_id = row
            rating = float(rating)
            popular_ratings[name] = (rating, int(tmdb_id))
    print(f"{CYAN}Successfully retrieved popular movie ratings{NC}")
    return popular_ratings


def query_movie_title_and_name(tmdb_id: int) -> tuple[str, list[str]]:
    # relevant TMDB reference: https://developer.themoviedb.org/reference/movie-details
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?language=en-US"
    headers = {"accept": "application/json", "Authorization": f"Bearer {tmdb_read_access_token}"}
    # JSONify the response and extract the movie title and genres
    response = requests.get(url, headers=headers)
    data: dict = response.json()
    if data.get("title") is None:
        # We grab the movie title from TMDB because some movies are named incorrectly in Mr. Howland's reviews
        print(f"{RED}Movie title could not be found{NC}")
        print(f"{YELLOW}Response: {data}{NC}")
        sys.exit(1)
    return data["title"], [genre["name"] for genre in data["genres"]]


def main():
    h_ranks = get_howland_ratings()
    p_ranks = get_popular_ratings()
    total_movies = len(p_ranks)

    with open(COMP_RANKS, "w", newline="", encoding="utf-8") as compared_ratings:
        writer = csv.writer(compared_ratings)
        writer.writerow(["Title", "Popular Rating", "Howland Rating", "Genres"])  # write the header row

        for i, (name, (pop_rating, tmdb_id)) in enumerate(p_ranks.items()):
            if (howland_rating := h_ranks.get(name)) is None:
                print(f"{RED}No rating found for {name} in Howland's ratings{NC}")
                sys.exit(1)

            title, genres = query_movie_title_and_name(tmdb_id)
            writer.writerow([title, pop_rating, howland_rating, "; ".join(genres)])

            if i % (total_movies // 10) == 0:
                print(f"{LIGHTGREEN}Processed {i}/{total_movies} movies ({time.time() - START_TIME:.2f}s){NC}")

    print(f"{GREEN}Completed processing all movies ({time.time() - START_TIME:.2f}s){NC}")
    sys.exit(0)


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Fetch movie ratings from The Movie Database API")
    parser.add_argument("--tmdb_token", type=str, help="API token for The Movie Database API")
    args = parser.parse_args()

    if args.tmdb_token:
        # If an API token is provided as a command line arg, use it. This is for CI
        tmdb_read_access_token = args.tmdb_token
    else:
        try:
            # Load API key from JSON file if not provided as an argument
            with open("scripts/config.json", "r") as config:
                tmdb_read_access_token = json.load(config)["tmdb_token"]
        except (FileNotFoundError, KeyError):
            print(f"{RED}API key not provided and config.json file not found or invalid{NC}")
            sys.exit(1)

    main()
