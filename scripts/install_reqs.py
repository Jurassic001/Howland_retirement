# region setup
# all package imports are part of the Python standard library
import argparse
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)))

# set up color codes
RED: str = "\033[0;31m"
BOLDRED: str = "\033[1;31m"
GREEN: str = "\033[0;32m"
BOLDGREEN: str = "\033[1;32m"
CYAN: str = "\033[0;36m"
NC: str = "\033[0m"  # No color


# set up method for formatting terminal output
def print_with_sidebars(text: str = "", color_code: str = NC) -> None:
    """Adds "sidebars" in the form of `=` to each side of a string and prints it

    Args:
        text (str, optional): The string blessed with "sidebars". Leaving this blank will print a full line of `=`
        color_code (str, optional): Escape code of a certain color to wrap the text in. Leaving this blank will not color the text
    """
    # Check to see if standard output is connected to a terminal. If yes get the terminal width, otherwise set a default value
    terminal_width = os.get_terminal_size().columns if os.isatty(sys.stdout.fileno()) else 80

    if not text:
        msg = "=" * terminal_width
    else:
        void_len = len(text) + 2  # Define the "void" area where the string will go
        sidebar_len = (terminal_width - void_len) // 2  # Define the length of a single sidebar
        sidebar = "=" * sidebar_len  # Make the sidebars
        msg = f"{sidebar} {color_code}{text}{NC} {sidebar}"
    print(msg)


# region main method
def main(directory: str, strict: bool, bypass_venv: bool) -> None:
    # define the parent directory path, which is used to represent the location of each requirements.txt file relative to the specified directory
    PARENT_PATH = Path(directory).resolve().parent

    # make sure pip and wheel are up-to-date
    print_with_sidebars("Pre-execution checks", CYAN)
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "wheel", "pip", "--upgrade"],
        check=True,
    )

    # check if we're outside a virtual environment and container and CI
    if (
        not bypass_venv
        and sys.base_prefix == sys.prefix  # no virtual environment
        and not os.path.exists("/.dockerenv")  # no container
        and os.getenv("CI") is None  # no github actions
        and os.getenv("BUILD_BUILDID") is None  # no azure pipelines
    ):
        print_with_sidebars("Not inside a docker container/virtual environment, exiting", RED)
        sys.exit(1)

    # Install requirements.txt recursively
    for filepath in Path(directory).glob("**/requirements*.txt"):
        # don't install any requirements.txt files that may be in the venv
        if ".venv" in str(filepath):
            continue

        local_path = f"{filepath.relative_to(PARENT_PATH)}"

        print_with_sidebars(local_path, CYAN)
        subprocess.run(
            [
                "pip",
                "install",
                "-r",
                str(filepath.absolute()),
            ],
            check=strict,
        )

    print_with_sidebars("Setting up git hooks", CYAN)
    # Setup pre-commit hooks
    subprocess.run(
        ["pre-commit", "install"],
        check=strict,
        cwd=PARENT_PATH,
    )
    print_with_sidebars("Requirement installation/setup successful", GREEN)
    sys.exit(0)


# region execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--directory",
        "-d",
        type=str,
        default=DEFAULT_DIR,
        help=f"Directory to walk recursively. Defaults to the parent directory ({DEFAULT_DIR})",
    )
    parser.add_argument(
        "--strict",
        "-s",
        action="store_true",
        default=False,
        help="Fail if ANY requirements could not installed",
    )
    parser.add_argument(
        "-B",
        "--bypass-venv",
        action="store_true",
        default=False,
        help=f"Bypass the virtual environment/docker container check",
    )

    args = parser.parse_args()
    args.directory = os.path.abspath(args.directory)

    main(args.directory, args.strict, args.bypass_venv)
