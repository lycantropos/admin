import logging
import os
from typing import (Dict,
                    Set)

from aiohttp import ClientSession
from aiohttp.web_request import Request
from aiohttp.web_response import (Response,
                                  json_response)

from observable.utils import bad_request_json
from observable.validators import (MAX_FILES_COUNT,
                                   subscriber_valid,
                                   directory_valid)


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
        return bad_request_json(body=body)

    subscriber_is_valid = await subscriber_valid(subscriber,
                                                 session=session)
    if not subscriber_is_valid:
        body = {'status': 'error',
                'reason': 'Invalid subscriber: '
                          'failed to send request '
                          f'at "{subscriber}".'}
        return bad_request_json(body=body)

    directory_is_valid = directory_valid(directory_path)

    if not directory_is_valid:
        body = {'status': 'error',
                'reason': 'Invalid directory path: '
                          f'"{directory_path}" should be '
                          f'reachable directory '
                          f'with less than {MAX_FILES_COUNT:_} files.'}
        return bad_request_json(body=body)

    try:
        subscribers = subscriptions[directory_path]
    except KeyError:
        subscriptions[directory_path] = {subscriber}
    else:
        if subscriber in subscribers:
            body = {'status': 'error',
                    'reason': 'Invalid subscription: already subscribed.'}
            return bad_request_json(body=body)
        subscribers.add(subscriber)

    logging.info('Successfully added subscription '
                 f'to directory "{directory_path}" '
                 f'for subscriber "{subscriber}".')

    return json_response({'status': 'ok'})
