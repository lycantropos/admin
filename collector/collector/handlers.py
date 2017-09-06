import json
import logging

from aiohttp.web_exceptions import HTTPBadRequest
from aiohttp.web_request import Request
from aiohttp.web_response import (Response,
                                  json_response)


async def collect(request: Request) -> Response:
    request_json = await request.json()
    logging.info(request_json)

    if not request_json:
        body = {'status': 'error',
                'reason': 'invalid JSON.'}
        return HTTPBadRequest(body=json.dumps(body),
                              content_type='application/json')

    return json_response({'status': 'OK'})
