from datetime import datetime

from pymongo.collection import Collection
from pymongo.cursor import Cursor


def date_time_to_timestamp(date_time: datetime) -> int:
    return int(date_time.timestamp())


def find(*,
         from_date_time: datetime,
         to_date_time: datetime,
         source: str,
         offset: int = None,
         limit: int = None,
         collection: Collection) -> Cursor:
    from_timestamp, to_timestamp = (date_time_to_timestamp(from_date_time),
                                    date_time_to_timestamp(to_date_time))
    where = {'$and': [{'source': source},
                      {'timestamp': {'$gte': from_timestamp}},
                      {'timestamp': {'$lte': to_timestamp}}]}
    return paginate(collection.find(where),
                    offset=offset,
                    limit=limit)


def paginate(cursor: Cursor,
             *,
             offset: int,
             limit: int) -> Cursor:
    if offset:
        cursor = cursor.skip(offset)
    if limit is not None:
        cursor = cursor.limit(limit)
    return cursor
