import json
from Tools.scripts.summarize_stats import load_raw_data

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:155.0) Gecko/20100101 Firefox/155.0"}


def get_puzzle_data(season, puzzle):
    print("loading", season, puzzle)
    html = BeautifulSoup(
        requests.get(f"https://thinkygames.com/dailies/puzzles/{season}-{puzzle}/", headers=HEADERS).text,
        features="html.parser")

    prefix = 'self.__next_f.push([1,"f:[\\"$\\",\\"$L1c\\",null,'
    suffix = ']\\n"])'
    raw = [
        x.text.removeprefix("self.__next_f.push(").removesuffix(')')
        for x in html.find_all("script")
        if x.text.startswith(prefix) and x.text.endswith(suffix)
    ][0]
    raw2 = json.loads(raw)
    parsed = json.loads(raw2[1].removeprefix('f:'))[3]

    try:
        title = parsed['title']
    except:
        print("Error on", "title", season, puzzle)
        title = None

    try:
        introImage = parsed['introImage']['url']
    except:
        print("Error on", "introImage", season, puzzle)
        introImage = None

    try:
        introText = "\n\n".join(
            subchildren['text'] for children in parsed['intro']['root']['children'] for subchildren in
            children['children'])
    except:
        print("Error on", "introText", season, puzzle)
        introText = None

    try:
        winImage = parsed['winImage']['url'] if puzzle == 61 else None

    except:
        print("Error on", "winImage", season, puzzle)
        winImage = None

    try:
        winText = "\n\n".join(
            subchildren['text'] for children in parsed['winMessage']['root']['children'] for subchildren in
            children['children'])
    except:
        print("Error on", "winText", season, puzzle)
        winText = None

    return {
        'title': title,
        'introImage': introImage,
        'introText': introText,
        'winImage': winImage,
        'winText': winText,
    }


def create_data():
    data = {}

    for s in range(1, 3 + 1):
        data[s] = {}
        for p in range(1, 61 + 1):

            try:
                data[s][p] = get_puzzle_data(s, p)
            except:
                print("Error on parsing", s, p)
                data[s][p] = None

    with open("story.json", "w") as output:
        json.dump(data, output, indent=2)


if __name__ == '__main__':
    create_data()
