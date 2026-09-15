#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#    "beautifulsoup4>=4.15.0",
#    "requests>=2.34.2",
# ]
# ///
import json
from Tools.scripts.summarize_stats import load_raw_data

import requests
from bs4 import BeautifulSoup
from utils import SEASONS, PUZZLES


def main() -> None:
    """Main."""
    data = {}

    for season in SEASONS:
        data[season] = {}
        for puzzle in PUZZLES:

            try:
                data[season][puzzle] = get_puzzle_data(season, puzzle)
            except Exception as e:
                print("Error on parsing", season, puzzle)
                data[season][puzzle] = None

    # save
    with open("story.json", "w") as output:
        json.dump(data, output, indent=2)


def get_html(url: str) -> BeautifulSoup:
    """Returns the html of a url."""
    return BeautifulSoup(
        requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:155.0) Gecko/20100101 Firefox/155.0"}
        ).text,
        features="html.parser"
    )


def get_puzzle_data(season: str, puzzle: str) -> dict[str, str]:
    """Returns the data of a specific puzzle."""
    print("loading", season, puzzle)

    # load html
    html = get_html(f"https://thinkygames.com/dailies/puzzles/{season}-{puzzle}/")

    # extract data
    raw = [
        x.text.removeprefix("self.__next_f.push(").removesuffix(')')
        for x in html.find_all("script")
        if x.text.startswith('self.__next_f.push([1,"f:[\\"$\\",\\"$L1c\\",null,')
           and x.text.endswith(']\\n"])')
    ][0]
    property = json.loads(raw)
    parsed = json.loads(property[1].removeprefix('f:'))[3]

    try:
        title = parsed['title']
    except Exception as e:
        print("Error on", "title", season, puzzle)
        title = None

    try:
        introImage = parsed['introImage']['url']
    except Exception as e:
        print("Error on", "introImage", season, puzzle)
        introImage = None

    try:
        introText = "\n\n".join(
            subchildren['text'] for children in parsed['intro']['root']['children'] for subchildren in
            children['children'])
    except Exception as e:
        print("Error on", "introText", season, puzzle)
        introText = None

    try:
        winImage = parsed['winImage']['url'] if puzzle == 61 else None

    except Exception as e:
        print("Error on", "winImage", season, puzzle)
        winImage = None

    try:
        winText = "\n\n".join(
            subchildren['text'] for children in parsed['winMessage']['root']['children'] for subchildren in
            children['children'])
    except Exception as e:
        print("Error on", "winText", season, puzzle)
        winText = None

    return {
        'title': title,
        'introImage': introImage,
        'introText': introText,
        'winImage': winImage,
        'winText': winText,
    }


if __name__ == '__main__':
    create_data()
