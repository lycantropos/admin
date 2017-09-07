from typing import Iterable

from pymongo.collection import Collection

from collector.types import DocumentType


def save(*documents: Iterable[DocumentType],
         collection: Collection) -> None:
    collection.insert_many(documents)
