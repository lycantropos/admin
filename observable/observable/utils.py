import json
import logging
from asyncio import sleep
from typing import (Type,
                    Callable,
                    Coroutine,
                    Dict,
                    Tuple)

from aiohttp import (ClientSession,
                     ClientConnectionError)
from aiohttp.web_exceptions import HTTPBadRequest


def bad_request_json(body: Dict[str, str]) -> HTTPBadRequest:
    return HTTPBadRequest(body=json.dumps(body),
                          content_type='application/json')


async def check_connection(
        url: str,
        *,
        retry_attempts: int = 10,
        retry_interval: int = 2,
        method: Callable[[ClientSession, str], Coroutine],
        exceptions: Tuple[Type[Exception], ...] = (ClientConnectionError,),
        session: ClientSession) -> None:
    logging.info('Establishing connection '
                 f'with "{url}".')
    for attempt_num in range(retry_attempts):
        try:
            await method(session, url)
            break
        except exceptions:
            err_msg = ('Connection attempt '
                       f'#{attempt_num + 1} failed.')
            logging.error(err_msg)
            await sleep(retry_interval)
    else:
        err_message = ('Failed to establish connection '
                       f'with "{url}" '
                       f'after {retry_attempts} attempts '
                       f'with {retry_interval} s. interval.')
        raise ConnectionError(err_message)
    logging.info(f'Connection established with "{url}".')
