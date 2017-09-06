import logging
import traceback
from typing import (Callable,
                    Coroutine)

from aiohttp.web import (Application,
                         Request,
                         Response)

from observable.utils import bad_request_json

HandlerType = Callable[[Request], Coroutine]


async def middleware_factory(app: Application,
                             handler: HandlerType) -> HandlerType:
    async def middleware_handler(request: Request) -> Response:
        try:
            return await handler(request)
        except Exception:
            logging.exception('')
            err_msg = traceback.format_exc()
            body = {'status': 'error',
                    'reason': err_msg}
            return bad_request_json(body=body)

    return middleware_handler
