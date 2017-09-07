import logging
from asyncio import AbstractEventLoop
from functools import partial

import pymongo
from aiohttp.web import Application

from .handlers import (collect,
                       search)
from .middlewares import middleware_factory

logger = logging.getLogger(__name__)


def create_app(*,
               collection: pymongo.collection.Collection,
               loop: AbstractEventLoop) -> Application:
    app = Application(logger=logger,
                      loop=loop,
                      middlewares=[middleware_factory])
    collect_handler = partial(collect,
                              collection=collection)
    search_handler = partial(search,
                             collection=collection)
    app.router.add_post('/collect', collect_handler)
    app.router.add_get('/search', search_handler)
    return app
