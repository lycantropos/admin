#!/usr/bin/env python3.6
import logging.config
import os
import sys
from asyncio import (get_event_loop,
                     ensure_future,
                     gather)
from functools import partial
from typing import List, Tuple, Dict
from urllib import parse

import click
from aiohttp import ClientSession
from aiohttp.web import run_app

from collector.app import create_app
from collector.config import PACKAGE_NAME
from collector.services.observer import subscribe
from collector.utils import check_connection


@click.group()
@click.option('--verbose', '-v',
              is_flag=True,
              help='Set logging level to DEBUG.')
@click.pass_context
def main(ctx: click.Context,
         verbose: bool) -> None:
    instance_name = os.environ['Collector.Name']
    set_logging(instance_name=instance_name,
                verbose=verbose)

    host = os.environ['Collector.Host']
    port = int(os.environ['Collector.Port'])
    ctx.obj = {'host': host,
               'port': port}


def set_logging(
        *,
        instance_name: str,
        package_name: str = PACKAGE_NAME,
        log_file_extension: str = 'log',
        verbose: bool) -> None:
    logs_file_name = instance_name + os.extsep + log_file_extension
    configurator = dict_configurator(logs_file_name)
    configurator.configure()

    if not verbose:
        logging.getLogger(package_name).setLevel(logging.INFO)


def dict_configurator(logs_file_name: str,
                      version: int = 1) -> logging.config.DictConfigurator:
    file_config = {'format': '[%(levelname)-8s %(asctime)s - %(name)s] '
                             '%(message)s'}
    console_formatter_config = {'format': '[%(levelname)-8s %(name)s] %(msg)s'}
    formatters = {'console': console_formatter_config,
                  'file': file_config}

    console_handler_config = {'class': 'logging.StreamHandler',
                              'level': logging.DEBUG,
                              'formatter': 'console',
                              'stream': sys.stdout}
    file_handler_config = {'class': 'logging.FileHandler',
                           'level': logging.DEBUG,
                           'formatter': 'file',
                           'filename': logs_file_name}
    handlers = {'console': console_handler_config,
                'file': file_handler_config}

    loggers = {None: {'level': logging.DEBUG,
                      'handlers': ('console', 'file'),
                      'qualname': PACKAGE_NAME}}
    config = dict(formatters=formatters,
                  handlers=handlers,
                  loggers=loggers,
                  version=version)
    return logging.config.DictConfigurator(config)


@main.command()
@click.argument('urls', nargs=-1)
@click.pass_context
def run(ctx: click.Context,
        urls: List[str]) -> None:
    host = ctx.obj['host']
    port = ctx.obj['port']
    channels = dict(map(split_query_params, urls))

    loop = get_event_loop()
    session = ClientSession(loop=loop)

    tasks = [ensure_future(check_connection(channel,
                                            session=session,
                                            method=partial(ClientSession.post,
                                                           json={})))
             for channel in channels]
    loop.run_until_complete(gather(*tasks))

    subscriber = f'http://{host}:{port}/collect'
    tasks = [ensure_future(subscribe(channel=channel,
                                     subscription={**query_params,
                                                   'subscriber': subscriber},
                                     session=session))
             for channel, query_params in channels.items()]
    loop.run_until_complete(gather(*tasks))

    app = create_app(loop)
    run_app(app,
            host=host,
            port=port,
            print=logging.info,
            loop=loop)


def split_query_params(url: str) -> Tuple[str, Dict[str, str]]:
    url_parts = list(parse.urlparse(url))
    query = dict(parse.parse_qsl(url_parts[4]))
    url_parts[4] = {}
    return parse.urlunparse(url_parts), query


if __name__ == '__main__':
    main()
