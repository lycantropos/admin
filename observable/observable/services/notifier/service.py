import logging
from typing import Iterable

from aiohttp import ClientSession

from observable.types import DiffType

logger = logging.getLogger(__name__)


async def run(*,
              subscribers: Iterable[str],
              json_data: DiffType,
              session: ClientSession):
    for subscriber in subscribers:
        try:
            await session.post(subscriber,
                               json=json_data)
        except Exception:
            logger.exception('')
            continue
