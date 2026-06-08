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
from typing import List, Optional, Union, Iterable, NamedTuple

import aiohttp
from aiohttp import ClientSession


class Entry(NamedTuple):
    season: int
    puzzle: int
    prefix: str
    suffix: str


class Result(NamedTuple):
    season: str
    puzzle: str
    infix: str
    url: str


InfixNode = Union[str, List["InfixNode"]]

# If str, no more elements in the list will be checked.
INFIXES: List[InfixNode] = [
    [""],  # sometimes this may not exist, we allow failing
    ["-1", "-2", "-3"],
    ["%20(1)", "%20(2)", "%20(3)"],
    ["a", ["a%20(1)", "a%20(2)"], ["b", ["b%20(1)"], "c"]],
    ["A", "B"],
]


# Script to run on https://thinkygames.com/dailies/puzzles/1/ (and relative) to extract all the infixes:
# new Set([...document.querySelectorAll("div[class^=styles_preview] img")].map(e=>e.src).map(l=>l.replace('https://static.prod.thinkygames.com/uploads/puzzle_intro_images/','').replace(/\.png$/,'').replace(/600x600$/,'').replace(/^\dx\d\d/,'')))


def main() -> None:
    """Main."""

    print("Building entries")
    entries: List[Entry] = []
    for season in [1, 2, 3]:
        for puzzle in range(1, 61 + 1):
            entries.append(Entry(season,
                                 puzzle,
                                 f"https://static.prod.thinkygames.com/uploads/puzzle_intro_images/{season}x{puzzle:02}",
                                 "-600x600.png"))

    print("Requesting")
    results = asyncio.run(parse_entries(entries))

    print("Statistics:")

    def flatten(xs):
        for x in xs:
            if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
                yield from flatten(x)
            else:
                yield x

    for infix in flatten(INFIXES):
        print(f"Infix '{infix}' has {sum(infix == result.infix for result in results)} elements")

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
    return await parse_infix(INFIXES, entry, session)


async def parse_infix(infix: List[InfixNode], entry: Entry, session: ClientSession) -> List[Result]:
    """Parses an entry with a list of infixes."""
    results: List[Result] = []
    for infx in infix:
        if isinstance(infx, str):
            # single value
            result = await keep_if_exists(
                Result(
                    season=str(entry.season),
                    puzzle=str(entry.puzzle),
                    infix=infx,
                    url=entry.prefix + infx + entry.suffix,
                ),
                session,
            )
            if result is not None:
                results.append(result)
            else:
                # if a value fails, stop evaluating
                break
        else:
            # list, continue regardless
            results.extend(await parse_infix(infx, entry, session))
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
