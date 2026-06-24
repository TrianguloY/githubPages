#!/usr/bin/env -S uv run --script
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
from typing import List, Optional, Union, NamedTuple, Any, Callable, Generator

import aiohttp
from aiohttp import ClientSession


# Infixes

def infix_numeric() -> Generator[str, Any, None]:
    for i in range(1, 100):
        yield f"-{i}"


def infix_windows() -> Generator[str, Any, None]:
    for i in range(1, 100):
        yield f"%20({i})"


def infix_lower() -> Generator[str, Any, None]:
    for l in "abcdefghijklmnopqrstuvwxyz":
        yield l


def infix_upper() -> Generator[str, Any, None]:
    for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        yield l


InfixGenerator = Union[Callable[[], Generator[str, Any, None]]]
INFIXES: List[InfixGenerator] = [infix_numeric, infix_windows, infix_lower, infix_upper]


# Script you can run on https://thinkygames.com/dailies/puzzles/1/ (and relative) to extract all the infixes:
# new Set([...document.querySelectorAll("div[class^=styles_preview] img")].map(e=>e.src).map(l=>l.replace('https://static.prod.thinkygames.com/uploads/puzzle_intro_images/','').replace(/\.png$/,'').replace(/600x600$/,'').replace(/^\dx\d\d/,'')))

# data classes

class Entry(NamedTuple):
    season: int
    puzzle: int
    prefix_left: str
    prefix_right: str
    suffix: str


class Result(NamedTuple):
    season: str
    puzzle: str
    infix: str
    url: str


# script

def main() -> None:
    """Main."""

    print("Building entries")
    entries: List[Entry] = []
    for season in [1, 2, 3]:
        for puzzle in range(1, 61 + 1):
            entries.append(Entry(season,
                                 puzzle,
                                 f"https://static.prod.thinkygames.com/uploads/puzzle_intro_images/{season}",
                                 f"{puzzle:02}",
                                 "-600x600.png"))

    print("Requesting")
    results = asyncio.run(parse_entries(entries))

    print("Statistics:")
    infixes_count = {}
    for result in results:
        infixes_count[result.infix] = infixes_count[result.infix] + 1 if result.infix in infixes_count else 1
    for infix, count in infixes_count.items():
        print(f"Infix '{infix}' has {count} elements")

    print("Writing to file")
    images = {}
    for result in results:
        images.setdefault(result.season, {}).setdefault(result.puzzle, []).append(result.url)
    with open("betaImages.json") as file:
        data = json.load(file)
    data['images'] = images
    with open("betaImages.json", 'w') as file:
        json.dump(data, file, indent=2)

    print("done")


async def parse_entries(entries: List[Entry]) -> List[Result]:
    """Removes invalid entries (where the url doesn't exist)."""
    async with aiohttp.ClientSession() as session:
        filtered = await asyncio.gather(*(parse_entry(entry, session) for entry in entries))
    return [entry for result in filtered for entry in result]


async def parse_entry(entry: Entry, session: ClientSession) -> List[Result]:
    """Parses an entry with all infixes."""
    return (
        await parse_infix("", "x", INFIXES, entry, session)
    ) + (
        await parse_infix("", "X", INFIXES, entry, session)
    )


async def parse_infix(current_infix: str, prefix_infix: str, infix_generators: List[InfixGenerator], entry: Entry,
                      session: ClientSession) -> List[Result]:
    """Parses an entry with a list of infix generators."""
    # TODO: try to find a generic url-generation to avoid the ugly prefix_infix
    # check value
    result = await keep_if_exists(
        Result(
            season=str(entry.season),
            puzzle=str(entry.puzzle),
            infix=prefix_infix + "/" + current_infix,
            url=entry.prefix_left + prefix_infix + entry.prefix_right + current_infix + entry.suffix,
        ),
        session,
    )
    if result is None and current_infix != "":
        # value doesn't exist, stop
        # note: some variants exist even if the base url does not, so we continue in that case
        return []

    # url exists, lets try the generators
    results: List[Result] = [result] if result else []
    for generator in infix_generators:
        for infix in generator():
            partial = await parse_infix(current_infix + infix, prefix_infix, infix_generators, entry, session)
            if not partial:
                break
            results.extend(partial)
    return results


async def keep_if_exists(result: Result, session: ClientSession) -> Optional[Result]:
    """Returns the entry if it exists (based on a HEAD request), None if not. Retries on network error"""
    exc = None
    for retry in range(1, 10 + 1):
        try:
            await sleep(random.random() * retry)
            async with session.head(url=result.url) as response:
                ok = response.ok
                print("OK" if ok else "ko", result.url)
                return result if ok else None
        except Exception as e:
            exc = e
            await sleep(random.randint(1, retry))
    raise exc


if __name__ == '__main__':

    # https://stackoverflow.com/a/70758881
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    main()
