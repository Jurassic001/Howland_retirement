import csv
import os
import re
import time

import requests
from bs4 import BeautifulSoup

START_TIME = time.time()  # Track program time cuz I'm curious
URL = "https://sites.google.com/hpisd.org/howlandsmoviereviews/home?pli=1"  # URL for Mr. Howland's movie review website
DATAPATH = "data\\howland_ratings.csv"  # Path to save the CSV file to

# I promise colors are absolutely necessary for this, no I am not addicted to coloring strings
RED: str = "\033[0;31m"
BOLDRED: str = "\033[1;31m"
GREEN: str = "\033[0;32m"
LIGHTGREEN: str = "\033[2;32m"
YELLOW: str = "\033[0;33m"
CYAN: str = "\033[0;36m"
NC: str = "\033[0m"


def main():
    print(f"{CYAN}Fetching review website... ({time.time() - START_TIME:.2f}s)")
    response = requests.get(URL)
    print(f"Website fetched ({time.time() - START_TIME:.2f}s)")
    parsable = BeautifulSoup(response.text, "html.parser")
    reviews = parsable.select("li.zfr3Q")
    print(f"Review HTML parsed ({time.time() - START_TIME:.2f}s){NC}", end="\n\n")

    print(f"{GREEN}Parsing & writing data to CSV file... ({time.time() - START_TIME:.2f}s){NC}", end="\n\n")
    with open(DATAPATH, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, delimiter=",")
        writer.writerow(["Name", "Rating", "Notes"])
        review_count = len(reviews)
        for i, review in enumerate(reviews):
            # Process each review and setup some default vals
            text = review.get_text(strip=True)
            text = text.rstrip(",").strip()
            rating, notes = "", ""

            # Check & log progress at each 10% interval
            if i % (review_count // 10) == 0:
                print(f"{LIGHTGREEN}{i}/{review_count} reviews parsed & written ({time.time() - START_TIME:.2f}s){NC}")

            # Check for content in parentheses, which we call notes
            """notes_match Regex breakdown:
            . is the wildcard character, so it'll match anything
            * will match any amount of the preceding character (in this case, the wildcard character)
            We use backslashes to escape the parentheses as they are special characters (used for grouping in Regex)

            The end result is that the following Regex will match anything that is enclosed in parentheses"""
            notes_match = re.search(r"\(.*\)", text)
            if notes_match:
                notes = notes_match.group(0)
                # print(f"Notes found: {notes} ({time.time() - start_time:.2f}s)")
                """note-rating Regex breakdown:
                ^ asserts the start of the string, so we're parsing from the 0th index (using the match statement synergizes with this)
                again we use backslashes to escape parentheses so that they are part of the query as a literal and not a grouping operator
                backslash d will match any digit, 0-9
                + will match 1 or more instances of the preceding character, in this case we're looking for digits before the slash
                /10 is just a literal match, looking for out of 10
                $ asserts the end of the string, so we're parsing until the end of the string

                End result: we parse for reviews that follow the format of number/10 and are wrapped in parentheses, an edge case for Mr. H's website"""
                if re.match(r"^\(\d+/10\)$", notes):
                    # If a note contains a rating, convert the note to a rating
                    rating = notes.rstrip(")").lstrip("(")
                    notes = ""
                # this regex is pretty simple so I won't do a breakdown, we just replace anything in parentheses with an empty string
                # if Mr. H gets parentheses-happy, I might need to adjust this
                text = re.sub(r"\(.*\)", "", text).strip()

            # Check for a movie rating, unless one has been discovered in the notes
            if not rating:
                # The rating regexes are just less complicated versions of the note-rating regex so I won't do a breakdown :(
                # Identical, but without the parentheses and string start/end assertions
                rating_match = re.search(r"\d+/10", text)
                if rating_match:
                    rating = rating_match.group(0)
                    text = re.sub(r"\d+/10", "", text).strip()  # literally a dupe of the above regex, just a substitute instead of a search
                else:
                    print(f'\n{RED}Couldn\'t find rating in "{text}".  Attempting to account for formatting errors... ({time.time() - START_TIME:.2f}s){NC}')
                    # Regex so simple it barely deserves it's own comment, just looks for number/0 instead of number/10
                    bad_ten_match = re.search(r"\d+/0", text)
                    if bad_ten_match:
                        # a "bad ten" is a rating that is out of zero instead of ten on accident
                        rating = bad_ten_match.group(0)
                        print(f"{YELLOW}{rating} detected, correcting to {(rating := rating.replace("/0", "/10"))} ({time.time() - START_TIME:.2f}s){NC}", end="\n\n")
                        text = re.sub(r"\d+/0", "", text).strip()  # this one is so simple I'm going to link the Regex wikipedia page: https://en.wikipedia.org/wiki/Regular_expression
                    # more formatting errors can be addressed here if needed
                    else:
                        # Failsafe, honestly the program should just exit here because bad data is 100x worse than debugging
                        print(f"{BOLDRED}Couldn't find rating, skipping this entry ({time.time() - START_TIME:.2f}s){NC}")
                        continue

            # The rest of the text should be the movie name
            writer.writerow([text.strip(), rating, notes])
    print(f"\n{GREEN}Data saved successfully ({time.time() - START_TIME:.2f}s)")


if __name__ == "__main__":
    main()
    print(f"Opening CSV file... ({time.time() - START_TIME:.2f}s) {NC}")
    os.startfile(DATAPATH)
