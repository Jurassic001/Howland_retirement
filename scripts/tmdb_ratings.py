import argparse
import csv
import json
import re
import sys
import time

import requests

START_TIME = time.time()
H_RANKS = "data\\howland_ratings.csv"
POP_RANKS = "data\\popular_ratings.csv"

# Color constants
RED = "\033[0;31m"
BOLDRED = "\033[1;31m"
GREEN = "\033[0;32m"
LIGHTGREEN = "\033[2;32m"
YELLOW = "\033[0;33m"
CYAN = "\033[0;36m"
NC = "\033[0m"


def get_tmdb_rating(title, notes):
    """Get the rating & official name of a movie from The Movie Database API.
    If a release date is included in Mr. Howland's notes, incorporate that into the query"""

    # Build the API query from the movie title
    url = f"https://api.themoviedb.org/3/search/movie?query={title}&include_adult=false&language=en-US"
    """release_year regex breakdown:
    We use backslashes to escape the parentheses
    backslash d will match any digit, 0-9
    {4} Will match four of the preceding token (digits in this case)

    The end result is that the following Regex will match a four-digit number enclosed in parentheses,
    which is used to denote a release year in the notes"""
    release_year = re.search(r"\(\d{4}\)", notes)
    if release_year:
        url += f"&primary_release_year={release_year.group()}"
    url += "&page=1"

    # relevant TMDB reference: https://developer.themoviedb.org/reference/search-movie
    headers = {"accept": "application/json", "Authorization": f"Bearer {tmdb_read_access_token}"}
    # JSONify the response and extract the rating, official name, and ID
    response = requests.get(url, headers=headers)
    data = response.json()
    if data.get("results"):
        return data["results"][0].get("vote_average"), data["results"][0].get("id")
    return None, None


def main():
    with open(H_RANKS, "r", encoding="utf-8") as howland_ratings:
        # Get the table of Howland's ratings from his website
        reader = csv.reader(howland_ratings)
        next(reader)  # Skip the header row
        rows = list(reader)
        total_movies = len(rows)
        failed_fetches = 0
        failure_limit = total_movies // 10

        with open(POP_RANKS, "w", newline="", encoding="utf-8") as popular_ratings:
            writer = csv.writer(popular_ratings)
            writer.writerow(["Name", "Rating", "TMDB ID"])

            for i, row in enumerate(rows):
                # grab the name/notes from Howland's ratings and get the popular rating and movie ID from TMDB
                movie_name = row[0]
                notes = row[2] if len(row) > 2 else ""
                rating, id = get_tmdb_rating(movie_name, notes)

                if rating is not None:
                    # Write the name, rating, and the ID of the movie on TMDB
                    writer.writerow([movie_name, rating, id])
                else:
                    print(f'{YELLOW}Could not retrieve rating for "{movie_name}", skipping...{NC}')
                    failed_fetches += 1
                    if failed_fetches >= failure_limit:
                        # if we've failed to fetch more than 10% of the movies, exit
                        print(f"{RED}Exceeded failure limit with {failed_fetches} failures out of {total_movies} movies, exiting...{NC}")
                        sys.exit(1)

                if i % (total_movies // 10) == 0:
                    # status update every 10% of the way through
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
