import logging
import traceback
from typing import (Callable,
                    Coroutine)

from aiohttp.web import (Application,
                         Request,
                         Response)
from aiohttp.web_exceptions import HTTPBadRequest

HandlerType = Callable[[Request], Coroutine]


async def middleware_factory(app: Application,
                             handler: HandlerType) -> HandlerType:
    async def middleware_handler(request: Request) -> Response:
        try:
            return await handler(request)
        except Exception:
            logging.exception('')
            err_msg = traceback.format_exc()
            return HTTPBadRequest(body=err_msg)

    return middleware_handler
