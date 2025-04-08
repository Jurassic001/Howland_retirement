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

# Color constants
RED = "\033[0;31m"
BOLDRED = "\033[1;31m"
GREEN = "\033[0;32m"
LIGHTGREEN = "\033[2;32m"
YELLOW = "\033[0;33m"
CYAN = "\033[0;36m"
NC = "\033[0m"


def string_comp(movie_title_one: str, movie_title_two: str) -> float:
    """Compares two titles using the Damerau-Levenshtein distance algorithm and returns a similarity score.
    The Damerau-Levenshtein distance measures the minimum number of operations (insertions, deletions, substitutions,
    and transpositions of adjacent characters) required to transform one string into the other. This function calculates
    the distance and converts it into a similarity score between 0 and 1, where 1 indicates identical titles and 0 indicates
    completely dissimilar titles.

    Args:
        movie_title_one (str): The first title to compare.
        movie_title_two (str): The second title to compare.
    Returns:
        float: A similarity score between 0 and 1, where higher values indicate more similar titles.
    """
    # print(f'Comparing "{movie_title_one}" to "{movie_title_two}"...')
    m1_len = len(movie_title_one)
    m2_len = len(movie_title_two)

    # Initialize the Damerau-Levenshtein matrix with dimensions (howl_title_length + 1) x (tmdb_title_length + 1)
    DamLev_matrix = [[0 for _ in range(m2_len + 1)] for _ in range(m1_len + 1)]

    # Fill the first column with incremental values (base case for deletions)
    for i in range(m1_len + 1):
        DamLev_matrix[i][0] = i

    # Fill the first row with incremental values (base case for insertions)
    for j in range(m2_len + 1):
        DamLev_matrix[0][j] = j

    # Compute the Damerau-Levenshtein distance
    for i in range(1, m1_len + 1):
        for j in range(1, m2_len + 1):
            # Determine the cost of substitution (0 if characters match, 1 otherwise)
            cost = 0 if movie_title_one[i - 1] == movie_title_two[j - 1] else 1

            # Calculate the minimum cost among deletion, insertion, and substitution
            DamLev_matrix[i][j] = min(
                DamLev_matrix[i - 1][j] + 1,  # Deletion
                DamLev_matrix[i][j - 1] + 1,  # Insertion
                DamLev_matrix[i - 1][j - 1] + cost,  # Substitution
            )

            # Check for transposition (swapping of adjacent characters) and update the cost if applicable
            if i > 1 and j > 1 and movie_title_one[i - 1] == movie_title_two[j - 2] and movie_title_one[i - 2] == movie_title_two[j - 1]:
                DamLev_matrix[i][j] = min(DamLev_matrix[i][j], DamLev_matrix[i - 2][j - 2] + cost)  # Transposition

    # The edit distance is the number of characters that need to be changed to make the two titles identical
    edit_distance = DamLev_matrix[m1_len][m2_len]

    # Calculate a similarity percentage, where a higher value indicates more similar titles
    return 1 - (edit_distance / max(m1_len, m2_len))


def get_best_result(results: list[dict], title: str) -> dict:
    """Finds the best matching result from a list of movie results sourced from TMDB's API, based on title similarity and vote count.
    Attempts to handle known edge cases where possible, preferring to discard results instead of potentially contaminating the data.

    Args:
        results (list[dict]): A list of movies returned from TMDB's API. Each movie is represented as a dictionary containing various attributes.
        title (str): The title of the movie to match against the results.
    Returns:
        dict: The dictionary representing the best matching movie result. If no suitable match is found, an empty dictionary is returned.
    """
    highest_similarity_score: float = 0.0
    best_result: dict = {}

    for result in results:
        # loop through the results and check for the best match

        if result.get("vote_count", 0) == 0:
            # Disregard movies with no votes
            continue

        tmdb_title: str = result["title"]
        if tmdb_title.lower() == title.lower():
            # If the result title is an exact match, return the result
            print(f'{CYAN}Found "{tmdb_title}" for "{title}" as an exact match ({time.time() - START_TIME:.2f}s){NC}')
            return result
        else:
            # If the API-sourced movie title is not an exact match, calculate similarity between the two
            similarity_score = string_comp(tmdb_title, title)

            if similarity_score > highest_similarity_score:
                print(f'{CYAN}Found "{tmdb_title}" for "{title}" with a similarity score of {similarity_score:.2f} ({time.time() - START_TIME:.2f}s){NC}')
                # The movie with the highest similarity score is set as the best result
                highest_similarity_score = similarity_score
                best_result = result
            continue

    if highest_similarity_score < 0.3 and best_result:
        # if the similarity score is too low, check if Mr. Howland wrote the title in shorthand and the official title is much longer
        # this is the case for a movie like "Shang-Chi" which is officially titled "Shang-Chi and the Legend of the Ten Rings"
        shorthand_check = title in best_result["title"]
        print(
            f'{CYAN}Low similarity score of {highest_similarity_score:.2f} with "{best_result["title"]}" for "{title}" triggered shorthand title check ({"passed" if shorthand_check else "failed"}) ({time.time() - START_TIME:.2f}s){NC}'
        )
        if not shorthand_check:
            return {}  # if the shorthand check fails, discard the result

    return best_result


def get_tmdb_rating(title, notes):
    """Get the rating & TMDB ID of a movie from The Movie Database API.
    If a release date is included in Mr. Howland's notes, incorporate that into the query.

    If the movie couldn't be found, return None for both the rating and ID.
    """
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
    response = requests.get(url, headers=headers)

    data: dict[str, list[dict]] = response.json()
    if data.get("results"):
        # verify that results for our query exist, and find the best result
        if best_result := get_best_result(data["results"], title):
            return best_result["vote_average"], best_result["id"]
        else:
            # no best result failure case
            print(f'{YELLOW}Could not find qualified entry for "{title}", skipping... ({time.time() - START_TIME:.2f}s){NC}')
            return None, None
    else:
        # no results failure case
        print(f'{YELLOW}Found no results for "{title}", skipping... ({time.time() - START_TIME:.2f}s){NC}')
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
