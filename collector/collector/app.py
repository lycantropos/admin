import logging
from asyncio import AbstractEventLoop

from aiohttp.web import Application

from .handlers import collect
from .middlewares import middleware_factory

logger = logging.getLogger(__name__)


def create_app(loop: AbstractEventLoop) -> Application:
    app = Application(logger=logger,
                      loop=loop,
                      middlewares=[middleware_factory])
    app.router.add_post('/collect', collect)
    return app
