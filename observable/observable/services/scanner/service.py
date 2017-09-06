import os
from asyncio import sleep
from typing import (Iterable,
                    AsyncIterable,
                    Iterator,
                    Tuple)

from observable.types import DiffType
from .utils import (mappings_diff,
                    file_size)


async def run_periodically(directories_paths: Iterable[str],
                           *,
                           delay: int) -> AsyncIterable[Tuple[str, DiffType]]:
    states = {}
    while True:
        for directory_path in directories_paths:
            try:
                old_state = states[directory_path]
            except KeyError:
                old_state = {}
            new_state = dict(run(directory_path))
            diff = dict(mappings_diff(old_state,
                                      new_state))
            if not diff:
                continue
            yield directory_path, diff
            states[directory_path] = new_state
        await sleep(delay)


def run(directory_path: str) -> Iterator[Tuple[str, int]]:
    for root, _, files_names in os.walk(directory_path):
        for file_name in files_names:
            path = os.path.join(root, file_name)
            size = file_size(path)
            yield path, size
