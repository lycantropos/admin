import json
import logging
from functools import partial
from typing import (Dict,
                    Set)
import os
from aiohttp import ClientSession
from aiohttp.web_exceptions import HTTPBadRequest
from aiohttp.web_request import Request
from aiohttp.web_response import (Response,
                                  json_response)

from observable.utils import check_connection


async def subscribe(request: Request,
                    subscriptions: Dict[str, Set[str]],
                    session: ClientSession) -> Response:
    subscription = request.query
    try:
        directory_path = os.path.abspath(subscription['directory'])
        subscriber = subscription['subscriber']
    except KeyError:
        body = {'status': 'error',
                'reason': 'Invalid subscription: '
                          'query should contain '
                          'both keys "directory", '
                          '"subscriber".'}
        return HTTPBadRequest(body=json.dumps(body),
                              content_type='application/json')

    subscriber_is_valid = await subscriber_valid(subscriber,
                                                 session=session)
    if not subscriber_is_valid:
        body = {'status': 'error',
                'reason': 'Invalid subscriber: '
                          'failed to send request '
                          f'at "{subscriber}".'}
        return HTTPBadRequest(body=json.dumps(body),
                              content_type='application/json')

    try:
        subscribers = subscriptions[directory_path]
    except KeyError:
        subscriptions[directory_path] = {subscriber}
    else:
        if subscriber in subscribers:
            body = {'status': 'error',
                    'reason': 'Invalid subscription: already subscribed.'}
            return HTTPBadRequest(body=json.dumps(body),
                                  content_type='application/json')
        subscribers.add(subscriber)

    logging.info('Successfully added subscription '
                 f'to directory "{directory_path}" '
                 f'for subscriber "{subscriber}".')

    return json_response({'status': 'ok'})


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
