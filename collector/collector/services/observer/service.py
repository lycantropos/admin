import logging
from typing import Dict

from aiohttp import ClientSession


async def subscribe(*,
                    channel: str,
                    subscription: Dict[str, str],
                    session: ClientSession) -> None:
    async with session.post(channel,
                            params=subscription) as response:
        response_json = await response.json()
        if response_json['status'] == 'ok':
            logging.info(f'Successfully subscribed "{subscription}" '
                         f'to a channel "{channel}".')
            return
