import copy
from typing import Dict

from collector.types import (SerializableType,
                             DocumentType)
from .utils import current_time_in_seconds

DOT_ESCAPE = '__DOT__'


def escape_dots(source: SerializableType) -> SerializableType:
    if not isinstance(source, dict):
        return source
    return {key.replace('.', DOT_ESCAPE): escape_dots(value)
            for key, value in source.items()}


def unescape_dots(source: SerializableType) -> SerializableType:
    if not isinstance(source, dict):
        return source
    return {key.replace(DOT_ESCAPE, '.'): unescape_dots(value)
            for key, value in source.items()}


def to_serializable(document: DocumentType
                    ) -> Dict[str, SerializableType]:
    result = copy.deepcopy(document)
    result.pop('_id')
    return result


def normalize(document: DocumentType) -> DocumentType:
    result = copy.deepcopy(document)
    result['timestamp'] = current_time_in_seconds()
    return result
