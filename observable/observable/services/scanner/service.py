from asyncio import (AbstractEventLoop,
                     Future,
                     sleep,
                     ensure_future)
from datetime import datetime
from functools import partial
from typing import (Callable,
                    Coroutine,
                    Iterator,
                    Dict,
                    Set,
                    Tuple)

from aiohttp import ClientSession

from observable.services import notifier
from observable.types import StatesDiffType
from .utils import (files_paths,
                    file_size,
                    states_diff_stream)


async def halt_client(delay: int,
                      client: str,
                      last_calls: Dict[str, datetime]) -> None:
    try:
        last_call = last_calls[client]
    except KeyError:
        last_call = datetime.utcnow()

    current_time = datetime.utcnow()
    seconds_since_last_call = (current_time - last_call).total_seconds()
    await sleep(delay - seconds_since_last_call)
    last_calls[client] = current_time


async def run_periodically(subscriptions: Dict[str, Set[str]],
                           *,
                           name: str,
                           delay: int,
                           session: ClientSession,
                           loop: AbstractEventLoop) -> None:
    states = {}
    last_calls = {}
    update = partial(update_states,
                     states=states)
    halt = partial(halt_client,
                   delay=delay,
                   last_calls=last_calls)
    while True:
        for directory_path, subscribers in subscriptions.items():
            future = ensure_future(update(directory_path),
                                   loop=loop)
            stopper = partial(halt_client,
                              delay=delay,
                              client=directory_path,
                              last_calls=last_calls)
            future.add_done_callback(partial(notify,
                                             name=name,
                                             subscribers=subscribers,
                                             stopper=stopper,
                                             session=session,
                                             loop=loop))
        await halt(client=None)


def notify(done_future: Future,
           name: str,
           subscribers: Set[str],
           stopper: Callable[[], Coroutine],
           session: ClientSession,
           loop: AbstractEventLoop) -> None:
    diff = done_future.result()
    if not diff:
        return
    message = {'diff': diff,
               'source': name}
    loop.run_until_complete(notifier.run(subscribers=subscribers,
                                         message=message,
                                         session=session))
    loop.run_until_complete(stopper())


async def update_states(directory_path: str,
                        *,
                        states: dict) -> StatesDiffType:
    try:
        old_state = states[directory_path]
    except KeyError:
        old_state = {}
    new_state = dict(state_stream(directory_path))
    states[directory_path] = new_state
    return dict(states_diff_stream(old_state,
                                   new_state))


def state_stream(directory_path: str) -> Iterator[Tuple[str, int]]:
    for path in files_paths(directory_path):
        yield path, file_size(path)
