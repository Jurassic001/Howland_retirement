import argparse
import csv
import time

import matplotlib.pyplot as plt
import numpy as np

START_TIME = time.time()
COMP_RANKS = "data/compared_ratings.csv"
GRAPH_OUTPUT = "data/compared_ratings.svg"

# Color constants
RED = "\033[0;31m"
BOLDRED = "\033[1;31m"
GREEN = "\033[0;32m"
LIGHTGREEN = "\033[2;32m"
YELLOW = "\033[0;33m"
CYAN = "\033[0;36m"
NC = "\033[0m"


def get_compared_ratings() -> list[tuple[str, int, int, list[str]]]:
    compared_ratings = []
    with open(COMP_RANKS, "r", encoding="utf-8") as compared_ratings_file:
        reader = csv.reader(compared_ratings_file)
        next(reader)  # Skip header row
        for row in reader:
            title, p_rat, h_rat, genres = row
            compared_ratings.append((title, float(p_rat), int(h_rat), [genre.strip() for genre in genres.split(";")]))
    print(f"{CYAN}Successfully retrieved compared ratings ({time.time() - START_TIME:.2f}s){NC}")
    return compared_ratings


def make_graph(compared_ratings):
    # Extract x axis (Howland's ratings) and y axis (popular ratings) values from the data
    x = [movie[2] for movie in compared_ratings]
    y = [movie[1] for movie in compared_ratings]

    # Create a scatter plot
    fig, ax = plt.subplots()
    scatter = ax.scatter(x, y)

    # Create an annotation object for displaying movie details on hover
    annot = ax.annotate("", xy=(0, 0), bbox=dict(boxstyle="round", fc="w"))
    annot.set_visible(False)

    # Function to update the annotation text and position
    def update_annot(ind):
        movie_index = ind["ind"][0]
        movie_name, pop_rat, howl_rat, genres = compared_ratings[movie_index]
        text = f"{movie_name}\nPopular rating: {pop_rat}\nHowland rating: {howl_rat}/10\nGenres: {', '.join(genres)}"
        annot.set_text(text)

    # Event handler for hover events
    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = scatter.contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    # Connect the hover event to the event handler
    fig.canvas.mpl_connect("motion_notify_event", hover)

    # Add a trendline to the scatter plot
    plt.plot(np.unique(x), np.poly1d(np.polyfit(x, y, 1))(np.unique(x)), color="red", linestyle="--", label="Trendline")

    # Add labels, title, and legend to the plot
    ax.legend()
    ax.set_xlabel("Howland rating")
    ax.set_ylabel("Popular rating")
    ax.set_title("Movie Ratings Comparison")

    # The X axis (Howland's ratings) seems to autoscale pretty well, so we just set the Y axis to be the same
    ax.set_ylim(ax.set_xlim())

    print(f"{CYAN}Successfully created graph ({time.time() - START_TIME:.2f}s){NC}")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Create a graph comparing movie ratings")
    parser.add_argument("--noshow", action="store_true", help="Prevent showing the graph after saving. Graph is only interactive when shown.")
    args = parser.parse_args()

    comp_ratings = get_compared_ratings()
    make_graph(comp_ratings)

    plt.savefig(GRAPH_OUTPUT, dpi=300, bbox_inches="tight")
    print(f"{GREEN}Graph saved to {GRAPH_OUTPUT} ({time.time() - START_TIME:.2f}s){NC}")
    if not args.noshow:
        plt.show()
