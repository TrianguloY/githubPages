# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "aiohttp>=3.14.0",
# ]
# ///
import asyncio
import json

import aiohttp
from aiohttp import ClientSession


# Script to run on https://thinkygames.com/dailies/puzzles/1/ (and relative) to extract all the infixes:
# new Set([...document.querySelectorAll("div[class^=styles_preview] img")].map(e=>e.src).map(l=>l.replace('https://static.prod.thinkygames.com/uploads/puzzle_intro_images/','').replace(/\.png$/,'').replace(/600x600$/,'').replace(/^\dx\d\d/,'')))


def main() -> None:
    """Main."""

    # build and filter entries
    entries = build_entries()
    valid_entries = asyncio.run(filter_entries(entries))

    # write as json
    data = {}
    for season, puzzle, url in valid_entries:
        data.setdefault(season, {}).setdefault(puzzle, []).append(url)
    with open("betaImages.json", 'w') as output:
        json.dump(data, output, indent=2)


def build_entries() -> list[tuple[int, int, str]]:
    """Builds all possible entries (a bit of a brute-force approach)"""
    data: list[tuple[int, int, str]] = []

    for season in [1, 2, 3]:
        for puzzle in range(1, 61 + 1):
            for infix in ["", "-1", "-2", "a", "%20(1)", "%20(2)", "a%20(1)", "A"]:
                data.append((season, puzzle,
                             f"https://static.prod.thinkygames.com/uploads/puzzle_intro_images/{season}x{puzzle:02}{infix}-600x600.png"))
    return data


async def filter_entries(entries: list[tuple[int, int, str]]) -> list[tuple[int, int, str]]:
    """Removes invalid entries (where the url doesn't exist)."""
    async with aiohttp.ClientSession() as session:
        filtered = await asyncio.gather(*(keep_if_exists(entry, session) for entry in entries))
    return [entry for entry in filtered if entry is not None]


async def keep_if_exists(entry: tuple[int, int, str], session: ClientSession):
    """Returns the entry if it exists (based on a HEAD request), None if not."""
    async with session.head(url=entry[2]) as response:
        return entry if response.ok else None


if __name__ == '__main__':
    main()
