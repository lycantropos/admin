#!/usr/bin/env python3.6
import logging.config
import os
import sys
from asyncio import (get_event_loop,
                     ensure_future,
                     gather)
from functools import partial
from typing import (Dict,
                    Tuple,
                    List)
from urllib import parse

import click
import pymongo.errors
import time
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
    db_uri = os.getenv('Collector.Mongo.URI')

    ctx.obj = {'host': host,
               'port': port,
               'db_uri': db_uri}


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
    db_uri = ctx.obj['db_uri']
    channels = dict(map(split_query_params, urls))

    check_mongo_connection(db_uri)

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

    collection_name = 'collected'
    client = pymongo.MongoClient(db_uri)
    database = client.get_database()
    collection = database.get_collection(collection_name)
    app = create_app(collection=collection,
                     loop=loop)
    run_app(app,
            host=host,
            port=port,
            print=logging.info,
            loop=loop)


def check_mongo_connection(db_uri: str,
                           *,
                           retry_attempts: int = 10,
                           retry_interval: int = 2,
                           exceptions=(pymongo.errors.PyMongoError,)) -> None:
    client = pymongo.MongoClient(db_uri)
    logging.info('Establishing connection '
                 f'with "{db_uri}".')
    for attempt_num in range(retry_attempts):
        try:
            response = client.db_name.command('ping')
            if 'ok' not in response:
                continue
            break
        except exceptions:
            err_msg = ('Connection attempt '
                       f'#{attempt_num + 1} failed.')
            logging.error(err_msg)
            time.sleep(retry_interval)
    else:
        err_message = ('Failed to establish connection '
                       f'with "{db_uri}" '
                       f'after {retry_attempts} attempts '
                       f'with {retry_interval} s. interval.')
        raise ConnectionError(err_message)
    logging.info(f'Connection established with "{db_uri}".')


def split_query_params(url: str) -> Tuple[str, Dict[str, str]]:
    url_parts = list(parse.urlparse(url))
    query = dict(parse.parse_qsl(url_parts[4]))
    url_parts[4] = {}
    return parse.urlunparse(url_parts), query


if __name__ == '__main__':
    main()
