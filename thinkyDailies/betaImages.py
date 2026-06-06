# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "aiohttp>=3.14.0",
# ]
# ///
import asyncio
import json
import platform
import random
from asyncio import sleep
from typing import List, Tuple, Optional

import aiohttp
from aiohttp import ClientSession

INFIXES: List[str] = [
    # base
    "",
    # known
    "-1", "-2", "a", "%20(1)", "%20(2)", "a%20(1)", "A",
    # extra just in case
    "-3", "b", "%20(3)", "b%20(1)", "a%20(2)", "B",
]


# Script to run on https://thinkygames.com/dailies/puzzles/1/ (and relative) to extract all the infixes:
# new Set([...document.querySelectorAll("div[class^=styles_preview] img")].map(e=>e.src).map(l=>l.replace('https://static.prod.thinkygames.com/uploads/puzzle_intro_images/','').replace(/\.png$/,'').replace(/600x600$/,'').replace(/^\dx\d\d/,'')))


def main() -> None:
    """Main."""

    print("Building entries")
    entries = build_entries()
    valid_entries = asyncio.run(filter_entries(entries))

    print("Statistics:")
    for infix in INFIXES:
        print(f"Infix '{infix}' has {sum(infix == i for _s, _p, i, _u in valid_entries)} elements")

    print("Writing to file")
    images = {}
    for season, puzzle, _, url in valid_entries:
        images.setdefault(season, {}).setdefault(puzzle, []).append(url)
    with open("betaImages.json", 'r+') as output:
        data = json.load(output)
        data['images'] = images
        output.seek(0)
        json.dump(data, output, indent=2)

    print("done")


def build_entries() -> List[Tuple[int, int, str, str]]:
    """Builds all possible entries (a bit of a brute-force approach)"""
    data: List[Tuple[int, int, str, str]] = []

    for season in [1, 2, 3]:
        for puzzle in range(1, 61 + 1):
            for infix in INFIXES:
                data.append((season, puzzle, infix,
                             f"https://static.prod.thinkygames.com/uploads/puzzle_intro_images/{season}x{puzzle:02}{infix}-600x600.png"))
    return data


async def filter_entries(entries: List[Tuple[int, int, str, str]]) -> List[Tuple[int, int, str, str]]:
    """Removes invalid entries (where the url doesn't exist)."""
    async with aiohttp.ClientSession() as session:
        filtered = await asyncio.gather(*(keep_if_exists(entry, session) for entry in entries))
    return [entry for entry in filtered if entry is not None]


async def keep_if_exists(entry: Tuple[int, int, str, str], session: ClientSession) -> Optional[
    Tuple[int, int, str, str]]:
    """Returns the entry if it exists (based on a HEAD request), None if not."""
    exc = None
    for retry in range(1, 10 + 1):
        try:
            await sleep(random.random() * retry)
            async with session.head(url=entry[3]) as response:
                ok = response.ok
                print("OK" if ok else "ko", entry[3])
                return entry if ok else None
        except Exception as e:
            exc = e
            await sleep(random.randint(1, retry))
    raise exc


if __name__ == '__main__':

    # https://stackoverflow.com/a/70758881
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    main()
