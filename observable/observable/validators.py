import os
from functools import partial

from aiohttp import ClientSession

from observable.utils import check_connection

MAX_FILES_COUNT = 20_000


def directory_valid(path: str) -> bool:
    if not os.path.isdir(path):
        return False
    files_count = 0
    for _, _, files in os.walk(path):
        files_count += len(files)
        if files_count > MAX_FILES_COUNT:
            return False
    return True


async def subscriber_valid(subscriber: str,
                           *,
                           session: ClientSession) -> bool:
    try:
        check_connection(subscriber,
                         method=partial(ClientSession.post,
                                        json={}),
                         session=session)
        return True
    except ConnectionError:
        return False
