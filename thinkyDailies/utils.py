import random
from asyncio import sleep
from itertools import groupby
from typing import Iterable, Tuple, Callable, TypeVar, Awaitable

from aiohttp import ClientSession, ClientResponse

SEASONS = range(1, 4 + 1)
PUZZLES = range(1, 61 + 1)


def group_by[K, V](elements: Iterable[Tuple[K, V]]) -> list[Tuple[
    K, list[V]]]:
    """( (k1, v11), (k1, v12), (k2, v2) ) --> [ (k1, [v11, v12]), (k2, [v2]) ]"""
    return [
        (key, [element[1] for element in grouped_elements])
        for key, grouped_elements in groupby(elements, key=lambda x: x[0])
    ]


T = TypeVar('T')


async def network_request(method: str, url: str, session: ClientSession,
                          mapper: Callable[[ClientResponse], Awaitable[T]]) -> T:
    """
    Performs a network request with random delay and automatic retry if response fails.
    yields the response, mapped by the async mapper.
    Throws exception after several retries.
    """
    exc = None
    for retry in range(1, 10 + 1):
        try:
            await sleep(random.random() * retry)
            async with session.request(method=method, url=url, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:155.0) Gecko/20100101 Firefox/155.0"}) as response:
                print("OK" if response.ok else "ko", url)
                return await mapper(response)
        except Exception as e:
            exc = e
            await sleep(random.randint(1, retry))
    raise exc
