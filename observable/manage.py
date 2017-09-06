#!/usr/bin/env python3.6
import logging.config
import logging.handlers
import os
import sys
from asyncio import (get_event_loop,
                     ensure_future)
from typing import (Dict,
                    Set)

import click
from aiohttp import ClientSession
from aiohttp.web import run_app

from observable.app import create_app
from observable.config import PACKAGE_NAME
from observable.services import (scanner,
                                 notifier)


@click.group()
@click.option('--verbose', '-v',
              is_flag=True,
              help='Set logging level to DEBUG.')
@click.pass_context
def main(ctx: click.Context,
         verbose: bool) -> None:
    instance_name = os.environ['Observable.Name']
    set_logging(instance_name=instance_name,
                verbose=verbose)

    host = os.environ['Observable.Host']
    port = int(os.environ['Observable.Port'])
    ctx.obj = {'host': host,
               'port': port,
               'name': instance_name}


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
@click.pass_context
def run(ctx: click.Context) -> None:
    host = ctx.obj['host']
    port = ctx.obj['port']
    name = ctx.obj['name']

    loop = get_event_loop()
    subscriptions = dict()
    session = ClientSession(loop=loop)
    app = create_app(loop,
                     subscriptions=subscriptions,
                     session=session)
    ensure_future(scan_and_notify(subscriptions,
                                  name=name,
                                  delay=2,
                                  session=session),
                  loop=loop)
    run_app(app,
            host=host,
            port=port,
            print=logging.info,
            loop=loop)


async def scan_and_notify(subscriptions: Dict[str, Set[str]],
                          *,
                          name: str,
                          delay: int,
                          session: ClientSession):
    async for directory_path, diff in scanner.run_periodically(subscriptions,
                                                               delay=delay):
        subscribers = subscriptions[directory_path]
        json_data = {'diff': diff,
                     'name': name}
        await notifier.run(subscribers=subscribers,
                           json_data=json_data,
                           session=session)


if __name__ == '__main__':
    main()
