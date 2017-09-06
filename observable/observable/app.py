import logging
from asyncio import AbstractEventLoop
from functools import partial
from typing import (Dict,
                    Set)

from aiohttp import ClientSession
from aiohttp.web import Application

from observable.config import PACKAGE_NAME
from .handlers import subscribe
from .middlewares import middleware_factory

logger = logging.getLogger(PACKAGE_NAME)


def create_app(loop: AbstractEventLoop,
               subscriptions: Dict[str, Set[str]],
               session: ClientSession) -> Application:
    app = Application(logger=logger,
                      loop=loop,
                      middlewares=[middleware_factory])
    subscribe_handler = partial(subscribe,
                                subscriptions=subscriptions,
                                session=session)
    app.router.add_post('/subscribe', subscribe_handler)
    return app
