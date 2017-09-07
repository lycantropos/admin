from datetime import datetime

import pymongo
from aiohttp.web_request import Request
from aiohttp.web_response import (Response,
                                  json_response)

from collector.services.persistence import (find,
                                            save,
                                            documents)
from collector.utils import bad_request_json


async def collect(request: Request,
                  collection: pymongo.collection.Collection) -> Response:
    request_json = await request.json()

    document = documents.normalize(documents.escape_dots(request_json))
    save(document,
         collection=collection)

    if not request_json:
        body = {'status': 'error',
                'reason': 'invalid JSON.'}
        return bad_request_json(body=body)

    return json_response({'status': 'OK'})


def str_to_datetime(string: str,
                    format: str = '%Y-%m-%dT%H:%M:%S'):
    return datetime.strptime(string, format)


async def search(request: Request,
                 collection: pymongo.collection.Collection) -> Response:
    query = request.query

    from_date_time, to_date_time = (str_to_datetime(query['dateStart']),
                                    str_to_datetime(query['dateEnd']))
    offset = int(query.get('offset', 0))
    try:
        limit = int(query['limit'])
    except KeyError:
        limit = None
    cursor = find(source=query['source'],
                  from_date_time=from_date_time,
                  to_date_time=to_date_time,
                  limit=limit,
                  offset=offset,
                  collection=collection)
    count = cursor.count()
    data = list(map(documents.unescape_dots,
                    map(documents.to_serializable,
                        cursor)))
    return json_response({'data': data,
                          'offset': offset,
                          'count': count})
