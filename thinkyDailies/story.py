#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "beautifulsoup4>=4.15.0",
#     "requests>=2.34.2",
#     "aiohttp>=3.14.0",
# ]
# ///
import asyncio
import json
import platform
import random
from asyncio import sleep
from typing import Optional

import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup

from utils import SEASONS, PUZZLES, group_by, network_request


async def main() -> None:
    """Main."""

    # get data from urls
    async with aiohttp.ClientSession() as session:
        raw_puzzle_data = await asyncio.gather(
            *(get_puzzle_data(season, puzzle, session) for season in SEASONS for puzzle in PUZZLES))
    puzzle_data = [d for d in raw_puzzle_data if d is not None]

    # structure data
    tupled_data = [(season, (puzzle, data)) for season, puzzle, data in puzzle_data]
    data = {
        season: {
            puzzle: puzzle_data
            for puzzle, puzzle_data in season_tupled_data
        }
        for season, season_tupled_data in group_by(tupled_data)
    }

    # save
    with open("story.json", "w") as output:
        json.dump(data, output, indent=2)


async def get_puzzle_data(season: str, puzzle: str, session: ClientSession) -> tuple[str, str, dict[
    str, str | None]] | None:
    """Returns the data of a specific puzzle."""

    # load html
    async with network_request(
            "GET", f"https://thinkygames.com/dailies/puzzles/{season}-{puzzle}/", session) as response:
        if not response.ok: return None
        html = BeautifulSoup(await response.text(), features="html.parser")

    # extract data
    raw_script = [
        x.text.removeprefix("self.__next_f.push(").removesuffix(')')
        for x in html.find_all("script")
        if x.text.startswith('self.__next_f.push([1,"f:[\\"$\\",\\"$L1c\\",null,')
           and x.text.endswith(']\\n"])')
    ][0]
    raw_value = json.loads(raw_script)
    data = json.loads(raw_value[1].removeprefix('f:'))[3]

    # extract wanted fields
    try:
        title = data['title']
    except Exception as e:
        print("Error on", "title", season, puzzle, e)
        title = None

    try:
        introImage = data['introImage']['url']
    except Exception as e:
        print("Error on", "introImage", season, puzzle, e)
        introImage = None

    try:
        introText = "\n\n".join(
            subchildren['text'] for children in data['intro']['root']['children'] for subchildren in
            children['children'])
    except Exception as e:
        print("Error on", "introText", season, puzzle, e)
        introText = None

    try:
        winImage = data['winImage']['url'] if puzzle == 61 else None

    except Exception as e:
        print("Error on", "winImage", season, puzzle, e)
        winImage = None

    try:
        winText = "\n\n".join(
            subchildren['text'] for children in data['winMessage']['root']['children'] for subchildren in
            children['children'])
    except Exception as e:
        print("Error on", "winText", season, puzzle, e)
        winText = None

    # return
    return season, puzzle, {
        'title': title,
        'introImage': introImage,
        'introText': introText,
        'winImage': winImage,
        'winText': winText,
    }


async def get_html(url: str, session: ClientSession) -> Optional[BeautifulSoup]:
    """Returns the html of a url if it exists, None if not. Retries on network error"""
    async with network_request("GET", url, session) as response:
        return BeautifulSoup(await response.text(), features="html.parser") if response is not None else None


if __name__ == '__main__':

    # https://stackoverflow.com/a/70758881
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
