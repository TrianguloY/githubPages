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

from utils import SEASONS, PUZZLES, group_by


async def main() -> None:
    """Main."""

    async with aiohttp.ClientSession() as session:
        raw_data = await asyncio.gather(
            *(get_puzzle_data(season, puzzle, session) for season in SEASONS for puzzle in PUZZLES))

    raw_data = [d for d in raw_data if d is not None]
    tupled_data = [(season, (puzzle, data)) for season, puzzle, data in raw_data]

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
    print("loading", season, puzzle)

    # load html
    html = await get_html(f"https://thinkygames.com/dailies/puzzles/{season}-{puzzle}/", session)

    if html is None: return None

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

    return season, puzzle, {
        'title': title,
        'introImage': introImage,
        'introText': introText,
        'winImage': winImage,
        'winText': winText,
    }


async def get_html(url: str, session: ClientSession) -> Optional[BeautifulSoup]:
    """Returns the html of a url if it exists, None if not. Retries on network error"""
    exc = None
    for retry in range(1, 10 + 1):
        try:
            await sleep(random.random() * retry)
            async with session.get(url=url, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:155.0) Gecko/20100101 Firefox/155.0"}) as response:
                ok = response.ok
                print("OK" if ok else "ko", url)
                return BeautifulSoup(await response.text(), features="html.parser") if ok else None
        except Exception as e:
            exc = e
            await sleep(random.randint(1, retry))
    raise exc


if __name__ == '__main__':

    # https://stackoverflow.com/a/70758881
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
