import logging
from typing import (Union,
                    Iterable,
                    Dict)

from aiohttp import ClientSession

from observable.types import StatesDiffType

logger = logging.getLogger(__name__)


async def run(*,
              subscribers: Iterable[str],
              message: Dict[str, Union[str, StatesDiffType]],
              session: ClientSession):
    for subscriber in subscribers:
        try:
            await session.post(subscriber,
                               json=message)
        except Exception:
            logger.exception('')
            continue
